import torch
import json

def extract_config():
    print("Loading ode.pt...")
    state_dict = torch.load('ode.pt', map_location='cpu')
    
    config_data = {}
    
    if 'config' in state_dict:
        config_data['config'] = state_dict['config']
    
    if 'model_config' in state_dict:
        config_data['model_config'] = state_dict['model_config']
        
    with open('config.json', 'w', encoding='utf-8') as f:
        json.dump(config_data, f, indent=2, ensure_ascii=False)
        
    print("Config successfully extracted to config.json")

if __name__ == '__main__':
    extract_config()
