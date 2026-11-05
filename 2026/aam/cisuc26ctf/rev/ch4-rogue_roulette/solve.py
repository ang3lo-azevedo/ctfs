#!/usr/bin/env python3
"""
BETLick Entertainment - Rogue Roulette  |  CTF Solver
======================================================
Vulnerabilities exploited:
  1. Session ID printed at launch = casino_vault RNG state (fully known)
  2. Java LCG RNG: state = (0x5deece66d * state + 0xb) & 0xffffffffffff
  3. current_bet is XOR'd into new state → we can steer casino_vault
  4. Behavioral detector only watches consecutive wins (streak > 2 = ban)
  5. VIP vault requires: balance > $9,999,999,999 AND lower32(casino_vault)==0xdeadc0de

Usage:
  python3 betlick_solver.py <SESSION_ID_HEX>

  SESSION_ID_HEX is the hex value printed in the terminal when the game starts:
    [*] Session ID: 1A2B3C4D5E6F

Example:
  python3 betlick_solver.py 1A2B3C4D5E6F
"""

import sys

# ── Constants from binary ────────────────────────────────────────────────────
LCG_MUL    = 0x5deece66d
LCG_ADD    = 0xb
LCG_MASK   = 0xffffffffffff   # 48-bit mask
ROULETTE_N = 0x25             # 37 slots (0-36)
WIN_PAY    = 35               # current_bet * 0x23
VAULT_GOAL = 0xdeadc0de       # lower 32 bits of casino_vault at vault-open spin
BAL_THRESH = 0x2540be3ff      # $9,999,999,999  (need strictly MORE than this)
MAX_STREAK = 2                # win_streak > 2 → ban
INIT_BAL   = 0x64             # $100 starting balance

# ── Encrypted flag bytes (from data_4d0da0 + 0x50, length 0x1a = 26) ────────
CIPHER = bytes([
    0x28, 0x22, 0x2f, 0x29, 0x35,
    0x1b, 0x09, 0x0d, 0x02, 0x63,
    0x7e, 0x7f, 0x7b, 0x7d, 0x63,
    0x07, 0x7e, 0x7f, 0x7b, 0x7d,
    0x63, 0x07, 0x79, 0x05, 0x7f, 0x63,
])
FLAG_XOR_KEY = 0xde ^ 0x90    # (uint8_t)0xdeadc0de ^ 0x90 = 0x4e


# ── RNG helpers ──────────────────────────────────────────────────────────────
def lcg_step(state: int, bet: int) -> int:
    """One RNG tick: mirrors ProcessMathLogic / UpdateGameState."""
    return ((LCG_MUL * state + LCG_ADD) & LCG_MASK) ^ (bet & LCG_MASK)


def outcome_from_state(state: int) -> int:
    """Roulette outcome (0-36) from casino_vault state."""
    return (state >> 16) % ROULETTE_N


def predict_outcome(state: int, bet: int) -> tuple[int, int]:
    """Returns (new_state, outcome) for a given bet."""
    new_state = lcg_step(state, bet)
    return new_state, outcome_from_state(new_state)


# ── Static flag decryption ───────────────────────────────────────────────────
def decrypt_flag() -> str:
    return bytes(b ^ FLAG_XOR_KEY for b in CIPHER).rstrip(b'\x00').decode('ascii', errors='?')


# ── Core exploit strategy ────────────────────────────────────────────────────
def find_bet_for_target_lower32(vault_before: int, target_lower32: int) -> int | None:
    """
    Find a bet value such that:
      lower32( LCG(vault_before) ^ bet ) == target_lower32

    From:  new_vault = LCG(vault_before) ^ bet
    =>     bet = LCG(vault_before) ^ target_lower32  (only lower 32 bits matter)
    =>     bet_lower32 = (LCG_raw >> 0) & 0xffffffff ^ target_lower32
    The upper 16 bits of bet can be 0 (bet is a dollar amount, kept small).
    """
    lcg_raw = (LCG_MUL * vault_before + LCG_ADD) & LCG_MASK
    # We want lower32(lcg_raw ^ bet) == target_lower32
    bet_lower32 = (lcg_raw ^ target_lower32) & 0xffffffff
    # Upper 16 bits of vault come from lcg_raw >> 32; bet contributes nothing there
    # So check that the outcome/upper bits aren't polluted by a weird bet:
    # bet must be a positive integer (dollar amount).  We zero the upper bits.
    if bet_lower32 == 0:
        bet_lower32 = 1        # minimum non-zero bet
    return bet_lower32


def plan_winning_sequence(init_vault: int) -> list[dict]:
    """
    Simulate the game and build a move list that:
      - Never wins 3 in a row (streak kept ≤ 2)
      - Accumulates balance past $9,999,999,999
      - On the balance-crossing spin, arranges casino_vault lower32 == 0xdeadc0de

    Strategy:
      Win two straight → deliberately lose one → repeat.
      We predict every outcome ahead of time; we always know the winning number.
      When we're close to the balance threshold, plan the magic spin.
    """
    vault    = init_vault
    balance  = INIT_BAL
    streak   = 0
    moves    = []
    spin_no  = 0

    print(f"[*] Initial casino_vault : {vault:#014x}")
    print(f"[*] Starting balance     : ${balance}")
    print(f"[*] Target balance       : ${BAL_THRESH + 1:,}")
    print(f"[*] Static flag (XOR 0x{FLAG_XOR_KEY:02x}): {decrypt_flag()}\n")

    while True:
        spin_no += 1
        # Current bet: wager the maximum safe amount (all-in when approaching target)
        bet = min(balance, max(10, balance // 4))

        # --- Check if this could be the magic vault spin ---
        # Condition: win this spin AND balance + bet*35 > THRESH
        #            AND lower32(new_vault) == VAULT_GOAL
        projected_balance_after_win = balance + bet * WIN_PAY
        if projected_balance_after_win > BAL_THRESH and streak < MAX_STREAK:
            # Find the bet that steers vault lower32 to 0xdeadc0de
            magic_bet = find_bet_for_target_lower32(vault, VAULT_GOAL)
            # Clamp to available balance
            if magic_bet <= balance:
                new_vault, result = predict_outcome(vault, magic_bet)
                # We can bet on ANY number and still predict; we always guess result.
                # But we need to WIN this spin. Since we set the bet to control vault,
                # the outcome is also controlled — we just guess whatever it lands on.
                guess = result
                moves.append({
                    "spin": spin_no, "action": "BET_MAGIC",
                    "bet": magic_bet, "guess": guess,
                    "vault_after": new_vault,
                    "lower32": new_vault & 0xffffffff,
                    "balance_after": balance + magic_bet * WIN_PAY,
                    "note": "🔓 VAULT SPIN — lower32 == 0xdeadc0de guaranteed"
                })
                print(f"[+] Vault spin found at spin #{spin_no}")
                print(f"    Bet  : ${magic_bet:,}")
                print(f"    Guess: {guess}  (wheel lands here)")
                print(f"    Vault lower32 after: {new_vault & 0xffffffff:#010x}  "
                      f"{'✓ MATCH' if (new_vault & 0xffffffff) == VAULT_GOAL else '✗'}")
                print(f"    Balance after win: ${balance + magic_bet * WIN_PAY:,}\n")
                break

        # --- Normal spin: predict and bet safely ---
        # Always bet on the next winning number (we know it)
        new_vault, result = predict_outcome(vault, bet)
        guess = result

        # Enforce streak limit: if we've won twice already, deliberately lose
        if streak >= MAX_STREAK:
            # Choose a bet where we LOSE (guess a number we know won't come up)
            wrong_guess = (guess + 1) % ROULETTE_N
            moves.append({
                "spin": spin_no, "action": "DELIBERATE_LOSS",
                "bet": bet, "guess": wrong_guess,
                "vault_after": new_vault,
                "balance_after": balance - bet,
                "note": f"🛡  Safety loss (streak was {streak})"
            })
            balance -= bet
            streak = 0
        else:
            moves.append({
                "spin": spin_no, "action": "WIN",
                "bet": bet, "guess": guess,
                "vault_after": new_vault,
                "balance_after": balance + bet * WIN_PAY,
                "note": f"💰 Win #{streak + 1}"
            })
            balance += bet * WIN_PAY
            streak += 1

        vault = new_vault

        if balance <= 0:
            print("[!] Went broke — re-run with a different initial bet sizing.")
            break
        if spin_no > 5000:
            print("[!] Could not find vault spin in 5000 rounds. Try a different session.")
            break

    return moves


# ── Output helpers ────────────────────────────────────────────────────────────
def print_moves(moves: list[dict], verbose: bool = False):
    print("=" * 70)
    print("  MOVE SEQUENCE")
    print("=" * 70)
    for m in moves:
        tag = {"WIN": "✅", "DELIBERATE_LOSS": "🔴", "BET_MAGIC": "🏆"}.get(m["action"], "?")
        if m["action"] == "BET_MAGIC" or verbose:
            print(f"  Spin {m['spin']:>4}  {tag}  bet=${m['bet']:>12,}  "
                  f"guess={m['guess']:>2}  bal=${m['balance_after']:>15,}  {m['note']}")
        elif m["spin"] % 50 == 0:
            print(f"  Spin {m['spin']:>4}  ...  bal=${m['balance_after']:>15,}")
    print("=" * 70)
    print(f"\n  Total spins needed: {len(moves)}")
    print(f"  Final balance     : ${moves[-1]['balance_after']:,}")


def print_cheat_sheet(moves: list[dict]):
    """Print only the moves the player actually needs to type."""
    print("\n" + "=" * 70)
    print("  CHEAT SHEET  (copy these bets + guesses into the game)")
    print("=" * 70)
    for m in moves:
        action_str = f"bet ${m['bet']:,}  →  guess {m['guess']}"
        tag = {"WIN": "[WIN ]", "DELIBERATE_LOSS": "[LOSE]", "BET_MAGIC": "[VAULT]"}.get(m["action"])
        print(f"  Spin {m['spin']:>4}  {tag}  {action_str}")
    print("=" * 70)


# ── Entry point ───────────────────────────────────────────────────────────────
def main():
    if len(sys.argv) < 2:
        print(__doc__)
        # Demo: run with a synthetic vault value if no arg given
        import time, ctypes
        # Mimic: casino_vault = (time() * 0x1337) ^ &casino_vault_approx) & mask
        t = int(time.time())
        demo_vault = ((t * 0x1337) ^ 0x4f1978) & LCG_MASK
        print(f"[*] No Session ID supplied — running demo with vault={demo_vault:#014x}")
        session_id = demo_vault
    else:
        try:
            session_id = int(sys.argv[1], 16)
        except ValueError:
            print(f"[!] Invalid hex: {sys.argv[1]}")
            sys.exit(1)

    # Static flag (works regardless of session)
    print("\n── STATIC FLAG DECRYPTION ──────────────────────────────────────────")
    flag = decrypt_flag()
    print(f"   Cipher  : {CIPHER.hex()}")
    print(f"   XOR key : 0x{FLAG_XOR_KEY:02x}  (= 0xde ^ 0x90, where 0xde = low byte of 0xdeadc0de)")
    print(f"   FLAG    : {flag}")
    print()

    # Plan the exploit
    print("── EXPLOIT PLANNER ─────────────────────────────────────────────────")
    moves = plan_winning_sequence(session_id)

    # Summary
    print_moves(moves, verbose=False)
    print_cheat_sheet(moves)

    print("""
── HOW IT WORKS ────────────────────────────────────────────────────────
  1. RNG seed leak:  casino_vault is printed as "[*] Session ID: ..."
  2. LCG prediction: outcome = ((0x5deece66d*vault+0xb)&0xffffffffffff) ^ bet) >> 16) % 37
  3. Bet steering:   by choosing 'bet', we control lower32(new_vault)
  4. Streak bypass:  deliberately lose every 3rd spin to reset win_streak
  5. Vault trigger:  one final spin where bet is chosen so that:
       lower32(new_vault) == 0xdeadc0de  AND  we win  AND  balance tips over $9.999B
  6. Flag decrypt:   cipher[i] ^ 0xde ^ 0x90  (key = low byte of magic constant)
────────────────────────────────────────────────────────────────────────
""")


if __name__ == "__main__":
    main()