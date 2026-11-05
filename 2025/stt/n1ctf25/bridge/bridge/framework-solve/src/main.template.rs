use anchor_lang::{InstructionData, ToAccountMetas, system_program};
use solana_program::pubkey::Pubkey;
use std::net::TcpStream;
use std::{error::Error, fs, io::prelude::*, io::BufReader, str::FromStr};
use solana_sdk::instruction::AccountMeta;
use anchor_lang::Id;
use anchor_spl::associated_token::AssociatedToken;


fn get_line<R: Read>(reader: &mut BufReader<R>) -> Result<String, Box<dyn Error>> {
    let mut line = String::new();
    reader.read_line(&mut line)?;
    let ret = line
        .split(':')
        .nth(1)
        .ok_or("invalid input")?
        .trim()
        .to_string();
    Ok(ret)
}


fn main() -> Result<(), Box<dyn Error>> {
    let mut stream = TcpStream::connect("127.0.0.1:1337")?;
    let mut reader = BufReader::new(stream.try_clone().unwrap());

    let mut line = String::new();

    let so_data = fs::read("./solve/target/deploy/solve.so")?;

    reader.read_line(&mut line)?;
    writeln!(stream, "{}", solve::ID)?;
    reader.read_line(&mut line)?;
    writeln!(stream, "{}", so_data.len())?;
    stream.write_all(&so_data)?;

    let chall_id = challenge::ID;

    let chall    = Pubkey::from_str(&get_line(&mut reader)?)?;
    let solve    = Pubkey::from_str(&get_line(&mut reader)?)?;
    let user     = Pubkey::from_str(&get_line(&mut reader)?)?;
    reader.read_line(&mut line)?;

    println!("");
    println!("chall      : {}", chall);
    println!("solve      : {}", solve);
    println!("user       : {}", user);
    println!("");
    
    {
        let ix = solve::instruction::Initialize {};
        let data = ix.data();
        let ix_accounts = solve::accounts::Initialize {
            user,
            challenge: chall_id,
            system_program: system_program::id(),
        };

        let metas = ix_accounts.to_account_metas(None);

        // if you don't know what this is doing, look at server code and also sol-ctf-framework read_instruction:
        // https://github.com/otter-sec/sol-ctf-framework/blob/4a88e635fd211af7c56bba2c3184e713f497894e/src/lib.rs#L249
        reader.read_line(&mut line)?;
        writeln!(stream, "{}", metas.len())?;
        for meta in metas {
            let mut meta_str = String::new();
            meta_str.push('m');
            if meta.is_writable {
                meta_str.push('w');
            }
            if meta.is_signer {
                meta_str.push('s');
            }
            meta_str.push(' ');
            meta_str.push_str(&meta.pubkey.to_string());
            writeln!(stream, "{}", meta_str)?;
            stream.flush()?;
        }

        reader.read_line(&mut line)?;
        writeln!(stream, "{}", data.len())?;
        stream.write_all(&data)?;

        stream.flush()?;
    }

    {
        let ix = challenge::instruction::Bridge {
            amount: 1_000_000_000,
            dest: chall,
            target_chain: 42,
        };
        let data = ix.data();
        let ix_accounts = challenge::accounts::Bridge {
            user,
            config,
            mint,
            mint_config,
            escrow,
            user_ata,
            escrow_ata,
            fee_vault,
            token_program: Token2022::id(),
            associated_token_program: AssociatedToken::id(),
            system_program: system_program::ID,
        };

        let mut metas = ix_accounts.to_account_metas(None);

        // if you don't know what this is doing, look at server code and also sol-ctf-framework read_instruction:
        // https://github.com/otter-sec/sol-ctf-framework/blob/4a88e635fd211af7c56bba2c3184e713f497894e/src/lib.rs#L249
        reader.read_line(&mut line)?;
        writeln!(stream, "{}", metas.len())?;
        for meta in metas {
            let mut meta_str = String::new();
            meta_str.push('m');
            if meta.is_writable {
                meta_str.push('w');
            }
            if meta.is_signer {
                meta_str.push('s');
            }
            meta_str.push(' ');
            meta_str.push_str(&meta.pubkey.to_string());
            writeln!(stream, "{}", meta_str)?;
            stream.flush()?;
        }

        reader.read_line(&mut line)?;
        writeln!(stream, "{}", data.len())?;
        stream.write_all(&data)?;

        stream.flush()?;
    }

    line.clear();
    while reader.read_line(&mut line)? != 0 {
        print!("{}", line);
        line.clear();
    }

    Ok(())
}
