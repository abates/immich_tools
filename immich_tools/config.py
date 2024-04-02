from os import path

import platformdirs

from pydantic import BaseModel, HttpUrl
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)

APP_NAME = __name__.split(".")[0]
CONFIG_DIR = platformdirs.user_config_dir(APP_NAME, ensure_exists=True)

CONFIG_FILE = path.join(CONFIG_DIR, "config.json")
class Server(BaseModel):
    api_key: str
    endpoint: HttpUrl

class Settings(BaseSettings):
    model_config = SettingsConfigDict(json_file=CONFIG_FILE)
    server: Server

    @classmethod
    def load(cls):
        while not path.exists(CONFIG_FILE):
            print("It seems that you haven't used immich-tools before, let's setup your configuration.")
            url = input("Input the URL to the Immich API:")
            key = input("Input the Immich API key:")
            try:
                settings = Settings(server=Server(endpoint=url, api_key=key))
                with open(CONFIG_FILE, "w") as output_file:
                    output_file.write(settings.model_dump_json(indent=4))
            except ValueError as ex:
                for error in ex.errors():
                    print(error["msg"])

        with open(CONFIG_FILE) as input_file:
            return Settings.model_validate_json(input_file.read())

