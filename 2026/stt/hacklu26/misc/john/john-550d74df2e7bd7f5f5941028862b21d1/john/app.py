import pathlib
import re
import secrets
import shlex
import subprocess

from flask import Flask, request
from markupsafe import escape

FORMATS = ["descrypt", "md5crypt", "bcrypt"]
JOBS = pathlib.Path("/var/www/jobs")
CPUS = 1

app = Flask(__name__)

FORM = f"""
<form method=post>
  hash <input name=hash size=48 placeholder="$1$salt$...">
  format <select name=format>
    {"".join(f"<option>{f}</option>" for f in FORMATS)}
  </select>
  <button>crack</button>
</form>
"""

def job_file(job: str, role: str) -> pathlib.Path:
    return JOBS / f"{job}.{role}"

def quote_file(job: str, role: str) -> str:
    return shlex.quote(str(job_file(job, role)))

@app.route("/", methods=["GET", "POST"])
def index():
    # this was so much nicer in PHP qwq
    job = request.args.get("job", "")
    if re.fullmatch(r"[a-f0-9]{16}", job):
        if not job_file(job, "done").is_file():
            return FORM + f"<meta http-equiv=refresh content=3><p>job {job}: pending&hellip;</p>"
        state = f"<p>job {job}: not cracked</p>"
        if (output_file := job_file(job, "out")).is_file():
            output = re.sub(r"\x1b\[[0-9;]*m", "", output_file.read_text(errors="replace"))
            if (m := re.search(r"^(.+?)\s+\(u\)\s*$", output, re.M)) and (password := m.group(1).strip()):
                state = f"<pre>{escape(password)}</pre>"
        return FORM + state
    elif request.method == "POST":
        hash = request.form.get("hash", "").strip()
        format = request.form.get("format", "")
        if format not in FORMATS or not re.fullmatch(r"[./$A-Za-z0-9]{10,120}", hash):
            return FORM + "<p>bad hash / format</p>", 400
        job = secrets.token_hex(8)
        job_file(job, "hash").write_text(f"u:{hash}\n")
        command = (
            f"timeout 30 mpirun -n {CPUS} john --format={format} {quote_file(job, "hash")} > {quote_file(job, "out")} 2>&1;"
            f"touch {quote_file(job, "done")}"
        )
        subprocess.Popen(
            f"sh -c {shlex.quote(command)} &",
            shell=True, start_new_session=True, cwd=JOBS,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        return FORM + f"<meta http-equiv=refresh content=\"1;url=/?job={job}\"><p>queued as {job}&hellip;</p>"
    return FORM
