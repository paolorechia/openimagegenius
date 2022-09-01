from PIL import Image
from torch import autocast
from diffusers import StableDiffusionPipeline
import asyncio
import json
import logging
import os
import sys
import warnings
from dataclasses import dataclass
from multiprocessing import Process, Queue

import boto3
import websockets

MAX_MSG_SIZE = 2048


def setup_logger():
    logger = logging.getLogger()

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s[%(levelname)s]:(%(name)s) - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


logger = setup_logger()


@dataclass
class UserConfig:
    vram: int
    log_level: int = logging.INFO


class Config:
    API_FILENAME = "api_token.json"
    CONFIG_DIR = os.path.join(os.environ["HOME"], ".openimagegenius")
    CONFIG_FILE = "client-config.json"
    HUGGING_FACE_CONFIG_DIR = os.path.join(os.environ["HOME"], ".huggingface")
    HUGGING_FACE_TOKEN_FILENAME = "token"

    def __init__(self) -> None:
        self.stage = "dev"
        self.available_endpoints = {
            "dev": "wss://dev.ws-gpus.openimagegenius.com"
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
        with open(token_filepath, "r") as fp:
            j = json.load(fp)
        return j["api_token"]

    def load_hugging_face_token(self, filepath) -> str:
        # get your token at https://huggingface.co/settings/tokens
        with open(filepath, "r") as fp:
            return fp.read().strip()

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


@ dataclass
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
    def __init__(self, hugging_face_token):
        model_id = "CompVis/stable-diffusion-v1-4"
        output_dir = os.path.join(os.environ["HOME"], ".gpu-node-output")
        prompt_queue = Queue()
        file_queue = Queue()
        readiness_queue = Queue()

        diffusion_loop = Process(
            target=HuggingGPU.launch_diffusion_loop,
            args=(
                model_id,
                hugging_face_token,
                output_dir,
                prompt_queue,
                file_queue,
                readiness_queue
            ))
        self.model_id = model_id
        self.output_dir = output_dir
        self.prompt_queue = prompt_queue
        self.file_queue = file_queue
        self.readiness_queue = readiness_queue
        self.diffusion_loop = diffusion_loop
        self.diffusion_loop.start()

        # Wait until readiness is posted
        init_timeout_in_seconds = 600
        ready = self.readiness_queue.get(
            block=True, timeout=init_timeout_in_seconds)
        if not ready:
            raise RuntimeError(
                f"Diffusion pipeline failed to initialize within {init_timeout_in_seconds} seconds.")

    @staticmethod
    def launch_diffusion_loop(
        model_id,
        hugging_face_token,
        output_dir,
        prompt_queue,
        file_queue,
        readiness_queue,
    ):
        def _image_grid(imgs, rows, cols):
            assert len(imgs) == rows * cols
            w, h = imgs[0].size
            grid = Image.new("RGB", size=(cols * w, rows * h))

            for i, img in enumerate(imgs):
                grid.paste(img, box=(i % cols * w, i // cols * h))
            return grid
        logger = setup_logger()
        logger.info("Launching pipeline with args")
        logger.info("model_id: %s", model_id)
        logger.info("hugging_face_token: %s", hugging_face_token)
        logger.info("output_dir: %s", output_dir)
        logger.info("prompt_queue: %s", prompt_queue)
        logger.info("file_queue: %s", file_queue)
        logger.info("readiness_queue: %s", readiness_queue)

        logger.info("Creating output directory...")

        try:
            os.makedirs(output_dir)
        except FileExistsError:
            pass
        logger.info("Results will be saved to: %s", output_dir)

        logger.info("Launching diffusion pipeline...")
        pipe = StableDiffusionPipeline.from_pretrained(
            model_id, use_auth_token=hugging_face_token
        )
        device = "cuda"
        pipe = pipe.to(device)

        with autocast(device):
            input_prompt = ""
            logger.info("Signaling that pipelien is ready...")
            readiness_queue.put(True, block=True)
            logger.info("Starting main diffusion loop...")
            while True:
                logger.info("Fetching request from queue...")
                request_id, input_prompt, num_images, num_inference_steps, guidance_scale = prompt_queue.get(
                    block=True)
                logger.info("Got request: %s (%s)", input_prompt, request_id)
                prompt = [input_prompt] * num_images
                images = pipe(prompt, num_inference_steps=num_inference_steps,
                              guidance_scale=guidance_scale)["sample"]
                logger.info("Processed request: %s (%s)",
                            input_prompt, request_id)

                grid = _image_grid(images, rows=1, cols=num_images)
                filename = f"{request_id}.jpg"

                grid.save(os.path.join(
                    output_dir, filename))
                logger.info("Saved file: %s", filename)
                logger.info("Sending filename through file queue...")
                file_queue.put(filename, block=True)

    def gen_image_from_prompt(self, request_id: str, prompt: str, num_inference_steps=50, guidance_scale=8.0, num_images=1) -> str:
        """Returns filepath where file is saved"""
        logger = setup_logger()
        logger.info("Inserting request into prompt queue: %s %s",
                    (prompt, request_id))
        self.prompt_queue.put(
            (request_id, prompt, num_images,
             num_inference_steps, guidance_scale), block=True,
        )
        return self.file_queue.get(block=True)


class JobHandler:
    def __init__(self, gpu_client):
        self.gpu_client = gpu_client

    def handle_job(self, request: RequestImageGenFromPrompt) -> bool:
        if type(request) == RequestImageGenFromPrompt:
            generated_image_filepath = self.gpu_client.gen_image_from_prompt(
                request.request_id,
                request.prompt
            )
            if generated_image_filepath.split(".jpg")[0] != request.request_id:
                raise TypeError(
                    f"Generated filename {generated_image_filepath} name does not match {request.request_id}. Results are probably inconsistent, aborting.")
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
        gpu_client = HuggingGPU(config.hugging_face_token)
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
