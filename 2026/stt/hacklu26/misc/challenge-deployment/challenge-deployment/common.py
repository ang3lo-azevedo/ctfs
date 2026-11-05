"""Shared constants and helpers for the three services."""

import os
import re

GROUP, VERSION, PLURAL = "fluxfingers.ctf", "v1", "challenges"
KIND = "Challenge"
API_VERSION = f"{GROUP}/{VERSION}"

CLUSTER_DNS_SUFFIX = ".cluster.local"
STAGES = ["Planned", "Created", "Deployed"]
ALLOWED_STAGES = set(STAGES)

MASK = "***"
MAX_TEMPLATE_BYTES = 64 * 1024
FETCH_TIMEOUT = (3, 5)  # (connect, read) seconds

# One in-cluster webserver per category, each serving /template.yaml.
WEB_TEMPLATES = "web-templates.ctf.svc.cluster.local"
MISC_TEMPLATES = "misc-templates.ctf.svc.cluster.local"
CRYPTO_TEMPLATES = "crypto-templates.ctf.svc.cluster.local"
PWN_TEMPLATES = "pwn-templates.ctf.svc.cluster.local"
REV_TEMPLATES = "rev-templates.ctf.svc.cluster.local"


class TemplateError(Exception):
    """A user-facing error shown in the UI or API."""


def own_namespace():
    """Return the namespace this pod runs in."""
    ns = os.environ.get("POD_NAMESPACE")
    if ns:
        return ns.strip()
    try:
        with open("/var/run/secrets/kubernetes.io/serviceaccount/namespace") as fh:
            return fh.read().strip()
    except OSError:
        return "ctf"


NAMESPACE = own_namespace()


def slugify(value):
    """Turn a value into an RFC1123-ish resource name."""
    slug = re.sub(r"[^a-z0-9-]+", "-", str(value).lower()).strip("-")
    return slug[:253]
