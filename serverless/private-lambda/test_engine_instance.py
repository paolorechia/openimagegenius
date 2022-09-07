from stable_diffusion_engine import StableDiffusionEngine
from diffusers import LMSDiscreteScheduler, PNDMScheduler
import cv2
import numpy as np


lib_dir = "./build"
models_dir = "./models"


def test_instance_works():
    beta_start = 0.00085
    beta_end = 0.012
    beta_schedule = "scaled_linear"
    # diffusion params
    num_inference_steps = 32
    guidance_scale = 7.5
    eta = 0.0
    tokenizer = "openai/clip-vit-large-patch14"
    prompt = "Street-art painting of Emilia Clarke in style of Banksy, photorealism"
    init_image = None
    strength = 0.5
    mask = None
    output = "output.png"

    if init_image is None:
        scheduler = LMSDiscreteScheduler(
            beta_start=beta_start,
            beta_end=beta_end,
            beta_schedule=beta_schedule,
            tensor_format="np"
        )
    else:
        scheduler = PNDMScheduler(
            beta_start=beta_start,
            beta_end=beta_end,
            beta_schedule=beta_schedule,
            skip_prk_steps=True,
            tensor_format="np"
        )
    engine = StableDiffusionEngine(
        scheduler=scheduler,
        models_dir=models_dir
    )
    image = engine(
        prompt = prompt,
        init_image = None if init_image is None else cv2.imread(init_image),
        mask = None if mask is None else cv2.imread(mask, 0),
        strength = strength,
        num_inference_steps = num_inference_steps,
        guidance_scale = guidance_scale,
        eta = eta
    )
    cv2.imwrite(output, image)

test_instance_works()