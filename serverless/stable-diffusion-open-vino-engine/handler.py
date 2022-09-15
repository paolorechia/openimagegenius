import json

# -- coding: utf-8 --`
import argparse
from operator import is_
import os

# engine
from stable_diffusion_engine import StableDiffusionEngine

# scheduler
from diffusers import LMSDiscreteScheduler, PNDMScheduler

# utils
import cv2
import numpy as np
from dataclasses import dataclass
from PIL import Image, ImageEnhance


@dataclass
class StableDiffusionArguments:
    prompt: str
    num_inference_steps: int
    guidance_scale: float
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
        model=args.model, scheduler=scheduler, tokenizer=args.tokenizer
    )
    image = engine(
        prompt=args.prompt,
        init_image=None if args.init_image is None else cv2.imread(args.init_image),
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


def handler(event, context):
    # Get args
    # randomizer params
    body = json.loads(event.get("body"))
    prompt = body["prompt"]
    seed = body.get("seed")
    num_inference_steps: int = int(body.get("num_inference_steps", 32))
    guidance_scale: float = float(body.get("guidance_scale", 7.5))
    args = StableDiffusionArguments(
        prompt=prompt,
        seed=seed,
        num_inference_steps=num_inference_steps,
        guidance_scale=guidance_scale,
    )
    image = run_sd(args)
    body = json.dumps({"message": "wow, no way", "image": image.decode("latin1")})
    return {"statusCode": 200, "body": body}
