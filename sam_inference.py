print("running SAM inference")
import os
from os.path import join
import sys
import numpy as np
import torch
from PIL import Image


baseLoc = os.path.dirname(os.path.realpath(__file__))

SAM_VERSION = 2
SAM_SIZE = "base"

if SAM_VERSION == 1:
    from segment_anything import SamPredictor, sam_model_registry
elif SAM_VERSION == 2:
    from sam2.build_sam import build_sam2
    from sam2.sam2_image_predictor import SAM2ImagePredictor


# set checkpoint
if SAM_VERSION == 1:
    sam_checkpoint = join(baseLoc, "sam_vit_l_0b3195.pth")
elif SAM_VERSION == 2:
    if SAM_SIZE == "small":
        sam_cfg = "configs/sam2.1/sam2.1_hiera_s.yaml"
        sam_checkpoint = join(baseLoc, "sam2.1_hiera_small.pt")
    elif SAM_SIZE == "large":
        sam_cfg = "configs/sam2.1/sam2.1_hiera_l.yaml"
        sam_checkpoint = join(baseLoc, "sam2.1_hiera_large.pt")
    else: # base
        sam_cfg = "configs/sam2.1/sam2.1_hiera_b+.yaml"
        sam_checkpoint = join(baseLoc, "sam2.1_hiera_base_plus.pt")


if __name__=="__main__":
    
    x1, y1, x2, y2, new_w, new_h, original_w, original_h = sys.argv[1:]
    x1, y1, x2, y2, new_w, new_h, original_w, original_h = map(int, [x1, y1, x2, y2, new_w, new_h, original_w, original_h])

    image = Image.open(join(baseLoc, "rgb.png"))
    im = np.array(image.resize((new_w, new_h)))

    # load SAM
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    if SAM_VERSION == 1:
        sam = sam_model_registry["vit_b"](checkpoint=sam_checkpoint)
        #sam.to(device=device)
        predictor = SamPredictor(sam)
    elif SAM_VERSION == 2:
        sam2_model = build_sam2(sam_cfg, sam_checkpoint, device=device)
        predictor = SAM2ImagePredictor(sam2_model)
    print("done setting up model, starting inference...")
    
    predictor.set_image(im)

    # sam prediction
    bounds = np.array([x1, y1 , x2, y2])
    masks, _, _ = predictor.predict(box=bounds, multimask_output=False)

    mask_rgba = np.zeros((masks[0].shape[0], masks[0].shape[1], 4), dtype=np.uint8)
    mask_rgba[masks[0] == 1] = [255, 255, 255, 255]  # White with full opacity

    Image.fromarray(mask_rgba).resize((original_w, original_h)).save(join(baseLoc,"mask.png"))
    print("done with inference")