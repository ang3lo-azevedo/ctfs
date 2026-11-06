import os
import subprocess


def listed_dirs(startpath):
    """Directories containing files git would publish (tracked or untracked but not ignored)."""
    out = subprocess.run(["git", "-C", startpath, "ls-files", "-co", "--exclude-standard", "-z"],
                         capture_output=True, check=True).stdout.decode()
    dirs = set()
    for path in filter(None, out.split("\0")):
        parts = path.split("/")[:-1]
        for i in range(1, len(parts) + 1):
            dirs.add("/".join(parts[:i]))
    return dirs


def generate_markdown_tree(startpath):
    markdown = """# Cybersecurity CTFs

Write-ups and solve scripts from cybersecurity competitions, organized by year, team and event.
Categories include digital forensics, reverse engineering, pwn, web and OSINT.

Large challenge artifacts (memory images, disk images, triage collections, extracted
filesystems) are not included, get them from the original event where they are still available.

Team write-ups from r4ph3cks are in the `r4ph3cks` submodule ([r4ph3cks/ctfs](https://github.com/r4ph3cks/ctfs)).

## Repository Index

"""
    
    ignore_dirs = {".git", ".githooks", "extractions", ".venv_pyzip", "__pycache__"}
    published = listed_dirs(startpath)
    real_isdir = os.path.isdir
    def isdir(path):
        return real_isdir(path) and os.path.relpath(path, startpath) in published
    os.path.isdir = isdir
    
    # First, parse the years (directories that are numbers like 2025, 2026)
    years = [d for d in os.listdir(startpath) if os.path.isdir(os.path.join(startpath, d)) and d.isdigit()]
    years.sort()
    
    for year in years:
        markdown += f"## {year}\n\n"
        year_path = os.path.join(startpath, year)
        teams = [d for d in os.listdir(year_path) if os.path.isdir(os.path.join(year_path, d)) and d not in ignore_dirs]
        teams.sort()
        
        for team in teams:
            markdown += f"### `{team}`\n"
            team_path = os.path.join(year_path, team)
            challenges = [d for d in os.listdir(team_path) if os.path.isdir(os.path.join(team_path, d)) and d not in ignore_dirs]
            challenges.sort()
            for chal in challenges:
                markdown += f"- `{chal}`\n"
            markdown += "\n"
        markdown += "---\n\n"
        
    return markdown

if __name__ == "__main__":
    # Get the repo root (one folder above the 'tools' directory)
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    readme_path = os.path.join(repo_root, "README.md")
    
    with open(readme_path, "w") as f:
        f.write(generate_markdown_tree(repo_root))
