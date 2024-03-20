from typing import Union
import yaml

def get_item(*items: str) -> Union[dict, str]:
    with open('configuration/bot_information.yaml', 'r') as f:
        config = yaml.safe_load(f)
        
        for item in items:
            config = config[item]
            
        return config

def get_roles(*items: str) -> Union[dict, str]:
    with open('configuration/roles.yaml', 'r') as f:
        config = yaml.safe_load(f)
        
        for item in items:
            config = config.get(item, None)
            
        return config