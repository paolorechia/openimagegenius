import os

LIB_DIR = os.environ["LIB_DIR"]
MODELS_DIR = os.environ["MODELS_DIR"]

print("Using lib dir", LIB_DIR)
print("Using models dir", MODELS_DIR)

# Let's see if the import works :)

def handler(event, context):
    lib_files = os.listdir(LIB_DIR)
    print("Found these files", lib_files)

    model_files = os.listdir(MODELS_DIR)
    print("Found these files", model_files)

    import sys
    sys.path.append(LIB_DIR)  # nopep8 # noqa

    print("Trying to import libraries")
    # engine
    from stable_diffusion_engine import StableDiffusionEngine
    # scheduler
    from diffusers import LMSDiscreteScheduler, PNDMScheduler
    # utils
    import cv2
    import numpy as np

    def main(args):
        if args.seed is not None:
            np.random.seed(args.seed)
        if args.init_image is None:
            scheduler = LMSDiscreteScheduler(
                beta_start=args.beta_start,
                beta_end=args.beta_end,
                beta_schedule=args.beta_schedule,
                tensor_format="np"
            )
        else:
            scheduler = PNDMScheduler(
                beta_start=args.beta_start,
                beta_end=args.beta_end,
                beta_schedule=args.beta_schedule,
                skip_prk_steps = True,
                tensor_format="np"
            )
        engine = StableDiffusionEngine(
            model = args.model,
            scheduler = scheduler,
            tokenizer = args.tokenizer
        )
        image = engine(
            prompt = args.prompt,
            init_image = None if args.init_image is None else cv2.imread(args.init_image),
            mask = None if args.mask is None else cv2.imread(args.mask, 0),
            strength = args.strength,
            num_inference_steps = args.num_inference_steps,
            guidance_scale = args.guidance_scale,
            eta = args.eta
        )
        cv2.imwrite(args.output, image)


