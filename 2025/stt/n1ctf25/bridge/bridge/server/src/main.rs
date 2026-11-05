use solana_sdk::{
    account::Account, compute_budget::ComputeBudgetInstruction, instruction::Instruction, pubkey::Pubkey, signature::{Keypair, Signer}, transaction::Transaction
};

use anchor_lang::{InstructionData, ToAccountMetas, system_program};

use anchor_client::{handle_program_log, handle_system_log, Execution};
use regex::Regex;

use sol_ctf_framework::ChallengeBuilder;

use std::{
    env,
    error::Error,
    io::Write,
    net::{TcpListener, TcpStream},
};

#[tokio::main]
async fn main() -> Result<(), Box<dyn Error>> {
    let listener = TcpListener::bind("0.0.0.0:1337")?;

    println!("Server listening on port 1337");

    for stream in listener.incoming() {
        let mut stream = stream.unwrap();

        tokio::spawn(async move {
            if let Err(err) = handle_connection(&mut stream).await {
                writeln!(stream, "error: {:?}", err).ok();
            }
        });
    }
    Ok(())
}

async fn handle_connection(socket: &mut TcpStream) -> Result<(), Box<dyn Error>> {
    let mut builder = ChallengeBuilder::try_from(socket.try_clone()?)?;

    let solve_id = match builder.input_program() {
        Ok(pubkey) => pubkey,
        Err(e) => {
            writeln!(socket, "Error: cannot load player program -> {e}")?;
            return Ok(());
        }
    };
    let chall_id = builder
        .add_program("./challenge.so", Some(challenge::id()))
        .expect("Duplicate pubkey supplied");

    writeln!(socket, "Bridge: {}", chall_id)?;
    writeln!(socket, "Exploit: {}", solve_id)?;


    let admin_keypair = Keypair::new();
    let admin = admin_keypair.pubkey();
    builder.builder.add_account(
        admin,
        Account::new(1_000_000_000, 0, &system_program::ID),
    );

    let config = Pubkey::find_program_address(&[b"config"], &chall_id).0;
    let wsol_mint = Pubkey::from_str_const("So11111111111111111111111111111111111111112");
    let mint_config = Pubkey::find_program_address(&[b"mint-config", &wsol_mint.to_bytes()], &chall_id).0;

    let player = Keypair::new();
    builder.builder.add_account(
        player.pubkey(),
        Account::new(1_000_000_000, 0, &system_program::ID),
    );

    writeln!(socket, "Player: {}", player.pubkey())?;
    writeln!(socket, "")?;

    let mut chall = builder.build().await;

    {
        let ix = challenge::instruction::Initialize {
            admin,
            fee_bps: 10
        };
        let ix_accounts = challenge::accounts::Initialize {
            payer: admin,
            config,
            system_program: system_program::ID,
        };

        chall.run_ixs_full(
            &[Instruction::new_with_bytes(
                chall_id, 
                &ix.data(),
                ix_accounts.to_account_metas(None),
            )],
            &[&admin_keypair],
            &admin,
        ).await?;
    }

    {
        let ix = challenge::instruction::RegisterMint {
            remote_token: [0; 32],
            remote_chain: 42,
            max_bridge_amount: 1_000_000_000_000,
        };
        let ix_accounts = challenge::accounts::RegisterMint {
            admin,
            config,
            mint: wsol_mint,
            mint_config,
            system_program: system_program::ID,
        };

        chall.run_ixs_full(
            &[Instruction::new_with_bytes(
                chall_id, 
                &ix.data(),
                ix_accounts.to_account_metas(None),
            )],
            &[&admin_keypair],
            &admin,
        ).await?;
    }

    let solve_ix = chall.read_instruction(solve_id)?;

    let bridge_ix = chall.read_instruction(chall_id)?;

    let bump_budget = ComputeBudgetInstruction::set_compute_unit_limit(10_000_000);

    let mut tx = Transaction::new_with_payer(&[bump_budget, solve_ix, bridge_ix], Some(&player.pubkey()));

    tx.sign(&[&player], chall.ctx.last_blockhash);

    let logs = chall
        .ctx
        .banks_client
        .process_transaction_with_metadata(tx)
        .await?
        .metadata
        .expect("Error running exploit")
        .log_messages;

    let program_id_string = chall_id.to_string();
    let program_id_str = program_id_string.as_str();

    let events = parse_logs_response::<challenge::BridgeEvent>(logs, program_id_str);

    for event in events {
        if event.user == player.pubkey()
            && event.mint == wsol_mint
            && event.amount > 1_000_000_000_000
            && event.target_chain == 42
        {
            writeln!(socket, "Thank you for using our bridge! You are our first customer to bridge such a large amount of wSOL. Here is a gift for you:")?;
            if let Ok(flag) = env::var("FLAG") {
                writeln!(socket, "flag: {:?}", flag)?;
            } else {
                writeln!(socket, "flag not found, please contact admin")?;
            }
            return Ok(());
        }
    }

    writeln!(socket, "Thank you for using our bridge! See you next time!")?;

    Ok(())
}

// https://github.com/solana-foundation/anchor/blob/v0.31.1/client/src/lib.rs#L672
fn parse_logs_response<T: anchor_lang::Event + anchor_lang::AnchorDeserialize>(
    logs: Vec<String>,
    program_id_str: &str,
) -> Vec<T> {
    let mut events: Vec<T> = Vec::new();
    if !logs.is_empty() {
        if let Ok(mut execution) = Execution::new(&mut logs.as_slice()) {
            // Create a new peekable iterator so that we can peek at the next log whilst iterating
            let mut logs_iter = logs.iter().peekable();
            let regex = Regex::new(r"^Program (.*) invoke.*$").unwrap();

            while let Some(l) = logs_iter.next() {
                // Parse the log.
                let (event, new_program, did_pop) = {
                    if program_id_str == execution.program() {
                        handle_program_log(program_id_str, l).unwrap()
                    } else {
                        let (program, did_pop) = handle_system_log(program_id_str, l);
                        (None, program, did_pop)
                    }
                };
                // Emit the event.
                if let Some(e) = event {
                    events.push(e);
                }
                // Switch program context on CPI.
                if let Some(new_program) = new_program {
                    execution.push(new_program);
                }
                // Program returned.
                if did_pop {
                    execution.pop();

                    // If the current iteration popped then it means there was a
                    //`Program x success` log. If the next log in the iteration is
                    // of depth [1] then we're not within a CPI and this is a new instruction.
                    //
                    // We need to ensure that the `Execution` instance is updated with
                    // the next program ID, or else `execution.program()` will cause
                    // a panic during the next iteration.
                    if let Some(&next_log) = logs_iter.peek() {
                        if next_log.ends_with("invoke [1]") {
                            let next_instruction =
                                regex.captures(next_log).unwrap().get(1).unwrap().as_str();
                            // Within this if block, there will always be a regex match.
                            // Therefore it's safe to unwrap and the captured program ID
                            // at index 1 can also be safely unwrapped.
                            execution.push(next_instruction.to_string());
                        }
                    };
                }
            }
        }
    }
    events
}