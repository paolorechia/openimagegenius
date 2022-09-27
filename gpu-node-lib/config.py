import json
import os
import sys
import warnings

from gpu_node_lib.dataclasses import UserConfig


class Config:
    API_FILENAME = "api_token.json"
    CONFIG_DIR = os.path.join(os.environ["HOME"], ".openimagegenius")
    CONFIG_FILE = "client-config.json"
    HUGGING_FACE_CONFIG_DIR = os.path.join(os.environ["HOME"], ".huggingface")
    HUGGING_FACE_TOKEN_FILENAME = "token"

    def __init__(self, stage) -> None:
        self.stage = stage
        self.available_endpoints = {
            "dev": "wss://dev.ws-gpus.openimagegenius.com",
            "prod": "wss://ws-gpus.openimagegenius.com"
        }
        self.ws_endpoint = self.available_endpoints[self.stage]
        token_filepath = os.path.join(Config.CONFIG_DIR, Config.API_FILENAME)
        hugging_face_token_filepath = os.path.join(
            Config.HUGGING_FACE_CONFIG_DIR, "token")

        try:
            self.token = self.load_api_token(token_filepath)
        except FileNotFoundError:
            sys.exit(
                f"API key not found. Please create a file with it at {token_filepath}")
        try:
            self.hugging_face_token = self.load_hugging_face_token(
                hugging_face_token_filepath)
        except FileNotFoundError:
            sys.exit(
                f"Huggingface token not found. Please create a file with it at {hugging_face_token_filepath}."
            )
        self.user_config: UserConfig = self.load_config()

    def load_api_token(self, token_filepath) -> str:
        """
        Loads the api token from a json file.

        :param token_filepath: The path to the json file containing the api token.
        :type token_filepath: str
        :return: The api token.
        :rtype: str
        :raises FileNotFoundError: If the file does not exist.
        :raises KeyError: If the json file does not contain the api token.
        """
        with open(token_filepath, "r") as fp:
            j = json.load(fp)
        return j["api_token"]

    def load_hugging_face_token(self, filepath) -> str:
        """
        Load a Hugging Face token from a file.

        :param filepath: The path to the file containing the token.
        :type filepath: str
        :raises FileNotFoundError: If the file does not exist.
        :return: The token.
        :rtype: str
        """
        # get your token at https://huggingface.co/settings/tokens
        with open(filepath, "r") as fp:
            return fp.read().strip()


    def load_config(self) -> UserConfig:
        """
        Loads a config file from the config directory.
        :return: A UserConfig object.
        :raises KeyError: If the config file is malformed.
        """
        config_filepath = os.path.join(Config.CONFIG_DIR, Config.CONFIG_FILE)
        try:
            with open(config_filepath, "r") as fp:
                config = json.load(fp)
                # Check that some keys exist
                config["vram"]
                return UserConfig(**config)
        except FileNotFoundError:
            warnings.warn(
                f"Could not find config file {config_filepath}. Using default settings (not recommended)")
        except KeyError as excp:
            warnings.warn(f"Did not find key {(str(excp))} in config file")
            warnings.warn(
                f"Malformed config file, using default settings (not recommended)")
        return UserConfig(vram=12)
