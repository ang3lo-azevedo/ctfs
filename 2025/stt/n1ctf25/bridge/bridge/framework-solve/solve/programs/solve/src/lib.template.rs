use anchor_lang::prelude::*;

declare_id!("4FYNmWbFutX4fPV9edZCJg6vNnZGva56WpKCPWWMkpuj");

#[program]
pub mod solve {
    use super::*;

    pub fn initialize(ctx: Context<Initialize>) -> Result<()> {
        // solve goes here:
        
        Ok(())
    }
}

#[derive(Accounts)]
pub struct Initialize<'info> {
    // feel free to expand/change this as needed
    // if you change this, make sure to change framework-solve/src/main.rs accordingly

    #[account(mut)]
    pub user: Signer<'info>,

    pub challenge: Program<'info, challenge::program::Challenge>,

    pub system_program: Program<'info, System>,
}