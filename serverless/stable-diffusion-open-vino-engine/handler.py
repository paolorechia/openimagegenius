# -- coding: utf-8 --`
print("Starting container code...")

from dataclasses import dataclass
import numpy as np
import cv2
from diffusers import LMSDiscreteScheduler, PNDMScheduler
from stable_diffusion_engine import StableDiffusionEngine
import json
import os


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
    print("Getting into handler, event: ", event)

    print("Working dir at handler...", )
    current_dir = os.getcwd()
    print(current_dir)
    print(os.listdir(current_dir))
    print("Listing root")
    print(os.listdir("/"))

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
        models_dir=models_dir
    )
    print("Parsed args:", args)
    image = run_sd(args)
    print("Image generated")
    body = json.dumps(
        {"message": "wow, no way", "image": image.decode("latin1")})
    return {"statusCode": 200, "body": body}
