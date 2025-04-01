#!/usr/bin/env bash

chmod u+x selection_refiner.py

uv init
uv venv
ln -s .venv gimpenv

# Dependencies for CPU:
# echo "installing for CPU" && uv add torch torchvision --index-url https://download.pytorch.org/whl/cpu

# Dependencies for GPU:
echo "installing for GPU" && uv add torch torchvision

# SAM1:
#uv add git+https://github.com/facebookresearch/segment-anything.git

# SAM2:
uv add sam2


# Download SAM 1
#wget https://dl.fbaipublicfiles.com/segment_anything/sam_vit_b_01ec64.pth  # (base)
#wget https://dl.fbaipublicfiles.com/segment_anything/sam_vit_l_0b3195.pth  # (large)
#wget https://dl.fbaipublicfiles.com/segment_anything/sam_vit_h_4b8939.pth  # (huge)

# Download SAM 2.1
# small
#wget https://dl.fbaipublicfiles.com/segment_anything_2/092824/sam2.1_hiera_small.pt

# base
wget https://dl.fbaipublicfiles.com/segment_anything_2/092824/sam2.1_hiera_base_plus.pt

#large
#wget https://dl.fbaipublicfiles.com/segment_anything_2/092824/sam2.1_hiera_large.pt





# CHECK IF THE FOLDER NAMES ARE CORRECT
SCRIPT_PATH="$(realpath "$0")"

# Get the parent and grandparent folder names
PARENT_DIR=$(basename "$(dirname "$SCRIPT_PATH")")
GRANDPARENT_DIR=$(basename "$(dirname "$(dirname "$SCRIPT_PATH")")")

# Check if the folder names match
if [[ "$PARENT_DIR" != "selection_refiner" ]]; then
    echo "CHECK YOUR PATHS: THE .PY FILE SHOULD BE PLACED IN A FOLDER OF THE SAME NAME, e.g. 'selection_refiner.py' inside 'selection_refiner/'."
fi

if [[ "$GRANDPARENT_DIR" != "plug-ins" ]]; then
    echo "THE GRANDPARENT FOLDER OF THE SCRIPT SHOULD BE 'plug-ins'. FOUND: $GRANDPARENT_DIR"
fi
