use anchor_lang::prelude::*;
use anchor_spl::{
    associated_token::AssociatedToken,
    token_2022::spl_token_2022,
    token_interface::{Mint, TokenAccount, TokenInterface},
};

declare_id!("8PUGbrjqpxUMsxsra9iz8Dt25Qvp7Wvct1NK4kJB2EL3");

const MAX_BASIS_POINTS: u16 = 10_000;

#[program]
pub mod challenge {
    use super::*;

    pub fn initialize<'info>(
        ctx: Context<'_, '_, '_, 'info, Initialize<'info>>,
        admin: Pubkey,
        fee_bps: u16,
    ) -> Result<()> {
        require!(fee_bps <= MAX_BASIS_POINTS, BridgeError::InvalidFee);

        let config = &mut ctx.accounts.config;
        config.admin = admin;
        config.fee_bps = fee_bps;
        config.paused = false;
        let (_, bump) = Pubkey::find_program_address(&[b"config"], &crate::ID);
        config.bump = bump;
        Ok(())
    }

    pub fn set_fee(ctx: Context<SetFee>, new_fee_bps: u16) -> Result<()> {
        require!(new_fee_bps <= MAX_BASIS_POINTS, BridgeError::InvalidFee);

        ctx.accounts.config.fee_bps = new_fee_bps;
        Ok(())
    }

    pub fn set_pause_state(ctx: Context<SetPauseState>, paused: bool) -> Result<()> {
        ctx.accounts.config.paused = paused;
        Ok(())
    }

    pub fn register_mint<'info>(
        ctx: Context<'_, '_, '_, 'info, RegisterMint<'info>>,
        remote_token: [u8; 32],
        remote_chain: u16,
        max_bridge_amount: u64,
    ) -> Result<()> {
        let mint_config = &mut ctx.accounts.mint_config;
        mint_config.mint = ctx.accounts.mint.key();
        mint_config.remote_token = remote_token;
        mint_config.remote_chain = remote_chain;
        mint_config.max_bridge_amount = max_bridge_amount;
        mint_config.enabled = true;
        mint_config.bump = ctx.bumps.mint_config;

        emit!(MintRegisteredEvent {
            admin: ctx.accounts.admin.key(),
            mint: ctx.accounts.mint.key(),
            remote_chain,
            remote_token,
        });

        Ok(())
    }

    pub fn update_mint_config<'info>(
        ctx: Context<'_, '_, '_, 'info, UpdateMintConfig<'info>>,
        remote_token: [u8; 32],
        remote_chain: u16,
        max_bridge_amount: u64,
        enabled: bool,
    ) -> Result<()> {
        let mint_config = &mut ctx.accounts.mint_config;
        mint_config.remote_token = remote_token;
        mint_config.remote_chain = remote_chain;
        mint_config.max_bridge_amount = max_bridge_amount;
        mint_config.enabled = enabled;

        emit!(MintConfigUpdatedEvent {
            admin: ctx.accounts.admin.key(),
            mint: ctx.accounts.mint.key(),
            remote_chain,
            remote_token,
            enabled,
            max_bridge_amount,
        });

        Ok(())
    }

    pub fn bridge<'info>(
        ctx: Context<'_, '_, '_, 'info, Bridge<'info>>,
        amount: u64,
        target_chain: u8,
        dest: Pubkey,
    ) -> Result<()> {
        require!(amount > 0, BridgeError::InvalidAmount);
        require!(!ctx.accounts.config.paused, BridgeError::BridgePaused);

        let mint_config = &ctx.accounts.mint_config;
        require!(mint_config.enabled, BridgeError::MintNotEnabled);
        require!(
            amount <= mint_config.max_bridge_amount,
            BridgeError::InvalidAmount
        );

        let fee = compute_fee(amount, ctx.accounts.config.fee_bps)?;
        let net_amount = amount.checked_sub(fee).ok_or(BridgeError::MathOverflow)?;

        if net_amount > 0 {
            spl_token_2022::onchain::invoke_transfer_checked(
                &ctx.accounts.token_program.key(),
                ctx.accounts.user_ata.to_account_info(),
                ctx.accounts.mint.to_account_info(),
                ctx.accounts.escrow_ata.to_account_info(),
                ctx.accounts.user.to_account_info(),
                &ctx.remaining_accounts,
                net_amount,
                ctx.accounts.mint.decimals,
                &[],
            )?;
        }

        if fee > 0 {
            spl_token_2022::onchain::invoke_transfer_checked(
                &ctx.accounts.token_program.key(),
                ctx.accounts.user_ata.to_account_info(),
                ctx.accounts.mint.to_account_info(),
                ctx.accounts.fee_vault.to_account_info(),
                ctx.accounts.user.to_account_info(),
                &ctx.remaining_accounts,
                fee,
                ctx.accounts.mint.decimals,
                &[],
            )?;
        }

        emit!(BridgeEvent {
            user: ctx.accounts.user.key(),
            mint: ctx.accounts.mint.key(),
            amount: net_amount,
            dest,
            target_chain,
        });

        Ok(())
    }

    pub fn release<'info>(
        ctx: Context<'_, '_, '_, 'info, Release<'info>>,
        amount: u64,
        source_chain: u16,
        remote_sender: [u8; 32],
    ) -> Result<()> {
        require!(amount > 0, BridgeError::InvalidAmount);
        let mint_config = &ctx.accounts.mint_config;
        require!(mint_config.enabled, BridgeError::MintNotEnabled);
        require_eq!(
            mint_config.remote_chain,
            source_chain,
            BridgeError::ChainMismatch
        );
        require!(
            ctx.accounts.escrow_ata.amount >= amount,
            BridgeError::InsufficientLiquidity
        );

        let (_, escrow_bump) = Pubkey::find_program_address(&[b"escrow"], &crate::ID);
        let escrow_bump_seed = [escrow_bump];
        let escrow_seeds: &[&[u8]] = &[b"escrow", &escrow_bump_seed];
        let signer_seeds: &[&[&[u8]]] = &[escrow_seeds];

        spl_token_2022::onchain::invoke_transfer_checked(
            &ctx.accounts.token_program.key(),
            ctx.accounts.escrow_ata.to_account_info(),
            ctx.accounts.mint.to_account_info(),
            ctx.accounts.recipient_ata.to_account_info(),
            ctx.accounts.escrow.clone(),
            &ctx.remaining_accounts,
            amount,
            ctx.accounts.mint.decimals,
            signer_seeds,
        )?;

        emit!(ReleaseEvent {
            admin: ctx.accounts.admin.key(),
            recipient: ctx.accounts.recipient.key(),
            mint: ctx.accounts.mint.key(),
            amount,
            source_chain,
            remote_sender,
        });

        Ok(())
    }

    pub fn withdraw_fees<'info>(
        ctx: Context<'_, '_, '_, 'info, WithdrawFees<'info>>,
        amount: u64,
    ) -> Result<()> {
        require!(amount > 0, BridgeError::InvalidAmount);
        require!(
            ctx.accounts.fee_vault.amount >= amount,
            BridgeError::InsufficientLiquidity
        );

        let (_, config_bump) = Pubkey::find_program_address(&[b"config"], &crate::ID);
        let config_bump_seed = [config_bump];
        let config_seeds: &[&[u8]] = &[b"config", &config_bump_seed];
        let signer_seeds: &[&[&[u8]]] = &[config_seeds];

        spl_token_2022::onchain::invoke_transfer_checked(
            &ctx.accounts.token_program.key(),
            ctx.accounts.fee_vault.to_account_info(),
            ctx.accounts.mint.to_account_info(),
            ctx.accounts.admin_fee_ata.to_account_info(),
            ctx.accounts.config.to_account_info(),
            &ctx.remaining_accounts,
            amount,
            ctx.accounts.mint.decimals,
            signer_seeds,
        )?;

        Ok(())
    }
}

#[derive(Accounts)]
pub struct Initialize<'info> {
    #[account(mut)]
    pub payer: Signer<'info>,
    #[account(
        init,
        payer = payer,
        space = 8 + BridgeConfig::INIT_SPACE,
        seeds = [b"config"],
        bump,
    )]
    pub config: Account<'info, BridgeConfig>,
    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
pub struct SetFee<'info> {
    pub admin: Signer<'info>,
    #[account(
        mut,
        seeds = [b"config"],
        bump,
        has_one = admin @ BridgeError::Unauthorized,
    )]
    pub config: Account<'info, BridgeConfig>,
}

#[derive(Accounts)]
#[instruction(paused: bool)]
pub struct SetPauseState<'info> {
    pub admin: Signer<'info>,
    #[account(
        mut,
        seeds = [b"config"],
        bump,
        has_one = admin @ BridgeError::Unauthorized,
        constraint = paused != config.paused @ BridgeError::InvalidPauseState,
    )]
    pub config: Account<'info, BridgeConfig>,
}

#[derive(Accounts)]
pub struct RegisterMint<'info> {
    #[account(mut)]
    pub admin: Signer<'info>,
    #[account(
        seeds = [b"config"],
        bump,
        has_one = admin @ BridgeError::Unauthorized,
    )]
    pub config: Account<'info, BridgeConfig>,
    pub mint: InterfaceAccount<'info, Mint>,
    #[account(
        init,
        payer = admin,
        space = 8 + MintConfig::INIT_SPACE,
        seeds = [b"mint-config", mint.key().as_ref()],
        bump,
    )]
    pub mint_config: Account<'info, MintConfig>,
    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
pub struct UpdateMintConfig<'info> {
    pub admin: Signer<'info>,
    #[account(
        mut,
        seeds = [b"config"],
        bump,
        has_one = admin @ BridgeError::Unauthorized,
    )]
    pub config: Account<'info, BridgeConfig>,
    pub mint: InterfaceAccount<'info, Mint>,
    pub mint_config: Account<'info, MintConfig>,
}

#[derive(Accounts)]
pub struct Bridge<'info> {
    #[account(mut)]
    pub user: Signer<'info>,
    #[account(
        seeds = [b"config"],
        bump,
    )]
    pub config: Account<'info, BridgeConfig>,
    pub mint: InterfaceAccount<'info, Mint>,
    pub mint_config: Account<'info, MintConfig>,
    /// CHECK: Program-derived address that owns the escrow tokens
    #[account(
        seeds = [b"escrow"],
        bump,
    )]
    pub escrow: AccountInfo<'info>,
    #[account(
        mut,
        associated_token::mint = mint,
        associated_token::authority = user,
        associated_token::token_program = token_program,
    )]
    pub user_ata: InterfaceAccount<'info, TokenAccount>,
    #[account(
        init_if_needed,
        payer = user,
        associated_token::mint = mint,
        associated_token::authority = escrow,
        associated_token::token_program = token_program,
    )]
    pub escrow_ata: InterfaceAccount<'info, TokenAccount>,
    #[account(
        init_if_needed,
        payer = user,
        associated_token::mint = mint,
        associated_token::authority = config,
        associated_token::token_program = token_program,
    )]
    pub fee_vault: InterfaceAccount<'info, TokenAccount>,
    pub token_program: Interface<'info, TokenInterface>,
    pub associated_token_program: Program<'info, AssociatedToken>,
    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
pub struct Release<'info> {
    #[account(mut)]
    pub admin: Signer<'info>,
    #[account(
        seeds = [b"config"],
        bump,
        has_one = admin @ BridgeError::Unauthorized,
    )]
    pub config: Account<'info, BridgeConfig>,
    pub mint: InterfaceAccount<'info, Mint>,
    pub mint_config: Account<'info, MintConfig>,
    /// CHECK: Program-derived address that owns the escrow tokens
    #[account(
        seeds = [b"escrow"],
        bump,
    )]
    pub escrow: AccountInfo<'info>,
    #[account(
        mut,
        associated_token::mint = mint,
        associated_token::authority = escrow,
        associated_token::token_program = token_program,
    )]
    pub escrow_ata: InterfaceAccount<'info, TokenAccount>,
    pub recipient: SystemAccount<'info>,
    #[account(
        init_if_needed,
        payer = admin,
        associated_token::mint = mint,
        associated_token::authority = recipient,
        associated_token::token_program = token_program,
    )]
    pub recipient_ata: InterfaceAccount<'info, TokenAccount>,
    pub token_program: Interface<'info, TokenInterface>,
    pub associated_token_program: Program<'info, AssociatedToken>,
    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
pub struct WithdrawFees<'info> {
    #[account(mut)]
    pub admin: Signer<'info>,
    #[account(
        seeds = [b"config"],
        bump,
        has_one = admin @ BridgeError::Unauthorized,
    )]
    pub config: Account<'info, BridgeConfig>,
    pub mint: InterfaceAccount<'info, Mint>,
    #[account(
        mut,
        associated_token::mint = mint,
        associated_token::authority = config,
        associated_token::token_program = token_program,
    )]
    pub fee_vault: InterfaceAccount<'info, TokenAccount>,
    #[account(
        init_if_needed,
        payer = admin,
        associated_token::mint = mint,
        associated_token::authority = admin,
        associated_token::token_program = token_program,
    )]
    pub admin_fee_ata: InterfaceAccount<'info, TokenAccount>,
    pub token_program: Interface<'info, TokenInterface>,
    pub associated_token_program: Program<'info, AssociatedToken>,
    pub system_program: Program<'info, System>,
}

#[account]
#[derive(InitSpace)]
pub struct BridgeConfig {
    pub admin: Pubkey,
    pub fee_bps: u16,
    pub paused: bool,
    pub bump: u8,
    pub reserved: [u8; 5],
}

#[account]
#[derive(InitSpace)]
pub struct MintConfig {
    pub mint: Pubkey,
    pub remote_token: [u8; 32],
    pub remote_chain: u16,
    pub max_bridge_amount: u64,
    pub enabled: bool,
    pub bump: u8,
    pub reserved: [u8; 6],
}

#[event]
pub struct MintRegisteredEvent {
    pub admin: Pubkey,
    pub mint: Pubkey,
    pub remote_chain: u16,
    pub remote_token: [u8; 32],
}

#[event]
pub struct MintConfigUpdatedEvent {
    pub admin: Pubkey,
    pub mint: Pubkey,
    pub remote_chain: u16,
    pub remote_token: [u8; 32],
    pub enabled: bool,
    pub max_bridge_amount: u64,
}

#[event]
pub struct BridgeEvent {
    pub user: Pubkey,
    pub mint: Pubkey,
    pub amount: u64,
    pub dest: Pubkey,
    pub target_chain: u8,
}

#[event]
pub struct ReleaseEvent {
    pub admin: Pubkey,
    pub recipient: Pubkey,
    pub mint: Pubkey,
    pub amount: u64,
    pub source_chain: u16,
    pub remote_sender: [u8; 32],
}

#[error_code]
pub enum BridgeError {
    #[msg("Bridge is paused")]
    BridgePaused,
    #[msg("Fee is outside of accepted bounds")]
    InvalidFee,
    #[msg("Amount violates the configured limits")]
    InvalidAmount,
    #[msg("Invalid pause state")]
    InvalidPauseState,
    #[msg("Mint is not enabled for bridging")]
    MintNotEnabled,
    #[msg("Computation overflowed")]
    MathOverflow,
    #[msg("Insufficient liquidity in vault")]
    InsufficientLiquidity,
    #[msg("Mint does not match configuration")]
    MintMismatch,
    #[msg("Remote chain does not match configuration")]
    ChainMismatch,
    #[msg("Only the bridge admin may invoke this instruction")]
    Unauthorized,
}

fn compute_fee(amount: u64, fee_bps: u16) -> Result<u64> {
    if fee_bps == 0 {
        return Ok(0);
    }
    let numerator = amount
        .checked_mul(fee_bps as u64)
        .ok_or(BridgeError::MathOverflow)?;
    Ok(numerator / MAX_BASIS_POINTS as u64)
}
