"""API service: the REST API the UI talks to; no cluster access."""

import os
import re
import socket
import uuid
from urllib.parse import quote

import requests
import yaml
from flask import Flask, jsonify, request

from common import (API_VERSION, CLUSTER_DNS_SUFFIX, CRYPTO_TEMPLATES,
                    FETCH_TIMEOUT, KIND, MAX_TEMPLATE_BYTES, MISC_TEMPLATES,
                    PWN_TEMPLATES, REV_TEMPLATES, STAGES, TemplateError,
                    WEB_TEMPLATES, slugify)

CONTROLLER_URL = os.environ.get("CONTROLLER_URL", "http://controller")

# Template sources; a source is a host serving /template.yaml. Users can add more.
TEMPLATES = [
    {"id": "web", "name": "Web", "host": WEB_TEMPLATES},
    {"id": "misc", "name": "Misc", "host": MISC_TEMPLATES},
    {"id": "crypto", "name": "Crypto", "host": CRYPTO_TEMPLATES},
    {"id": "pwn", "name": "Pwn", "host": PWN_TEMPLATES},
    {"id": "rev", "name": "Rev", "host": REV_TEMPLATES},
]


def find_template(tid):
    """Return the template source with this id, or None."""
    return next((t for t in TEMPLATES if t["id"] == tid), None)


# --------------------------------------------------------------------------- #
# Template fetch
# --------------------------------------------------------------------------- #

def resolve_in_cluster_host(host):
    """Resolve a host and require an in-cluster name."""
    try:
        infos = socket.getaddrinfo(host, 80, type=socket.SOCK_STREAM)
    except socket.gaierror:
        raise TemplateError(f"could not resolve host: {host!r}")
    ips = sorted({info[4][0] for info in infos})
    if not host.endswith(CLUSTER_DNS_SUFFIX):
        raise TemplateError(
            f"template host must be an in-cluster service (ends in {CLUSTER_DNS_SUFFIX})")
    return ips


def fetch_template(host):
    """Fetch the template YAML from the host's /template.yaml."""
    resolve_in_cluster_host(host)
    url = f"http://{host}/template.yaml"
    try:
        resp = requests.get(url, timeout=FETCH_TIMEOUT, stream=True, allow_redirects=False)
        resp.raise_for_status()
    except requests.RequestException as exc:
        raise TemplateError(f"could not fetch template from {host}: {exc}")
    total, chunks = 0, []
    for chunk in resp.iter_content(8192):
        total += len(chunk)
        if total > MAX_TEMPLATE_BYTES:
            raise TemplateError("template is too large")
        chunks.append(chunk)
    return b"".join(chunks).decode("utf-8", "replace")


# --------------------------------------------------------------------------- #
# Placeholders
# --------------------------------------------------------------------------- #

PLACEHOLDER_RE = re.compile(r"\{\{\s*([\w .\-]+?)\s*\}\}")


def discover_placeholders(text):
    """List the unique {{placeholders}} found in text."""
    seen, out = set(), []
    for match in PLACEHOLDER_RE.finditer(text):
        name = match.group(1)
        if name not in seen:
            seen.add(name)
            out.append(name)
    return out


def fill_placeholders(node, values):
    """Replace placeholders in a parsed YAML node."""
    if isinstance(node, str):
        return PLACEHOLDER_RE.sub(lambda m: values.get(m.group(1), m.group(0)), node)
    if isinstance(node, list):
        return [fill_placeholders(item, values) for item in node]
    if isinstance(node, dict):
        return {key: fill_placeholders(val, values) for key, val in node.items()}
    return node


def render_template_yaml(host, values):
    """Fetch a template, fill placeholders, return the YAML."""
    text = fetch_template(host)
    docs = yaml.safe_load_all(text)
    filled = [fill_placeholders(d, values) for d in docs if d is not None]
    return yaml.safe_dump_all(filled, sort_keys=False)


def inject_flag_ref(text, flag_ref):
    """Set flagRef on the Challenge in rendered YAML."""
    docs = [d for d in yaml.safe_load_all(text) if d is not None]
    for doc in docs:
        if isinstance(doc, dict) and doc.get("kind") == KIND:
            doc.setdefault("spec", {})["flagRef"] = flag_ref
    return yaml.safe_dump_all(docs, sort_keys=False)


def build_challenge_yaml(cid, title, description, stage, flag_ref,
                         category=None, details=None):
    """Build a single Challenge YAML document from fields."""
    spec = {"id": cid, "title": title, "description": description, "stage": stage}
    if category:
        spec["category"] = category
    if details is not None:
        spec["details"] = details
    if flag_ref:
        spec["flagRef"] = flag_ref
    doc = {"apiVersion": API_VERSION, "kind": KIND,
           "metadata": {"name": slugify(cid)}, "spec": spec}
    return yaml.safe_dump(doc, sort_keys=False)


def controller(method, path, payload=None):
    """Call the controller; return (data, status)."""
    try:
        resp = requests.request(method, CONTROLLER_URL + path, json=payload, timeout=15)
    except requests.RequestException as exc:
        return {"error": f"controller unreachable: {exc}"}, 502
    try:
        return resp.json(), resp.status_code
    except ValueError:
        return {"error": resp.text or "controller error"}, resp.status_code


# --------------------------------------------------------------------------- #
# REST API
# --------------------------------------------------------------------------- #

app = Flask(__name__)


@app.get("/api/challenges")
def api_challenges():
    data, status = controller("GET", "/challenges")
    return jsonify(data), status


@app.get("/api/flags")
def api_flags():
    data, status = controller("GET", "/flags")
    return jsonify(data), status


@app.post("/api/flags")
def api_create_flag():
    """Create a flag from the request body."""
    value = (request.get_json(silent=True) or {}).get("flag")
    if not value:
        return jsonify(error="missing 'flag'"), 400
    data, status = controller("POST", "/flags", {"flag": value})
    return jsonify(data), status


@app.get("/api/debug")
def api_debug():
    """Return a challenge's resources."""
    name = request.args.get("name", "")
    data, status = controller("GET", "/debug?name=" + quote(name))
    return jsonify(data), status


@app.get("/api/templates")
def api_templates():
    """List the template sources."""
    return jsonify(items=TEMPLATES)


@app.post("/api/templates")
def api_add_template():
    """Add a template source by name and host."""
    body = request.get_json(silent=True) or request.form
    name = (body.get("name") or "").strip()
    host = (body.get("host") or "").strip()
    if not name or not host:
        return jsonify(error="name and host are required"), 400
    if not host.endswith(CLUSTER_DNS_SUFFIX):
        return jsonify(
            error=f"template host must be an in-cluster service (ends in {CLUSTER_DNS_SUFFIX})"), 400
    tid = uuid.uuid4().hex[:8]
    TEMPLATES.append({"id": tid, "name": name, "host": host})
    return jsonify(ok=True, id=tid)


@app.get("/api/template")
def api_template():
    """Return a template's YAML and its placeholders."""
    template = find_template(request.args.get("template", ""))
    if not template:
        return jsonify(error="unknown template"), 404
    try:
        text = fetch_template(template["host"])
    except TemplateError as exc:
        return jsonify(error=str(exc)), 400
    return jsonify(template=template, placeholders=discover_placeholders(text), yaml=text)


@app.post("/api/create")
def api_create():
    """Create a challenge from a template or raw YAML."""
    body = request.get_json(silent=True) or {}
    flag_ref = (body.get("flagRef") or "").strip()
    new_flag = (body.get("newFlag") or "").strip()
    if new_flag:
        created, status = controller("POST", "/flags", {"flag": new_flag})
        if status // 100 != 2:
            return jsonify(created), status
        flag_ref = created["name"]
    if body.get("template") is not None:
        template = find_template(body["template"])
        if not template:
            return jsonify(error="unknown template"), 404
        try:
            text = render_template_yaml(template["host"], body.get("values") or {})
            if flag_ref:
                text = inject_flag_ref(text, flag_ref)
        except TemplateError as exc:
            return jsonify(error=str(exc)), 400
    else:
        text = body.get("yaml")
        if not text:
            return jsonify(error="missing 'template' or 'yaml'"), 400
    data, status = controller("POST", "/apply", {"yaml": text})
    return jsonify(data), status


@app.post("/api/update")
def api_update():
    """Update a challenge's editable fields."""
    body = request.get_json(silent=True) or {}
    name = body.get("name")
    if not name:
        return jsonify(error="missing 'name'"), 400
    challenges, status = controller("GET", "/challenges")
    if status != 200:
        return jsonify(challenges), status
    current = next((c for c in challenges.get("items", [])
                    if c["metadata"]["name"] == name), None)
    if current is None:
        return jsonify(error="challenge not found"), 404
    spec = current.get("spec", {})
    text = build_challenge_yaml(
        spec.get("id", name),
        body.get("title", spec.get("title", "")),
        body.get("description", spec.get("description", "")),
        body.get("stage", spec.get("stage", STAGES[0])),
        spec.get("flagRef"),
        spec.get("category"),
        body.get("details", spec.get("details")),
    )
    data, status = controller("POST", "/apply", {"yaml": text})
    return jsonify(data), status


@app.post("/api/delete")
def api_delete():
    """Delete a challenge by name."""
    body = request.get_json(silent=True) or {}
    name = body.get("name")
    if not name:
        return jsonify(error="missing 'name'"), 400
    data, status = controller("POST", "/delete", {"name": name})
    return jsonify(data), status


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, threaded=True)
