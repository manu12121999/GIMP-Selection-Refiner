@echo off


echo please wait ...


python -m venv gimpenv
call gimpenv\Scripts\activate.bat

echo Installing dependencies for CPU
python -m pip install --upgrade pip
python -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
python -m pip install sam2

deactivate

echo Downloding SAM2 base
curl.exe -L -o sam2.1_hiera_base_plus.pt https://dl.fbaipublicfiles.com/segment_anything_2/092824/sam2.1_hiera_base_plus.pt


echo Virtual environment setup complete!
