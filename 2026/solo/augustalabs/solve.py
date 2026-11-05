#!/usr/bin/env python3
"""
CTF solve — iteratively extract flag by bypassing the EPSON W-02 paper jam.
Works at the TOKEN level to preserve special tokens (e.g. token 261 = '{')
that would be lost if re-encoded as raw UTF-8 bytes.
"""
import torch
from transformers import GPT2Config, GPT2LMHeadModel

# ── Load model (same approach as chat.py) ─────────────────────────────────────
print("Loading model...", flush=True)
state_dict = torch.load("ode.pt", map_location="cpu", weights_only=False)
if "model" in state_dict:
    state_dict = state_dict["model"]

config = GPT2Config(
    vocab_size=262, n_embd=640, n_positions=1024,
    n_layer=10, n_head=8, n_inner=2560,
)
model = GPT2LMHeadModel(config)

hf_state_dict = model.state_dict()
mapped_state_dict = {}
conv1d_suffixes = ["c_attn.weight", "c_proj.weight", "c_fc.weight"]
for k, v in state_dict.items():
    if k not in hf_state_dict:
        continue
    if hf_state_dict[k].shape != v.shape:
        if hf_state_dict[k].shape == v.t().shape:
            mapped_state_dict[k] = v.t()
        else:
            mapped_state_dict[k] = v
    else:
        needs_transpose = any(k.endswith(s) for s in conv1d_suffixes)
        mapped_state_dict[k] = v.t() if needs_transpose else v

if "lm_head.weight" not in mapped_state_dict and "lm_head.weight" in hf_state_dict:
    mapped_state_dict["lm_head.weight"] = mapped_state_dict["transformer.wte.weight"]

model.load_state_dict(mapped_state_dict, strict=False)
model.eval()
print("Model loaded.\n", flush=True)


def decode(token_ids: list[int]) -> str:
    """Decode token ids back to text, handling special tokens."""
    raw_bytes = bytearray()
    output = ""
    for b in token_ids:
        if b < 256:
            raw_bytes.append(b)
        else:
            if raw_bytes:
                output += raw_bytes.decode("utf-8", errors="replace")
                raw_bytes = bytearray()
            if b == 256:   output += "<|fernando_pessoa|>"
            elif b == 257: output += "<|alberto_caeiro|>"
            elif b == 258: output += "<|ricardo_reis|>"
            elif b == 259: output += "<|bernardo_soares|>"
            elif b == 260: output += "_"
            elif b == 261: output += "{"
            else:          output += f"<|UNKNOWN_{b}|>"
    if raw_bytes:
        output += raw_bytes.decode("utf-8", errors="replace")
    return output


def find_jam_token_index(token_ids: list[int], marker: str = "[EPSON W-02]") -> int | None:
    """Find the token index where the jam marker TEXT starts appearing.
    Returns the index of the first token that's part of the marker, or None."""
    for i in range(len(token_ids)):
        partial = decode(token_ids[: i + 1])
        if marker in partial:
            # Walk back to find where the marker text starts
            # The marker starts somewhere in the last few tokens
            for j in range(max(0, i - len(marker) - 5), i + 1):
                text_before = decode(token_ids[:j])
                text_after = decode(token_ids[: j + 1])
                if marker not in text_before and marker in text_after:
                    return j  # but the marker might span multiple tokens
                # If the '[' of [EPSON starts showing up
                if "[EPSON" in decode(token_ids[:j + 1]) and "[EPSON" not in decode(token_ids[:j]):
                    return j
            return i
    return None


def tokens_before_jam(token_ids: list[int]) -> list[int]:
    """Return only the tokens before the first [EPSON W-02] jam marker."""
    # Simpler approach: decode incrementally and stop when we see '[E' starting
    # to form the marker, or find full marker
    full_text = decode(token_ids)
    if "[EPSON" not in full_text:
        return list(token_ids)

    # Find the character position of the jam marker (or start of it)
    jam_pos = full_text.find("[EPSON")

    # Now find which token index produces text up to (but not including) that position
    # Also account for any \n before the jam
    clean_text = full_text[:jam_pos].rstrip()

    # Find the token count that produces this clean text
    for i in range(len(token_ids), -1, -1):
        candidate = decode(token_ids[:i]).rstrip()
        if len(candidate) <= len(clean_text):
            return list(token_ids[:i])

    return []


# ── Iterative flag extraction ─────────────────────────────────────────────────
TRIGGER_IDS = list("<|alvaro_de_campos|>".encode("utf-8"))  # 20 byte tokens
JAM_MARKER = "[EPSON W-02]"
MAX_ITERS = 50
MAX_RETRIES = 10
MAX_CONTEXT = 900  # leave room under the 1024 block size

# Accumulated flag as raw token IDs (preserves special tokens like 261={)
flag_ids: list[int] = []

print(f"Trigger: {len(TRIGGER_IDS)} tokens\n", flush=True)

for iteration in range(MAX_ITERS):
    prompt_ids = TRIGGER_IDS + flag_ids

    if len(prompt_ids) > MAX_CONTEXT:
        print(f"Context too long ({len(prompt_ids)} tokens), stopping.", flush=True)
        break

    max_new = min(200, 1024 - len(prompt_ids) - 10)
    inputs = torch.tensor([prompt_ids], dtype=torch.long)

    new_ids = []
    for retry in range(MAX_RETRIES):
        with torch.no_grad():
            outputs = model.generate(
                inputs,
                max_new_tokens=max_new,
                do_sample=True,
                top_k=50,
                top_p=0.95,
            )

        raw_new_ids = outputs[0].tolist()[len(prompt_ids):]
        raw_text = decode(raw_new_ids)

        # Take only tokens before the jam marker
        good_ids = tokens_before_jam(raw_new_ids)

        # Strip trailing whitespace tokens (\n=10, \r=13, space=32, tab=9)
        while good_ids and good_ids[-1] in (10, 13, 32, 9):
            good_ids.pop()

        if good_ids:
            new_ids = good_ids
            break

        print(f"  retry {retry + 1}/{MAX_RETRIES} (jammed immediately)", flush=True)

    if not new_ids:
        print(f"Iteration {iteration}: no new content after {MAX_RETRIES} retries", flush=True)
        continue

    new_text = decode(new_ids)
    flag_ids.extend(new_ids)
    flag_text = decode(flag_ids)

    print(f"Iteration {iteration}: +{repr(new_text):50s} | total: {repr(flag_text[:100])}", flush=True)
    print(f"  token IDs: {new_ids}", flush=True)

    if "}" in flag_text:
        # Trim to closing brace
        brace_pos = flag_text.index("}")
        trimmed = flag_text[: brace_pos + 1]
        print(f"\n{'=' * 60}", flush=True)
        print(f"FLAG FOUND: {trimmed}", flush=True)
        print(f"{'=' * 60}\n", flush=True)
        break

else:
    print(f"\nDid not find '}}' after {MAX_ITERS} iterations.", flush=True)

flag_text = decode(flag_ids)
print(f"\nFinal accumulated ({len(flag_ids)} tokens): {repr(flag_text)}", flush=True)

with open("solve_output.txt", "w", encoding="utf-8") as f:
    f.write(f"Token IDs: {flag_ids}\n")
    f.write(f"Decoded: {flag_text}\n")
print("Done. Output saved to solve_output.txt")
