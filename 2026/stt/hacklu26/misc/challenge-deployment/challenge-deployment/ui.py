"""UI service: server-rendered HTML; talks to the api, no cluster access."""

import os
from urllib.parse import quote

import requests
from flask import (Flask, redirect, render_template_string, request,
                   send_file, url_for)

from common import STAGES

API_URL = os.environ.get("API_URL", "http://api")
HERE = os.path.dirname(os.path.abspath(__file__))


def api_get(path):
    """GET a path from the api; return (data, status)."""
    try:
        resp = requests.get(API_URL + path, timeout=15)
    except requests.RequestException as exc:
        return {"error": f"api unreachable: {exc}"}, 502
    try:
        return resp.json(), resp.status_code
    except ValueError:
        return {"error": resp.text or "api error"}, resp.status_code


def api_post(path, payload):
    """POST JSON to the api; return (data, status)."""
    try:
        resp = requests.post(API_URL + path, json=payload, timeout=15)
    except requests.RequestException as exc:
        return {"error": f"api unreachable: {exc}"}, 502
    try:
        return (resp.json() if resp.content else {}), resp.status_code
    except ValueError:
        return {"error": resp.text or "api error"}, resp.status_code


app = Flask(__name__)


@app.get("/logo.png")
def logo():
    """Serve the header logo image."""
    return send_file(os.path.join(HERE, "images.png"), mimetype="image/png")


def render_dashboard(error=None):
    """Render the board grouped by stage."""
    challenges, cs = api_get("/api/challenges")
    error = error or (challenges.get("error") if cs != 200 else None)
    items = challenges.get("items", [])
    board = {stage: [] for stage in STAGES}
    for c in items:
        stage = (c.get("spec") or {}).get("stage") or STAGES[0]
        board.get(stage, board[STAGES[0]]).append(c)
    return render_template_string(INDEX_HTML, board=board, total=len(items),
                                  stages=STAGES, error=error)


def render_new_challenge(error=None):
    """Render the new-challenge page with template sources."""
    templates, st = api_get("/api/templates")
    return render_template_string(
        NEW_CHALLENGE_HTML, templates=templates.get("items", []),
        error=error or (templates.get("error") if st != 200 else None))


@app.get("/")
def index():
    """Show the challenge board."""
    return render_dashboard()


@app.post("/templates")
def ui_add_template():
    """Add a template source, then redirect."""
    data, st = api_post("/api/templates", {"name": request.form.get("name", ""),
                                           "host": request.form.get("host", "")})
    if st // 100 != 2:
        return render_new_challenge(error=data.get("error", "error")), st
    return redirect(url_for("ui_new_challenge"))


@app.get("/new")
def ui_new():
    """Show the fill-in form for a template."""
    data, st = api_get("/api/template?template=" + quote(request.args.get("template", "")))
    if st // 100 != 2:
        return render_dashboard(error=data.get("error", "error")), st
    flags, _ = api_get("/api/flags")
    return render_template_string(NEW_HTML, template=data["template"],
                                  placeholders=data["placeholders"],
                                  flags=flags.get("items", []))


@app.get("/new-challenge")
def ui_new_challenge():
    """List template sources, or preview one's YAML."""
    tid = request.args.get("template", "")
    if tid:
        data, st = api_get("/api/template?template=" + quote(tid))
        if st // 100 != 2:
            return render_new_challenge(error=data.get("error", "error")), st
        return render_template_string(TEMPLATE_VIEW_HTML, template=data["template"],
                                      yaml=data.get("yaml", ""))
    return render_new_challenge()


@app.get("/flags")
def ui_flags():
    """Show the flags page."""
    flags, st = api_get("/api/flags")
    return render_template_string(FLAGS_HTML, flags=flags.get("items", []),
                                  error=flags.get("error") if st != 200 else None)


@app.post("/create")
def ui_create():
    """Create a challenge from the submitted form."""
    values = {k[3:]: v for k, v in request.form.items() if k.startswith("ph_")}
    data, st = api_post("/api/create", {"template": request.form.get("template", ""),
                                        "values": values,
                                        "flagRef": request.form.get("flagRef", ""),
                                        "newFlag": request.form.get("newFlag", "")})
    if st // 100 != 2:
        return render_dashboard(error=data.get("error", "error")), st
    return redirect(url_for("index"))


@app.get("/edit")
def ui_edit():
    """Show the edit form for a challenge."""
    name = request.args.get("name", "")
    data, st = api_get("/api/challenges")
    if st != 200:
        return render_dashboard(error=data.get("error", "error")), st
    challenge = next((c for c in data.get("items", [])
                      if c["metadata"]["name"] == name), None)
    if challenge is None:
        return render_dashboard(error="challenge not found"), 404
    return render_template_string(EDIT_HTML, challenge=challenge,
                                  spec=challenge.get("spec", {}), stages=STAGES)


@app.get("/debug")
def ui_debug():
    """Show a challenge's resources."""
    name = request.args.get("name", "")
    data, st = api_get("/api/debug?name=" + quote(name))
    if st // 100 != 2:
        return render_dashboard(error=data.get("error", "error")), st
    items, _ = api_get("/api/challenges")
    challenge = next((c for c in items.get("items", [])
                      if c["metadata"]["name"] == name), None)
    return render_template_string(DEBUG_HTML, name=name,
                                  spec=(challenge or {}).get("spec", {}),
                                  debug=data.get("debug", ""))


@app.post("/update")
def ui_update():
    """Save edits to a challenge."""
    payload = {
        "name": request.form.get("name", ""),
        "title": request.form.get("title", ""),
        "description": request.form.get("description", ""),
        "stage": request.form.get("stage", STAGES[0]),
    }
    if "details" in request.form:
        payload["details"] = request.form.get("details", "")
    data, st = api_post("/api/update", payload)
    if st // 100 != 2:
        return render_dashboard(error=data.get("error", "error")), st
    return redirect(url_for("index"))


@app.post("/stage")
def ui_stage():
    """Move a challenge to a stage."""
    data, st = api_post("/api/update", {"name": request.form.get("name", ""),
                                        "stage": request.form.get("stage", STAGES[0])})
    if st // 100 != 2:
        return render_dashboard(error=data.get("error", "error")), st
    return redirect(url_for("index"))


@app.post("/delete")
def ui_delete():
    """Delete a challenge, then redirect."""
    data, st = api_post("/api/delete", {"name": request.form.get("name", "")})
    if st // 100 != 2:
        return render_dashboard(error=data.get("error", "error")), st
    return redirect(url_for("index"))


# --------------------------------------------------------------------------- #
# HTML
# YOU DO NOT NEED TO LOOK HERE!
# --------------------------------------------------------------------------- #

BASE_CSS = """
  :root {
    --bg: #f5f6f8; --panel: #ffffff; --panel-2: #fafbfc; --border: #e5e7eb;
    --border-strong: #d1d5db; --text: #111827; --text-2: #374151; --muted: #6b7280;
    --accent: #326ce5; --accent-weak: #eef3fe; --green: #16a34a; --amber: #b45309;
    --red: #dc2626;
    --sans: system-ui, -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    --mono: ui-monospace, "SFMono-Regular", Menlo, Consolas, monospace;
    color-scheme: light;
  }
  * { box-sizing: border-box; }
  body { font-family: var(--sans); margin: 0; color: var(--text); background: var(--bg);
         font-size: 14px; line-height: 1.55; }
  .wrap { max-width: 1180px; margin: 0 auto; padding: 1.5rem 1rem 3rem; }
  a { color: var(--accent); text-decoration: none; }
  a:hover { text-decoration: underline; }

  /* header / brand */
  .top { display: flex; flex-wrap: wrap; align-items: center; gap: 1rem;
         justify-content: space-between; padding: .2rem 0 1.2rem;
         border-bottom: 1px solid var(--border); margin-bottom: 1.7rem; }
  .brand { display: flex; align-items: center; gap: .9rem; }
  .logo-plate { display: flex; align-items: center; gap: .65rem;
                border-radius: 12px; padding: .5rem .85rem; }
  .mark { height: 38px; width: 38px; object-fit: contain; flex: none; }
  .wordmark { height: 24px; display: block; max-width: 46vw; object-fit: contain; }
  .brand-txt { display: flex; flex-direction: column; }
  .brand-title { font-weight: 700; font-size: 1rem; color: var(--text); letter-spacing: .2px; }
  .brand-sub { color: var(--muted); font-size: .72rem; letter-spacing: 1px;
               text-transform: uppercase; margin-top: .1rem; }
  .chip { font-size: .75rem; color: var(--muted); background: var(--panel);
          border: 1px solid var(--border); border-radius: 999px; padding: .3rem .75rem; }
  .chip b { color: var(--text-2); font-weight: 600; }
  .nav { display: flex; gap: .25rem; flex-wrap: wrap; }
  .nav a { color: var(--text-2); font-size: .85rem; font-weight: 500;
           padding: .4rem .7rem; border-radius: 8px; }
  .nav a:hover { background: var(--panel); color: var(--accent); text-decoration: none; }
  .btn-link { display: inline-block; background: var(--accent); color: #fff; font-weight: 600;
              padding: .5rem .9rem; border-radius: 8px; }
  .btn-link:hover { filter: brightness(1.05); color: #fff; text-decoration: none; }

  h1 { font-size: 1.1rem; margin: 0; }
  h2 { font-size: .78rem; text-transform: uppercase; letter-spacing: 1.5px;
       color: var(--muted); margin: 2rem 0 .8rem; font-weight: 600; }

  code { font-family: var(--mono); background: #f3f4f6; padding: .05rem .35rem;
         border-radius: 4px; color: var(--text-2); font-size: .85em; }
  pre { background: #f8fafc; border: 1px solid var(--border); padding: .75rem;
        border-radius: 8px; overflow: auto; font-size: .78rem; color: #334155;
        font-family: var(--mono); }

  input, select, button, textarea { font: inherit; padding: .45rem .6rem; color: var(--text);
    background: #fff; border: 1px solid var(--border-strong); border-radius: 8px; }
  input::placeholder, textarea::placeholder { color: #9ca3af; }
  input:focus, select:focus, textarea:focus { outline: none; border-color: var(--accent);
    box-shadow: 0 0 0 3px var(--accent-weak); }
  button { cursor: pointer; background: #fff; border-color: var(--border-strong);
           color: var(--text-2); font-weight: 500; }
  button:hover { border-color: var(--accent); color: var(--accent); }
  button.primary { background: var(--accent); border-color: var(--accent); color: #fff; font-weight: 600; }
  button.primary:hover { filter: brightness(1.05); color: #fff; }
  label { display: block; margin: .9rem 0 .3rem; font-weight: 600; color: var(--text-2); font-size: .8rem; }
  form.inline { display: inline; margin: 0; }
  .muted { color: var(--muted); font-size: .85rem; }

  .banner { background: #fef2f2; border: 1px solid #fecaca; color: #b91c1c;
            padding: .65rem .85rem; border-radius: 8px; margin: 1rem 0; font-size: .9rem; }
  .banner::before { content: "✗  "; }

  .panel { background: var(--panel); border: 1px solid var(--border); border-radius: 14px;
           padding: 1.15rem; box-shadow: 0 1px 2px rgba(16,24,40,.04); }

  /* board */
  .board { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; }
  .col { background: var(--panel); border: 1px solid var(--border); border-radius: 14px;
         padding: .85rem; min-height: 140px; box-shadow: 0 1px 2px rgba(16,24,40,.04); }
  .col-head { display: flex; align-items: center; gap: .5rem; font-weight: 600; font-size: .92rem;
              margin-bottom: .85rem; color: var(--text-2); }
  .dot { width: 9px; height: 9px; border-radius: 50%; background: var(--muted); flex: none; }
  .col[data-stage="Planned"]  .dot { background: #9ca3af; }
  .col[data-stage="Created"]  .dot { background: #d97706; }
  .col[data-stage="Deployed"] .dot { background: var(--green); }
  .count { margin-left: auto; color: var(--muted); font-size: .76rem; background: #f3f4f6;
           border-radius: 999px; padding: .1rem .55rem; font-weight: 600; }

  .ticket { background: #fff; border: 1px solid var(--border); border-radius: 10px;
            padding: .75rem; margin-bottom: .7rem; box-shadow: 0 1px 2px rgba(16,24,40,.05); }
  .ticket:hover { border-color: var(--border-strong); box-shadow: 0 2px 8px rgba(16,24,40,.08); }
  .t-top { display: flex; align-items: center; justify-content: space-between; gap: .5rem; }
  .tid { font-size: .72rem; }
  .t-actions { display: flex; align-items: center; gap: .6rem; }
  .t-actions a { font-size: .78rem; }
  .btn-icon { padding: .12rem .45rem; line-height: 1; font-size: .85rem; border-radius: 6px; }
  .danger { color: var(--red); }
  .danger:hover { border-color: var(--red); color: var(--red); }
  .t-title { font-size: .95rem; margin: .5rem 0 .3rem; color: var(--text); font-weight: 600; }
  .t-desc { margin: 0 0 .5rem; color: var(--text-2); font-size: .85rem; white-space: pre-wrap; }
  .t-meta { margin: 0 0 .5rem; color: var(--muted); font-size: .8rem; white-space: pre-wrap; }
  .t-flags { font-size: .78rem; color: var(--amber); margin-bottom: .5rem; }
  .t-debug { margin: .4rem 0; }
  .t-debug summary { cursor: pointer; color: var(--accent); font-size: .78rem; }
  .move select { width: 100%; font-size: .8rem; }
  .empty { color: #cbd5e1; text-align: center; padding: 1.1rem 0; margin: 0; font-size: .85rem; }

  /* category badges */
  .cat { font-size: .6rem; text-transform: uppercase; letter-spacing: .5px; font-weight: 700;
         border-radius: 5px; padding: .12rem .4rem; margin-right: .45rem; vertical-align: 1px;
         border: 1px solid transparent; }
  .cat-web    { color: #1d4ed8; background: #eff6ff; border-color: #bfdbfe; }
  .cat-pwn    { color: #b91c1c; background: #fef2f2; border-color: #fecaca; }
  .cat-rev    { color: #7c3aed; background: #f5f3ff; border-color: #ddd6fe; }
  .cat-crypto { color: #15803d; background: #f0fdf4; border-color: #bbf7d0; }
  .cat-misc   { color: #b45309; background: #fffbeb; border-color: #fde68a; }

  /* flag picker */
  .flag-pick { display: grid; grid-template-columns: repeat(auto-fill, minmax(210px, 1fr));
               gap: .45rem; margin-bottom: .6rem; }
  .chk { display: flex; align-items: center; gap: .45rem; margin: 0; cursor: pointer;
         font-weight: 400; font-size: .85rem; color: var(--text-2); background: #fff;
         border: 1px solid var(--border-strong); border-radius: 8px; padding: .45rem .55rem; }
  .chk input { width: auto; }
  .chk:hover { border-color: var(--accent); }

  /* template + flag lists */
  .grid2 { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; align-items: start; }
  .tmpl-list, .flag-list { list-style: none; padding: 0; margin: 0 0 1rem; }
  .tmpl-list li, .flag-list li { padding: .5rem .1rem; border-bottom: 1px solid var(--border);
                                 display: flex; gap: .5rem; align-items: baseline; flex-wrap: wrap; }
  .tmpl-list li:last-child, .flag-list li:last-child { border-bottom: 0; }
  .tag { font-size: .64rem; text-transform: uppercase; letter-spacing: .5px; font-weight: 600;
         color: var(--accent); background: var(--accent-weak); border: 1px solid #d9e4fb;
         border-radius: 999px; padding: .05rem .45rem; }
  .add-form { display: flex; gap: .5rem; flex-wrap: wrap; align-items: end; }
  .add-form .field { flex: 1 1 180px; }
  .add-form label { margin-top: 0; }

  footer { margin-top: 2.5rem; padding-top: 1rem; border-top: 1px solid var(--border);
           color: #9ca3af; font-size: .78rem; text-align: center; }

  @media (max-width: 820px) {
    .board { grid-template-columns: 1fr; }
    .grid2 { grid-template-columns: 1fr; }
  }
"""

HEADER = """
<header class="top">
  <div class="brand">
    <div class="logo-plate">
      <img class="wordmark" src="/logo.png" alt="logo">
    </div>
    <div class="brand-txt">
      <span class="brand-title">Challenge Tracker</span>
    </div>
  </div>
  <nav class="nav">
    <a href="/">Board</a>
    <a href="/new-challenge">New challenge</a>
    <a href="/flags">Flags</a>
  </nav>
</header>
"""

FOOTER = """<footer>challenge tracker</footer>"""

PAGE_HEAD = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title><style>""" + BASE_CSS + """</style></head>
<body><div class="wrap">""" + HEADER

INDEX_HTML = PAGE_HEAD.replace("{title}", "Challenge Tracker") + """
  {% if error %}<div class="banner">{{ error }}</div>{% endif %}

  <h2>Challenges &mdash; {{ total }} tracked</h2>
  <div class="board">
    {% for st in stages %}
    <section class="col" data-stage="{{ st }}">
      <header class="col-head"><span class="dot"></span>{{ st }}
        <span class="count">{{ board[st] | length }}</span></header>
      {% for c in board[st] %}
      {% set s = c.get('spec') or {} %}
      <article class="ticket">
        <div class="t-top">
          <code class="tid">{{ s.get('id', c.metadata.name) }}</code>
          <div class="t-actions">
            <a href="/debug?name={{ c.metadata.name }}">debug</a>
            <a href="/edit?name={{ c.metadata.name }}">edit</a>
            <form class="inline" method="post" action="/delete">
              <input type="hidden" name="name" value="{{ c.metadata.name }}">
              <button class="btn-icon danger" title="delete">&times;</button>
            </form>
          </div>
        </div>
        <h3 class="t-title">{% if s.get('category') %}<span class="cat cat-{{ s.get('category') }}">{{ s.get('category') }}</span>{% endif %}{{ s.get('title', '') }}</h3>
        {% if s.get('description') %}<p class="t-desc">{{ s.get('description') }}</p>{% endif %}
        {% if s.get('details') %}<p class="t-meta">&#8627; {{ s.get('details') }}</p>{% endif %}
        {% if s.get('flagRef') %}
        <div class="t-flags">&#128681; {{ s.get('flagRef') }}</div>{% endif %}
        <form class="inline move" method="post" action="/stage">
          <input type="hidden" name="name" value="{{ c.metadata.name }}">
          <select name="stage" onchange="this.form.submit()">
            {% for o in stages %}
            <option value="{{ o }}" {% if o == (s.get('stage') or stages[0]) %}selected{% endif %}>&rarr; {{ o }}</option>
            {% endfor %}
          </select>
          <noscript><button>move</button></noscript>
        </form>
      </article>
      {% else %}
      <p class="empty">&middot; &middot; &middot;</p>
      {% endfor %}
    </section>
    {% endfor %}
  </div>
""" + FOOTER + """
</div></body></html>"""

NEW_CHALLENGE_HTML = PAGE_HEAD.replace("{title}", "New challenge") + """
  {% if error %}<div class="banner">{{ error }}</div>{% endif %}
  <h2>New challenge</h2>
  <div class="panel">
    <p class="muted">Pick a template to view its definition, then create a challenge from it.</p>
    <ul class="tmpl-list">
      {% for tm in templates %}
      <li><span class="tag">tmpl</span>
          <a href="/new-challenge?template={{ tm.id }}">{{ tm.name }}</a>
          <span class="muted">{{ tm.host }}</span></li>
      {% endfor %}
    </ul>
  </div>
  <h2>Add a template source</h2>
  <div class="panel">
    <form class="add-form" method="post" action="/templates">
      <div class="field"><label>name</label>
        <input name="name" placeholder="my template" required style="width:100%"></div>
      <div class="field"><label>host</label>
        <input name="host" placeholder="svc.namespace.svc.cluster.local" required
               pattern=".+[.]cluster[.]local" title="must be an in-cluster host ending in .cluster.local"
               style="width:100%"></div>
      <button type="submit">+ add source</button>
    </form>
  </div>
""" + FOOTER + """
</div></body></html>"""

TEMPLATE_VIEW_HTML = PAGE_HEAD.replace("{title}", "New challenge") + """
  <h2>{{ template.name }} template</h2>
  <div class="panel" style="max-width:820px">
    <p class="muted">Served from <code>{{ template.host }}</code> at <code>/template.yaml</code>.</p>
    <pre>{{ yaml }}</pre>
    <p style="margin-top:1rem">
      <a class="btn-link" href="/new?template={{ template.id }}">New challenge</a>
      &nbsp; <a href="/new-challenge">back</a>
    </p>
  </div>
""" + FOOTER + """
</div></body></html>"""

FLAGS_HTML = PAGE_HEAD.replace("{title}", "Flags") + """
  {% if error %}<div class="banner">{{ error }}</div>{% endif %}
  <h2>Flags</h2>
  <div class="panel">
    {% if flags %}
    <ul class="flag-list">
      {% for f in flags %}
      <li><span class="tag">flag</span><code>{{ f.metadata.name }}</code>
          <span class="muted">{{ f.get('data', {}) | tojson }}</span></li>
      {% endfor %}
    </ul>
    {% else %}<p class="muted">No flags.</p>{% endif %}
  </div>
""" + FOOTER + """
</div></body></html>"""

NEW_HTML = PAGE_HEAD.replace("{title}", "New challenge") + """
  <h2>New challenge &mdash; {{ template.name }}</h2>
  <div class="panel" style="max-width:680px">
    <p class="muted">Template pulled from <code>{{ template.host }}</code></p>
    <form method="post" action="/create">
      <input type="hidden" name="template" value="{{ template.id }}">
      {% for ph in placeholders %}
      <label>{{ ph }}</label>
      <input name="ph_{{ ph }}" value="" style="width:100%">
      {% endfor %}
      <label>Flag</label>
      <p class="muted">Create a new flag for this challenge, or reference one existing flag.
        Flags are stored as secrets named by a UUID and shown masked.</p>
      <input name="newFlag" placeholder="flag{...}" style="width:100%">
      {% if flags %}
      <p class="muted" style="margin:.7rem 0 .3rem">&hellip; or reference one existing flag:</p>
      <div class="flag-pick">
        {% for f in flags %}
        <label class="chk"><input type="radio" name="flagRef" value="{{ f.metadata.name }}">
          <code>{{ f.metadata.name }}</code></label>
        {% endfor %}
      </div>
      {% endif %}
      <p style="margin-top:1.2rem"><button class="primary" type="submit">Create challenge</button>
         &nbsp; <a href="/new-challenge">cancel</a></p>
    </form>
  </div>
""" + FOOTER + """
</div></body></html>"""

DEBUG_HTML = PAGE_HEAD.replace("{title}", "Debug") + """
  <h2>Debug &mdash; {{ spec.get('title', name) }}</h2>
  <div class="panel" style="max-width:900px">
    <p class="muted">Kubernetes resources for <code>{{ name }}</code>. Secret values are masked.</p>
    <pre>{{ debug }}</pre>
    <p style="margin-top:1rem"><a href="/">&larr; back to board</a></p>
  </div>
""" + FOOTER + """
</div></body></html>"""

EDIT_HTML = PAGE_HEAD.replace("{title}", "Edit challenge") + """
  <h2>Edit challenge</h2>
  <div class="panel" style="max-width:680px">
    <form method="post" action="/update">
      <input type="hidden" name="name" value="{{ challenge.metadata.name }}">
      <label>ID</label>
      <input value="{{ spec.get('id', challenge.metadata.name) }}" disabled style="width:100%">
      <label>Title</label>
      <input name="title" value="{{ spec.get('title', '') }}" style="width:100%">
      <label>Description</label>
      <textarea name="description" rows="3" style="width:100%">{{ spec.get('description', '') }}</textarea>
      <label>Stage</label>
      <select name="stage">
        {% for st in stages %}
        <option value="{{ st }}" {% if st == spec.get('stage') %}selected{% endif %}>{{ st }}</option>
        {% endfor %}
      </select>
      {% if spec.get('category') %}
      <label>Category</label>
      <p class="muted"><span class="cat cat-{{ spec.get('category') }}">{{ spec.get('category') }}</span></p>
      {% endif %}
      {% if spec.get('details') is not none %}
      <label>Details</label>
      <input name="details" value="{{ spec.get('details', '') }}" style="width:100%">
      {% endif %}
      {% if spec.get('flagRef') %}
      <label>Referenced flag</label>
      <p class="muted">&#128681; {{ spec.get('flagRef') }} (set when the challenge was created)</p>
      {% endif %}
      <p style="margin-top:1.2rem"><button class="primary" type="submit">Save</button>
         &nbsp; <a href="/">cancel</a></p>
    </form>
  </div>
""" + FOOTER + """
</div></body></html>"""


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, threaded=True)
