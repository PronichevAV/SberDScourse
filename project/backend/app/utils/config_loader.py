import yaml

CONFIG_PATH = 'configs/config.yml'


class ConfigLoader:
    def __init__(self, config_path: str = CONFIG_PATH):
        with open(config_path) as file:
            self.config = yaml.safe_load(file)

    @property
    def need_db_update(self):
        return self.config['update_data']

    @property
    def db_path(self):
        return self.config['db_path']

    @property
    def model_path(self):
        return self.config['model_path']

    @property
    def flask_app_secret_key(self):
        return self.config['flask_app_secret_key']