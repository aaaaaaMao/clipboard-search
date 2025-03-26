import os
import json

class ConfigManager:

    def __init__(self):
        self.cwd = os.getcwd()

        self.config = {}
        self._style_sheet_cache = {}

        self.load_config()

    def load_config(self):
        for file_name in ['config.default.json', 'config.local.json']:
            file_path = os.path.join(self.cwd, 'configs', file_name)
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf8') as f:
                    try:
                        config = json.load(f)
                        if config:
                            self.config.update(config)
                    except Exception as e:
                        pass

        self._cache_dictionary_style_sheet()

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
        return self.get('env') == 'debug'
    
    def get_icon_path(self, icon_name: str):
        if not self.get(icon_name):
            return None
        return os.path.join(self.cwd, 'resources/images', self.get(icon_name))
    
    def list_dictionaries(self):
        return self.get('dictionaries')
    
    def get_dictionary_path(self, dictionary_name: str, ext='.db'):
        return os.path.join(self.cwd, 'resources/dictionaries', f'{dictionary_name}{ext}')
    
    def _cache_dictionary_style_sheet(self):
        for item in self.list_dictionaries():
            if item.get('search') and item.get('style_sheet'):
                file_path = os.path.join(self.cwd, 'resources/dictionaries', item['style_sheet'])
                if os.path.exists(file_path):
                    with open(file_path, 'r', encoding='utf8') as f:
                        self._style_sheet_cache[item['name']] = f.read()

    def get_dictionary_style_sheet(self, dictionary_name: str):
        return self._style_sheet_cache.get(dictionary_name)
    
    def hujiang_enabled(self):
        return self.get('hujiang.enabled') and self.get('hujiang.req_url') \
                and self.get('hujiang.req_headers')