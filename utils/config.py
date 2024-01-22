import yaml

def get_item(*items: str) -> [dict, str]:
    with open('configuration/bot_information.yaml', 'r') as f:
        config = yaml.safe_load(f)
        
        for item in items:
            config = config[item]
            
        return config

def music_config(*items: str) -> [dict, str]:
    with open('configuration/music_config.yaml', 'r') as f:
        config = yaml.safe_load(f)
        
        for item in items:
            config = config[item]
            
        return config