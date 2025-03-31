@echo off


echo please wait ...


python -m venv gimpenv
call gimpenv\Scripts\activate.bat

python -m pip install --upgrade pip

echo "installing for CPU"
python -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu

python -m pip install git+https://github.com/facebookresearch/segment-anything.git


deactivate

curl.exe -L -o sam_vit_b_01ec64.pth https://dl.fbaipublicfiles.com/segment_anything/sam_vit_b_01ec64.pth


echo Virtual environment setup complete!
