# NixJail — Organizer Solution

**Category:** Misc / Sandbox · **Difficulty:** Medium 
**Flag:** `pottlack{n1x_ev4l_b00l_0racle_3sc4pe}`

## What the service does

Each line you send becomes a Nix expression evaluated as:

```nix
let flag = "<the real flag>"; in
let __result = ( <YOUR EXPRESSION> ); in
if builtins.isBool __result then __result
else builtins.throw "booleans only"
```

run with `nix-instantiate --eval --strict --restrict-eval --option pure-eval true
-I /srv/public`. The harness prints **only** `uwu` (true) / `ono` (false) /
`owo` (rejected) — stdout is classified, never echoed, so a trace/throw message
cannot carry flag bytes out. That one bit per query is the whole channel.

## Why there is no "real" restrict-eval escape

This was designed after confirming (on Nix 2.24/2.34) that restricted + pure
eval resists the usual tricks — all of these return *forbidden in restricted
mode*:

- `builtins.readFile "/flag.txt"`, `import "/flag.txt"`, `builtins.path {...}`
- `../` traversal and **symlinks** inside the allowed dir (paths are
  canonicalised to their realpath before the allow-check)
- `fetchTree` / `fetchGit` / `fetchurl` / `fetchTarball` of `file://` or
  `path:` (URI-gated by `allowed-uris`)
- `builtins.getEnv "FLAG"` → `""` (pure eval), and the harness scrubs `FLAG`
  from the child env anyway

So the intended path is **not** an out-of-band escape; it's an **in-band oracle
leak**, exactly the "leak the flag character-by-character" idea in the brief.

## Intended solve — boolean oracle

`builtins.stringLength`, `builtins.substring` and string ordering (`<`) are all
pure, so each query is a yes/no question about the flag:

```
nix> builtins.stringLength flag == 37          # find length (binary search)
nix> builtins.substring 0 1 flag == "p"        # true
nix> (builtins.substring 7 1 flag) < "m"       # binary-search each byte
```

Binary search → ~7 queries/char + length ≈ 260 queries for a 37-char flag.

### Reference solver

`solve.py` (in this folder, **kept out of the player zip**) automates it:

```
python3 solve.py <HOST> <PORT>
```

**Verified end to end** against the real harness: it recovers the full flag in
**~19 s** (`MATCH`). Each `nix-instantiate` eval is ~30 ms; the service caps
each evaluation at 6 CPU-seconds / 8 wall-seconds / 1.5 GB. The sandbox is
`--restrict-eval` + `pure-eval` and the harness only ever emits
`uwu`/`ono`/`owo` — never raw evaluator output — so the flag can't be
read off disk or the environment, only leaked through the boolean oracle.

## Alternative solves to accept

- Linear charset scan instead of binary search (slower, same idea).
- Using `builtins.elemAt (builtins.split ...)`, `lessThan`, `builtins.compareVersions`,
  char-code tricks via `builtins.substring` + a lookup string — all fine.

## Anti-cheese already handled

- Non-boolean results (incl. returning `flag` itself) → `rejected`, never echoed.
- `trace` / `throw` / `abort` messages go to stderr, which is **discarded**.
- Infinite recursion / memory bombs → CPU+AS rlimits + wall-clock timeout →
  `rejected`.
- Breaking out of the `let` wrapper lands you in expression position only; you
  can shadow `flag` but that only hurts you, and there's still no output channel
  beyond the boolean.

## Deploy

```sh
cd deploy
docker compose up --build -d      # rootful Docker host
nc localhost 1337
```
Build must be on a rootful host (rootless w/o /etc/subuid can't map nixbld).
