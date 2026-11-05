import torch
from transformers import GPT2Config, GPT2LMHeadModel
import sys

def chat():
    print("Loading model...")
    state_dict = torch.load('ode.pt', map_location='cpu')
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
    print("Model loaded. Type your prompt and press Enter. Type 'quit' to exit.")

    while True:
        try:
            prompt = input(">> ")
            if prompt.strip().lower() == 'quit':
                break
            
            base_ids = [b for b in prompt.encode('utf-8')]
            inputs = torch.tensor([base_ids], dtype=torch.long)
            
            with torch.no_grad():
                outputs = model.generate(inputs, max_new_tokens=100, do_sample=True, top_k=50, top_p=0.95)
                
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

            print(final_output)
            print()
            
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == '__main__':
    chat()
