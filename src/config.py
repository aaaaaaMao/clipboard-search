import os
import json

class ConfigManager:

    def __init__(self):
        self.config = {}
        self.load_config()

    def load_config(self):
        cwd = os.getcwd()

        for file_name in ['config.default.json', 'config.local.json']:
            file_path = os.path.join(cwd, 'configs', file_name)
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf8') as f:
                    try:
                        config = json.load(f)
                        if config:
                            self.config.update(config)
                    except Exception as e:
                        pass
        
        for field in ['icon', 'floating_icon']:
            if self.config[field]:
                self.config[f'{field}_path'] = os.path.join(cwd, 'resources/images', self.config[field])