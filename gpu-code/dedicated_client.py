import argparse
from time import sleep

import asyncio
import warnings

import websockets

from gpu_node_lib.websockets import WebsocketsClient, message_parser
from gpu_node_lib.logger import setup_logger
from gpu_node_lib.config import Config
from gpu_node_lib.stable_diffusion import HuggingGPU
from gpu_node_lib.job_handler import JobHandler

logger = setup_logger()


async def main(stage):
    config = Config(stage=stage)

    logger.setLevel(config.user_config.log_level)
    logger.info("Loading GPU client...")
    gpu_client = HuggingGPU(config.hugging_face_token)

    logger.info("Starting Job Handler...")
    job_handler = JobHandler(gpu_client)
    error_count = 0

    while True:
        logger.info("Connecting to WS Gateway...")
        try:
            async with websockets.connect(
                config.ws_endpoint,
                extra_headers={
                    "Authorization": config.token
                }
            ) as ws:
                ws_client = WebsocketsClient(ws)
                logger.info("Starting WS Client...")
                logger.info("Sending ready state...")
                await ws_client.send_ready_state(vram=config.user_config.vram)
                logger.info("Ready! Waiting for message...")

                async for message in ws:
                    logger.info("Received message: %s", message)
                    parsed, type_, error_message = message_parser(message)
                    if error_message:
                        logger.error(
                            "Failed to parse message: %s", error_message)
                        await ws_client.send_error_message(error_message)

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
                    logger.info("Sending ready state...")
                    logger.info("Ready! Waiting for message...")
        except (websockets.exceptions.ConnectionClosedError, asyncio.exceptions.IncompleteReadError) as excp:
            print(excp)
        logger.info("Connection dropped? Reconnecting...")
        sleep(1.0)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--stage', dest='stage', type=str, default="dev",
                        help='environment to connect to')
    args = parser.parse_args()
    print("Using stage ", args.stage)
    asyncio.run(main(args.stage))
