import asyncio
import json
import logging
import os
import sys
import warnings
from concurrent.futures.process import _threads_wakeups
from dataclasses import dataclass

import boto3
import websockets

MAX_MSG_SIZE = 2048

logger = logging.getLogger(__name__)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


@dataclass
class UserConfig:
    vram: int
    log_level: int = logging.INFO


class Config:
    API_FILENAME = "api_token.json"
    CONFIG_DIR = os.path.join(os.environ["HOME"], ".openimagegenius")
    CONFIG_FILE = "client-config.json"

    def __init__(self) -> None:
        self.stage = "dev"
        self.available_endpoints = {
            "dev": "wss://dev.ws-gpus.openimagegenius.com"
        }
        self.ws_endpoint = self.available_endpoints[self.stage]
        try:
            self.token = self.load_api_token()
        except FileNotFoundError:
            sys.exit(
                f"Please setup your {Config.API_FILENAME} in your home directory.")
        self.user_config: UserConfig = self.load_config()

    def load_api_token(self) -> str:
        token_filepath = os.path.join(Config.CONFIG_DIR, Config.API_FILENAME)
        with open(token_filepath, "r") as fp:
            j = json.load(fp)
        return j["api_token"]

    def load_config(self) -> UserConfig:
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


class WebsocketsClient:
    def __init__(self, ws_connection):
        self.ws_connection = ws_connection

    async def send_ready_state(self, vram):
        return await self.ws_connection.send(json.dumps({
            "message_type": "status",
            "data": {
                "status": "ready",
                "vram_in_gigabytes": vram,
            }
        }))

    async def send_ack_message(self):
        return await self.ws_connection.send(json.dumps({
            "message_type": "acknowledge",
        }))

    async def send_error_message(self, error_message):
        return await self.ws_connection.send(json.dumps({
            "message_type": "error",
            "data": error_message
        }))

    async def send_job_completed(self, request_id):
        return await self.ws_connection.send(json.dumps({
            "message_type": "job_completed",
            "data": request_id
        }))

    async def send_job_failed(self, request_id):
        return await self.ws_connection.send(json.dumps({
            "message_type": "job_failed",
            "data": request_id
        }))


@dataclass
class RequestImageGenFromPrompt:
    request_id: str
    prompt: str
    s3_presigned_url: str


def message_parser(message: str):
    # Returns tuple parsed, type_, error_message
    type_ = None
    parsed = None

    if message is None:
        return None, None, "Empty message received"

    if type(message) != str:
        return None, type(message), "Non string message"

    if len(message) > MAX_MSG_SIZE:
        return None, type(message), "Message exceeds size limit"

    try:
        parsed = json.loads(message)
    except json.JSONDecodeError as excp:
        return None, type(excp), "Message is not JSON encoded"

    try:
        message_type = parsed["message_type"]
    except KeyError as excp:
        return None, type(excp), "key 'message_type' missing in JSON"

    # Parse specific message types
    try:
        if message_type == "request_prompt":
            data = parsed["data"]
            prompt = data["prompt"]
            s3_presigned_url = data["s3_presigned_url"]
            request_id = data["request_id"]
            return RequestImageGenFromPrompt(
                request_id,
                prompt,
                s3_presigned_url
            ), RequestImageGenFromPrompt, None

        elif message_type == "heartbeat":
            pass
    except KeyError as excp:
        return None, type(excp), f"key missing in JSON: {str(excp)}"

    return None, None, ValueError(f"Unrecognized message_type: {message_type}")


class HuggingGPU:
    def __init__(self):
        # Load model here etc
        # TODO: insert actual implementation
        pass

    def gen_image_from_prompt(prompt: str) -> str:
        """Returns filepath where file is saved"""
        # TODO: insert actual implementation


class JobHandler:
    def __init__(self, gpu_client):
        self.gpu_client = gpu_client

    def handle_job(self, request: RequestImageGenFromPrompt) -> bool:
        if type(request) == RequestImageGenFromPrompt:
            generated_image = self.gpu_client(request.prompt)
            # with open(generated_image, "rb"):
            # TODO: upload to boto3 here
            # url = "stub"
            return True
        return False


async def main():
    config = Config()
    logger.setLevel(config.user_config.log_level)

    logger.info("Connecting to WS Gateway...")
    async with websockets.connect(
        config.ws_endpoint,
        extra_headers={
            "Authorization": config.token
        }
    ) as ws:
        logger.info("Loading GPU client...")
        gpu_client = HuggingGPU()
        logger.info("Starting Job Handler...")
        job_handler = JobHandler(gpu_client)
        logger.info("Starting WS Client...")
        ws_client = WebsocketsClient(ws)
        error_count = 0
        logger.info("Sending ready state...")
        await ws_client.send_ready_state(vram=config.user_config.vram)
        logger.info("Awaiting ACK...")
        await ws.recv()
        logger.info("Ready!")
        logger.info("Waiting for message...")
        async for message in ws:
            parsed, type_, error_message = message_parser(message)
            if error_message:
                await ws_client.send_error_message(error_message)
            else:
                await ws_client.send_ack_message()
                request_id = parsed.request_id
                is_success = False
                try:
                    is_success = job_handler.handle_job(parsed)
                except Exception as excp:
                    warnings.warn(f"Job failed: {str(excp)}")
                if is_success:
                    await ws_client.send_job_completed(request_id)
                else:
                    await ws_client.send_job_failed(request_id)
                    error_count += 1


if __name__ == "__main__":
    asyncio.run(main())
