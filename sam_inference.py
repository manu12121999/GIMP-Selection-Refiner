print("running SAM inference")

from os.path import join
import sys
import numpy as np
#import torch
from PIL import Image

# use SAM 1 for now
from segment_anything import SamPredictor, sam_model_registry
print("done importing, stating to set up model")


if __name__=="__main__":
    
    x1, y1, x2, y2, new_w, new_h, original_w, original_h, baseLoc = sys.argv[1:]
    x1, y1, x2, y2, new_w, new_h, original_w, original_h = map(int, [x1, y1, x2, y2, new_w, new_h, original_w, original_h])

    # set checkpoint
    sam_checkpoint = join(baseLoc, "sam_vit_b_01ec64.pth")
    image = Image.open(join(baseLoc, "rgb.png"))
    im = np.array(image.resize((new_w, new_h)))

    # load SAM
    #device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    SAM_VERSION = 1
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