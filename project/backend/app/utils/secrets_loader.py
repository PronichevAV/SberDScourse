import yaml

SECRETS_PATH = 'configs/secrets.yml'


class SecretsLoader:
    def __init__(self, secrets_path: str = SECRETS_PATH):
        with open(secrets_path) as file:
            self.config = yaml.safe_load(file)

    @property
    def flask_app_secret_key(self):
        return self.config['flask_app_secret_key']
