import os
from multiprocessing import Process, Queue

from diffusers import StableDiffusionPipeline
from gpu_node_lib.logger import setup_logger
from PIL import Image
from torch import autocast

logger = setup_logger()


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
            logger.info("Signaling that pipeline is ready...")
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

                filepath = os.path.join(output_dir, filename)
                grid.save(filepath)
                logger.info("Saved file: %s", filename)
                logger.info("Sending filename through file queue...")
                file_queue.put(filepath, block=True)

    def gen_image_from_prompt(self, request_id: str, prompt: str, num_inference_steps=50, guidance_scale=8.0, num_images=1) -> str:
        """Returns filepath where file is saved"""
        logger.info("Inserting request into prompt queue: %s %s",
                    prompt, request_id)
        self.prompt_queue.put(
            (request_id, prompt, num_images,
             num_inference_steps, guidance_scale), block=True,
        )
        return self.file_queue.get(block=True)
