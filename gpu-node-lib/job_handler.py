
import logging

import requests
from gpu_node_lib.dataclasses import RequestImageGenFromPrompt
from gpu_node_lib.logger import setup_logger

logger = setup_logger()


class JobHandler:
    def __init__(self, gpu_client):
        self.gpu_client = gpu_client

    def handle_job(self, request: RequestImageGenFromPrompt) -> bool:
        if type(request) == RequestImageGenFromPrompt:
            generated_image_filepath = self.gpu_client.gen_image_from_prompt(
                request.request_id,
                request.prompt
            )
            if generated_image_filepath.split("/")[-1].split(".jpg")[0] != request.request_id:
                raise TypeError(
                    f"Generated filename {generated_image_filepath} name does not match {request.request_id}. Results are probably inconsistent, aborting.")

            logger.info("Opening file...")
            # Demonstrate how another Python program can use the presigned URL to upload a file
            with open(generated_image_filepath, 'rb') as f:
                files = {'file': (generated_image_filepath, f)}
                logger.info(
                    "Uploading to S3 through presigned URL: %s", request.s3_url[0:32])
                http_response = requests.post(
                    request.s3_url, data=request.s3_fields, files=files)
            # If successful, returns HTTP status code 204
            logging.info(
                f'File upload HTTP status code: {http_response.status_code}')
            return http_response.status_code == 204
        return False
