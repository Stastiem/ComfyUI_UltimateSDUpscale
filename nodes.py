# ComfyUI Node for Ultimate SD Upscale by Coyote-A: https://github.com/Coyote-A/ultimate-upscale-for-automatic1111

import os
import sys
import comfy
from .repositories import ultimate_upscale as ult
from .utils import tensor_to_pil, pil_to_tensor
from modules.processing import StableDiffusionProcessing
import modules.shared as shared
from modules.upscaler import UpscalerData
sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.realpath(__file__)), "comfy"))


MAX_RESOLUTION = 8192
# The modes avaiable for Ultimate SD Upscale
MODES = {
    "Linear": ult.USDUMode.LINEAR,
    "Chess": ult.USDUMode.CHESS,
    "None": ult.USDUMode.NONE,
}


class UltimateSDUpscale:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                # Sampling Params
                "model": ("MODEL",),
                "positive": ("CONDITIONING",),
                "negative": ("CONDITIONING",),
                "vae": ("VAE",),
                "upscale_by": ("FLOAT", {"default": 2, "min": 0.05, "max": 4, "step": 0.05}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
                "steps": ("INT", {"default": 20, "min": 1, "max": 10000, "step": 1}),
                "cfg": ("FLOAT", {"default": 8.0, "min": 0.0, "max": 100.0}),
                "sampler_name": (comfy.samplers.KSampler.SAMPLERS,),
                "scheduler": (comfy.samplers.KSampler.SCHEDULERS,),
                "denoise": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.01}),
                # Upscale Params
                "upscale_model": ("UPSCALE_MODEL",),
                "mode_type": (list(MODES.keys()),),
                "tile_width": ("INT", {"default": 512, "min": 64, "max": MAX_RESOLUTION, "step": 64}),
                "tile_height": ("INT", {"default": 512, "min": 64, "max": MAX_RESOLUTION, "step": 64}),
                "mask_blur": ("INT", {"default": 8, "min": 0, "max": 64, "step": 1}),
                "tile_padding": ("INT", {"default": 32, "min": 0, "max": 128, "step": 1}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "upscale"
    CATEGORY = "image/upscaling"

    def upscale(self, image, model, positive, negative, vae, upscale_by, seed,
                steps, cfg, sampler_name, scheduler, denoise, upscale_model,
                mode_type, tile_width, tile_height, mask_blur, tile_padding):
        #
        # Set up A1111 patches
        #

        # Upscaler
        # An object that the script works with
        shared.sd_upscalers[0] = UpscalerData()
        # Where the actual upscaler is stored, will be used when the script upscales using the Upscaler in UpscalerData
        shared.actual_upscaler = upscale_model
        # Reset the resulting image
        shared.tiled_image = None

        # Processing
        sdprocessing = StableDiffusionProcessing(tensor_to_pil(image),
                                                 model, positive, negative, vae,
                                                 seed, steps, cfg, sampler_name,
                                                 scheduler, denoise)

        # Test
        from modules.processing import test_save
        test_save(tensor_to_pil(image), "init")

        #
        # Running the script
        #
        script = ult.Script()
        processed = script.run(p=sdprocessing, _=None, tile_width=tile_width, tile_height=tile_height, mask_blur=mask_blur,
                               padding=tile_padding, seams_fix_width=None, seams_fix_denoise=None, seams_fix_padding=None,
                               upscaler_index=0, save_upscaled_image=False, redraw_mode=MODES[mode_type], save_seams_fix_image=False,
                               seams_fix_mask_blur=None, seams_fix_type=ult.USDUSFMode.NONE, target_size_type=2, custom_width=None,
                               custom_height=None, custom_scale=upscale_by)

        # Return the resulting image
        upscaled_image = pil_to_tensor(processed.images[0])
        return (upscaled_image,)


# A dictionary that contains all nodes you want to export with their names
# NOTE: names should be globally unique
NODE_CLASS_MAPPINGS = {
    "UltimateSDUpscale": UltimateSDUpscale
}

# A dictionary that contains the friendly/humanly readable titles for the nodes
NODE_DISPLAY_NAME_MAPPINGS = {
    "UltimateSDUpscale": "Ultimate SD Upscale"
}