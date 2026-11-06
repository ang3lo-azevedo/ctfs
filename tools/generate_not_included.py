"""Write a NOT_INCLUDED.md in every folder whose large files or artifact folders are left out by .gitignore.

Only entries ignored by the artifact sections of .gitignore are listed, so build junk, secrets and
private material stay unmentioned. Prints the NOT_INCLUDED.md paths that were written or removed.
"""
import os
import subprocess

NOTE = "NOT_INCLUDED.md"

# .gitignore sections whose matches are large or bulky challenge content.
ARTIFACT_SECTIONS = {
    "# Common CTF artifacts to ignore",
    "# Additional ignored files",
    "# Extracted filesystems, triage collections and tool output",
    "# Files over 5 MiB (challenge handouts, images, wordlists, models)",
}
SKIP_PATTERNS = {"*.ovpn"}
SKIP_PREFIXES = ("2026/ecsc/",)


def git(*args, check=True, input=None):
    return subprocess.run(["git", *args], capture_output=True, check=check, input=input).stdout.decode()


def artifact_lines():
    lines, section = set(), None
    with open(".gitignore") as f:
        for number, line in enumerate(f, 1):
            line = line.strip()
            if line.startswith("#"):
                if not line.startswith("# ---"):
                    section = line
                continue
            if line and section in ARTIFACT_SECTIONS and line not in SKIP_PATTERNS:
                lines.add(number)
    return lines


def human(size):
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1000 or unit == "GB":
            return f"{size:.0f} {unit}" if unit == "B" else f"{size:.1f} {unit}"
        size /= 1000


def measure(path):
    if not path.endswith("/"):
        return human(os.lstat(path).st_size)
    count = total = 0
    for root, _, files in os.walk(path):
        for name in files:
            count += 1
            total += os.lstat(os.path.join(root, name)).st_size
    return f"{count} files, {human(total)}"


def main():
    os.chdir(git("rev-parse", "--show-toplevel").strip())
    wanted = artifact_lines()
    entries = [e for e in git("ls-files", "-o", "-i", "--exclude-standard", "--directory", "-z").split("\0")
               if e and not e.startswith(SKIP_PREFIXES) and "__MACOSX" not in e]
    # -n reports non-matching paths too (empty source); the exit status is 1 when any path is not ignored.
    out = git("check-ignore", "-v", "-n", "--no-index", "-z", "--stdin", check=False,
              input="\0".join(entries).encode()).split("\0")
    matched = sorted(path for source, line, _, path in zip(*[iter(out)] * 4)
                     if source == ".gitignore" and int(line) in wanted)

    # Keep the topmost matched entry of each branch: an ignored folder is listed, not its contents.
    by_folder, last_dir = {}, None
    for path in matched:
        if last_dir and path.startswith(last_dir):
            continue
        if path.endswith("/"):
            last_dir = path
        folder, name = os.path.split(path.rstrip("/"))
        by_folder.setdefault(folder, []).append(name + ("/" if path.endswith("/") else ""))

    written = set()
    for folder, names in sorted(by_folder.items()):
        rows = "\n".join(f"| `{name}` | {measure(os.path.join(folder, name))} |" for name in sorted(names))
        text = ("# Not included\n\n"
                "These files are left out of the repository because of their size or type.\n"
                "Get them from the original challenge if you want to reproduce the solve.\n\n"
                "| Path | Size |\n|---|---|\n" + rows + "\n")
        note = os.path.join(folder, NOTE)
        written.add(note)
        old = open(note).read() if os.path.exists(note) else None
        if old != text:
            with open(note, "w") as f:
                f.write(text)
            print(note)

    for note in git("ls-files", "-z", f"*{NOTE}").split("\0"):
        if note and note not in written and os.path.exists(note):
            os.remove(note)
            print(note)


if __name__ == "__main__":
    main()
