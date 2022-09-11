import asyncio
import warnings
from time import sleep

import websockets

from gpu_node_lib.config import Config
from gpu_node_lib.job_handler import JobHandler
from gpu_node_lib.logger import setup_logger
from gpu_node_lib.stable_diffusion import HuggingGPU
from gpu_node_lib.websockets import WebsocketsClient, message_parser

logger = setup_logger()


async def main():
    logger.info(
        "Loading EXPERIMENTAL client, serves both environments simultaneously!!")
    dev_config = Config(stage="dev")
    prod_config = Config(stage="prod")

    logger.setLevel(dev_config.user_config.log_level)
    logger.info("Loading GPU client...")
    gpu_client = HuggingGPU(dev_config.hugging_face_token)

    logger.info("Starting Job Handler...")
    job_handler = JobHandler(gpu_client)
    error_count = 0

    while True:
        logger.info("Connecting to WS dev Gateway...")
        dev_websocket = await websockets.connect(
            dev_config.ws_endpoint,
            extra_headers={
                "Authorization": dev_config.token
            }
        )
        logger.info("Connecting to WS prod Gateway...")
        prod_websocket = await websockets.connect(
            prod_config.ws_endpoint,
            extra_headers={
                "Authorization": prod_config.token
            }
        )
        logger.info("Starting WS Clients...")
        dev_ws_client = WebsocketsClient(dev_websocket)
        prod_ws_client = WebsocketsClient(prod_websocket)

        logger.info("Sending ready states...")
        await dev_ws_client.send_ready_state(vram=dev_config.user_config.vram)
        await prod_ws_client.send_ready_state(vram=dev_config.user_config.vram)

        logger.info("Ready! Waiting for messages...")
        while True:
            try:
                clients_in_use = []
                prod_message = None
                dev_message = None

                try:
                    prod_message = await asyncio.wait_for(prod_websocket.recv(), timeout=0.1)
                except (asyncio.exceptions.CancelledError, asyncio.exceptions.TimeoutError):
                    pass

                try:
                    dev_message = await asyncio.wait_for(dev_websocket.recv(), timeout=0.1)
                except (asyncio.exceptions.CancelledError, asyncio.exceptions.TimeoutError):
                    pass

                if dev_message:
                    clients_in_use.append(("dev", dev_message, dev_ws_client))
                if prod_message:
                    clients_in_use.append(
                        ("prod", prod_message, prod_ws_client))

                for stage, message, ws_client in clients_in_use:
                    logger.info("Received message: %s", message)
                    logger.info("Stage: %s", stage)
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
                    # logger.info("Sending ready state...")
                    # await ws_client.send_ready_state(vram=dev_config.user_config.vram)
            except (websockets.exceptions.ConnectionClosedError, asyncio.exceptions.IncompleteReadError, websockets.exceptions.ConnectionClosedOK) as excp:
                print(excp)
                logger.info("Connection dropped? Reconnecting...")
                sleep(1.0)
                break

if __name__ == "__main__":
    asyncio.run(main())
