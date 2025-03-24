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

    def get(self, key: str, default=None):
        """获取配置项，支持嵌套键使用点号分隔，如 'window.width'"""
        keys = key.split('.')
        value = self.config
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default

    def set(self, key: str, value):
        """设置配置项，支持嵌套键"""
        keys = key.split('.')
        config = self.config
        for k in keys[:-1]:
            if k not in config or not isinstance(config[k], dict):
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value

    def in_debug(self):
        return self.get('mode') == 'debug'