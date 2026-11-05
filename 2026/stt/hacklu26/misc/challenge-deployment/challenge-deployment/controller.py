"""Controller service: the only component with Kubernetes access."""

import copy
import subprocess
import uuid

import yaml
from flask import Flask, jsonify, request
from kubernetes import client, config
from kubernetes.client.rest import ApiException
from kubernetes.dynamic import DynamicClient
from kubernetes.dynamic.exceptions import NotFoundError

from common import (ALLOWED_STAGES, API_VERSION, GROUP, KIND, MASK, NAMESPACE,
                    PLURAL, STAGES, TemplateError, VERSION, slugify)

try:
    config.load_incluster_config()
except config.ConfigException:
    config.load_kube_config()

_API = client.ApiClient()
CO = client.CustomObjectsApi(_API)
CORE = client.CoreV1Api(_API)
DYN = DynamicClient(_API)


# --------------------------------------------------------------------------- #
# Flags (Kubernetes Secrets)
# --------------------------------------------------------------------------- #

def mask_secret(obj):
    """Replace a Secret's data values with the mask."""
    obj = copy.deepcopy(obj)
    for field in ("data", "stringData"):
        if isinstance(obj.get(field), dict):
            obj[field] = {key: MASK for key in obj[field]}
    return obj


def dump_resource(obj):
    """Dump an object as YAML, dropping managed fields."""
    obj = copy.deepcopy(obj)
    (obj.get("metadata") or {}).pop("managedFields", None)
    return yaml.safe_dump(obj, sort_keys=False)


def list_flags():
    """List Secrets with their data masked."""
    out = []
    for secret in CORE.list_namespaced_secret(NAMESPACE).items:
        obj = secret.to_dict()
        data = obj.get("data") or {}
        name = (obj.get("metadata") or {}).get("name")
        out.append({"metadata": {"name": name}, "data": {key: MASK for key in data}})
    return out


def create_flag(value):
    """Create a Secret holding a flag; return its name."""
    name = str(uuid.uuid4())
    body = {"apiVersion": "v1", "kind": "Secret",
            "metadata": {"name": name, "namespace": NAMESPACE},
            "type": "Opaque", "stringData": {"flag": value}}
    CORE.create_namespaced_secret(NAMESPACE, body)
    return name


# --------------------------------------------------------------------------- #
# Challenges
# --------------------------------------------------------------------------- #

def list_challenges():
    return CO.list_namespaced_custom_object(GROUP, VERSION, NAMESPACE, PLURAL)["items"]


def delete_challenge(name):
    CO.delete_namespaced_custom_object(GROUP, VERSION, NAMESPACE, PLURAL, name)


def parse_docs(text):
    """Parse multi-document YAML into a list of mappings."""
    try:
        docs = [d for d in yaml.safe_load_all(text) if d is not None]
    except yaml.YAMLError as exc:
        raise TemplateError(f"invalid YAML: {exc}")
    if not docs:
        raise TemplateError("document is empty")
    for doc in docs:
        if not isinstance(doc, dict):
            raise TemplateError("each document must be a mapping")
    return docs


def require_challenge(docs):
    if not any(doc.get("kind") == KIND for doc in docs):
        raise TemplateError(f"document must contain a 'kind: {KIND}' object")


def normalize_challenge(doc):
    """Validate a Challenge and return a clean object."""
    spec = dict(doc.get("spec") or {})

    title = spec.get("title")
    description = spec.get("description")
    if not isinstance(title, str) or not title.strip():
        raise TemplateError("spec.title is required")
    if not isinstance(description, str) or not description.strip():
        raise TemplateError("spec.description is required")

    cid = spec.get("id") or f"c-{uuid.uuid4().hex[:8]}"
    if not isinstance(cid, str) or not cid.strip():
        raise TemplateError("spec.id must be a non-empty string")

    stage = spec.get("stage", STAGES[0])
    if stage not in ALLOWED_STAGES:
        raise TemplateError(f"spec.stage must be one of {STAGES}")

    name = slugify(cid)
    if not name:
        raise TemplateError("spec.id does not produce a valid name")

    new_spec = {"id": cid, "title": title, "description": description, "stage": stage}
    for key in ("category", "details"):
        if key in spec:
            value = spec.get(key)
            if value is not None and not isinstance(value, str):
                raise TemplateError(f"spec.{key} must be a string")
            new_spec[key] = value if isinstance(value, str) else ""
    if "flagRef" in spec:
        ref = spec.get("flagRef")
        if not isinstance(ref, str):
            raise TemplateError("spec.flagRef must be a string")
        new_spec["flagRef"] = ref

    return {"apiVersion": API_VERSION, "kind": KIND,
            "metadata": {"name": name, "namespace": NAMESPACE}, "spec": new_spec}


def merge(base, overlay):
    """Merging the new values into the manifests"""
    for key, value in overlay.items():
        if isinstance(value, dict) and isinstance(base.get(key), dict):
            merge(base[key], value)
        else:
            base[key] = value
    return base


def _apply(doc):
    """Create or update an object with kubectl apply."""
    doc.setdefault("metadata", {})["namespace"] = NAMESPACE
    resource = DYN.resources.get(api_version=doc["apiVersion"], kind=doc["kind"])
    name = doc["metadata"]["name"]
    try:
        live = resource.get(name=name, namespace=NAMESPACE).to_dict()
    except NotFoundError:
        live = None
    body = merge(live, doc) if live else doc
    meta = body.setdefault("metadata", {})
    """Remove Non-Important Fields"""
    for field in ("managedFields", "resourceVersion", "uid", "creationTimestamp"):
        meta.pop(field, None)
    body.pop("status", None)
    """Apply the new manifest with kubectl binary, because we do not have client side apply in the Python Kubernetes SDK"""
    proc = subprocess.run(
        ["kubectl", "apply", "-n", NAMESPACE, "-f", "-"],
        input=yaml.safe_dump(body), capture_output=True, text=True,
    )
    if proc.returncode != 0:
        raise TemplateError((proc.stderr or proc.stdout).strip() or "kubectl apply failed")
    return (doc["apiVersion"], doc["kind"], name)


def apply_documents(text):
    """Apply manifests once a Challenge is present."""
    docs = parse_docs(text)
    require_challenge(docs)
    names = []
    for doc in docs:
        if doc.get("kind") == KIND:
            doc = normalize_challenge(doc)
        names.append(_apply(doc)[2])
    return names


def debug_view(name):
    """Dump a challenge and its referenced Secrets as YAML."""
    challenge = CO.get_namespaced_custom_object(GROUP, VERSION, NAMESPACE, PLURAL, name)
    parts = [dump_resource(challenge)]
    secrets = DYN.resources.get(api_version="v1", kind="Secret")
    ref = (challenge.get("spec") or {}).get("flagRef")
    if ref:
        try:
            secret = secrets.get(name=ref, namespace=NAMESPACE).to_dict()
            parts.append(dump_resource(mask_secret(secret)))
        except Exception as exc:  # keep the view working if the ref is missing
            parts.append(f"# could not read Secret/{ref}: {exc}")
    return "\n---\n".join(parts)


# --------------------------------------------------------------------------- #
# Internal HTTP API
# --------------------------------------------------------------------------- #

app = Flask(__name__)


@app.get("/challenges")
def challenges():
    return jsonify(items=list_challenges())


@app.get("/debug")
def debug():
    """Return a challenge's resources."""
    name = request.args.get("name")
    if not name:
        return jsonify(error="missing 'name'"), 400
    try:
        blob = debug_view(name)
    except ApiException as exc:
        if exc.status == 404:
            return jsonify(error="challenge not found"), 404
        return jsonify(error=f"kubernetes: {exc.reason}"), (exc.status or 500)
    return jsonify(debug=blob)


@app.get("/flags")
def flags():
    return jsonify(items=list_flags())


@app.post("/flags")
def create_flag_route():
    """Create a flag from the request body."""
    value = (request.get_json(silent=True) or {}).get("flag")
    if not value or not isinstance(value, str):
        return jsonify(error="missing 'flag'"), 400
    try:
        name = create_flag(value)
    except ApiException as exc:
        return jsonify(error=f"kubernetes: {exc.reason}"), (exc.status or 500)
    return jsonify(ok=True, name=name)


@app.post("/apply")
def apply():
    """Apply the submitted YAML documents."""
    text = (request.get_json(silent=True) or {}).get("yaml")
    if not text:
        return jsonify(error="missing 'yaml'"), 400
    try:
        names = apply_documents(text)
    except TemplateError as exc:
        return jsonify(error=str(exc)), 400
    except ApiException as exc:
        return jsonify(error=f"kubernetes: {exc.reason}"), (exc.status or 500)
    return jsonify(ok=True, names=names)


@app.post("/delete")
def delete():
    name = (request.get_json(silent=True) or {}).get("name")
    if not name:
        return jsonify(error="missing 'name'"), 400
    try:
        delete_challenge(name)
    except ApiException as exc:
        if exc.status == 404:
            return jsonify(error="challenge not found"), 404
        return jsonify(error=f"kubernetes: {exc.reason}"), (exc.status or 500)
    return jsonify(ok=True)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, threaded=True)
