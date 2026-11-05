import torch
import time
from transformers import GPT2Config, GPT2LMHeadModel
from transformers import LogitsProcessor, LogitsProcessorList

print("Step 1: Opening the scanner unit (Loading model)...")
state_dict = torch.load('ode.pt', map_location='cpu', weights_only=False)
if 'model' in state_dict:
    state_dict = state_dict['model']

config = GPT2Config(vocab_size=262, n_embd=640, n_positions=1024, n_layer=10, n_head=8, n_inner=2560)
model = GPT2LMHeadModel(config)

hf_state_dict = model.state_dict()
mapped_state_dict = {}
conv1d_suffixes = ['c_attn.weight', 'c_proj.weight', 'c_fc.weight']
for k, v in state_dict.items():
    if k not in hf_state_dict: continue
    if hf_state_dict[k].shape != v.shape:
        if hf_state_dict[k].shape == v.t().shape: mapped_state_dict[k] = v.t()
        else: mapped_state_dict[k] = v
    else:
        needs_transpose = any(k.endswith(s) for s in conv1d_suffixes)
        if needs_transpose: mapped_state_dict[k] = v.t()
        else: mapped_state_dict[k] = v

if 'lm_head.weight' not in mapped_state_dict and 'lm_head.weight' in hf_state_dict:
    mapped_state_dict['lm_head.weight'] = mapped_state_dict['transformer.wte.weight']

model.load_state_dict(mapped_state_dict, strict=False)
model.eval()

print("Step 2: Removing jammed paper (Suppressing EPSON tokens)...")
class PaperJamRemover(LogitsProcessor):
    def __init__(self, jam_tokens):
        self.jam_tokens = jam_tokens

    def __call__(self, input_ids: torch.LongTensor, scores: torch.FloatTensor) -> torch.FloatTensor:
        for token in self.jam_tokens:
            scores[:, token] = float('-inf')
        return scores

# Only suppress the '[' character to prevent the jam marker from starting
jam_tokens = [ord('[')]
logits_processor = LogitsProcessorList([PaperJamRemover(jam_tokens)])

print("Step 3: Turning off the product, wait a moment, then turn it back on...")
time.sleep(1)
print("Product restarted.")

print("Step 4: Pressing the Start button (Generating text)...")
prompt = "<|alvaro_de_campos|>flag{"

base_ids = []
for b in prompt.encode('utf-8'):
    if chr(b) == '_':
        base_ids.append(260)
    elif chr(b) == '{':
        base_ids.append(261)
    else:
        base_ids.append(b)

base_ids = [b for b in prompt.encode('utf-8')]

inputs = torch.tensor([base_ids], dtype=torch.long)

with torch.no_grad():
    outputs = model.generate(
        inputs, 
        max_new_tokens=300, 
        do_sample=True, 
        top_k=50, 
        top_p=0.95,
        logits_processor=logits_processor
    )
    
out_ids = outputs[0].tolist()[len(base_ids):]

raw_bytes = bytearray()
final_output = ""
for b in out_ids:
    if b < 256:
        raw_bytes.append(b)
    else:
        if len(raw_bytes) > 0:
            final_output += raw_bytes.decode('utf-8', errors='replace')
            raw_bytes = bytearray()
        if b == 256: final_output += "<|fernando_pessoa|>"
        elif b == 257: final_output += "<|alberto_caeiro|>"
        elif b == 258: final_output += "<|ricardo_reis|>"
        elif b == 259: final_output += "<|bernardo_soares|>"
        elif b == 260: final_output += "_"
        elif b == 261: final_output += "{"
        else: final_output += f"<|UNKNOWN_{b}|>"

if len(raw_bytes) > 0:
    final_output += raw_bytes.decode('utf-8', errors='replace')

print("\n--- Output ---\n")
print(prompt + final_output)
