# -- coding: utf-8 --`
from stable_diffusion_engine import StableDiffusionEngine
from message_types import RequestImageGenFromPrompt, message_parser
from diffusers import LMSDiscreteScheduler, PNDMScheduler
import numpy as np
import cv2
import boto3
from dataclasses import dataclass
import os
import logging

s3_client = boto3.client("s3")
bucket = os.environ["S3_BUCKET"]
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


@dataclass
class StableDiffusionArguments:
    prompt: str
    num_inference_steps: int
    guidance_scale: float
    models_dir: str
    seed: int = None
    init_image: str = None
    beta_start: float = 0.00085
    beta_end: float = 0.012
    beta_schedule: str = "scaled_linear"
    model: str = "bes-dev/stable-diffusion-v1-4-openvino"
    mask: str = None
    strength: float = 0.5
    eta: float = 0.0
    tokenizer: str = "openai/clip-vit-large-patch14"


def run_sd(args: StableDiffusionArguments):
    if args.seed is not None:
        np.random.seed(args.seed)
    if args.init_image is None:
        scheduler = LMSDiscreteScheduler(
            beta_start=args.beta_start,
            beta_end=args.beta_end,
            beta_schedule=args.beta_schedule,
            tensor_format="np",
        )
    else:
        scheduler = PNDMScheduler(
            beta_start=args.beta_start,
            beta_end=args.beta_end,
            beta_schedule=args.beta_schedule,
            skip_prk_steps=True,
            tensor_format="np",
        )
    engine = StableDiffusionEngine(
        model=args.model, scheduler=scheduler, tokenizer=args.tokenizer, models_dir=args.models_dir
    )
    image = engine(
        prompt=args.prompt,
        init_image=None if args.init_image is None else cv2.imread(
            args.init_image),
        mask=None if args.mask is None else cv2.imread(args.mask, 0),
        strength=args.strength,
        num_inference_steps=args.num_inference_steps,
        guidance_scale=args.guidance_scale,
        eta=args.eta,
    )
    is_success, im_buf_arr = cv2.imencode(".jpg", image)
    if not is_success:
        raise ValueError("Failed to encode image as JPG")
    byte_im = im_buf_arr.tobytes()
    return byte_im


def handler(event, context, models_dir=None):
    logger.info("Event :%s", event)

    records = event["Records"]
    first = records[0]
    body = first["body"]
    logger.info("Body :%s", body)
    parsed, type_, error_message = message_parser(body)
    if error_message:
        logger.error("Error: %s", error_message)

    logger.info("Parsed: %s", parsed)
    if type_ != RequestImageGenFromPrompt:
        return {"statusCode": 400, "body": "Failed to parse message!"}

    prompt = parsed.prompt

    seed = None
    num_inference_steps = 32
    guidance_scale = 7.5

    # These are not read yet, using default values instead
    try:
        seed = parsed.seed
    except AttributeError:
        pass

    try:
        num_inference_steps = parsed.num_inference_steps
    except AttributeError:
        pass

    try:
        guidance_scale = parsed.guidance_scale
    except AttributeError:
        pass

    args = StableDiffusionArguments(
        prompt=prompt,
        seed=seed,
        num_inference_steps=num_inference_steps,
        guidance_scale=guidance_scale,
        models_dir=models_dir
    )
    logger.info("Calling Stable Diffusion Engine with args: %s", args)
    image = run_sd(args)
    logger.info("Image is generated, uploading to S3 bucket...")
    # Upload to S3
    response = s3_client.put_object(
        Bucket=bucket,
        Key=parsed.s3_url,
        Body=image,
    )
    logger.info("Response: %s", response)
    logger.info("Image is probably uploaded to S3 bucket.")
    return {"statusCode": 200, "body": body}
