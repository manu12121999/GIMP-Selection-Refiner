#!/usr/bin/env bash
chmod +x selection_refiner.py
python3 -m venv gimpenv
source gimpenv/bin/activate

# for CPU:
# echo "installing for CPU" && python3 -m pip install torch==2.5 torchvision --index-url https://download.pytorch.org/whl/cpu

# for GPU:
echo "installing for GPU" && python3 -m pip install torch torchvision

python3 -m pip install git+https://github.com/facebookresearch/segment-anything.git
deactivate

# Download SAM (base)
wget https://dl.fbaipublicfiles.com/segment_anything/sam_vit_l_0b3195.pth
# (base) https://dl.fbaipublicfiles.com/segment_anything/sam_vit_b_01ec64.pth 
# (large) https://dl.fbaipublicfiles.com/segment_anything/sam_vit_l_0b3195.pth
# (huge) https://dl.fbaipublicfiles.com/segment_anything/sam_vit_h_4b8939.pth

# CHECK IF THE FOLDER NAMES ARE CORRECT
SCRIPT_PATH="$(realpath "$0")"

# Get the parent and grandparent folder names
PARENT_DIR=$(basename "$(dirname "$SCRIPT_PATH")")
GRANDPARENT_DIR=$(basename "$(dirname "$(dirname "$SCRIPT_PATH")")")

# Check if the folder names match
if [[ "$PARENT_DIR" != "gimp-sam" ]]; then
    echo "CHECK YOUR PATHS: THE .PY FILE SHOULD BE PLACED IN A FOLDER OF THE SAME NAME, e.g. 'background-remover.py' inside 'background-remover'."
fi

if [[ "$GRANDPARENT_DIR" != "plug-ins" ]]; then
    echo "THE GRANDPARENT FOLDER OF THE SCRIPT SHOULD BE 'plug-ins'. FOUND: $GRANDPARENT_DIR"
fi