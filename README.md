# GIMP-Selection-Refiner
GIMP Plugin to refine a selection using the neural network segment-anything2

![Image](https://github.com/user-attachments/assets/5cd938df-5dc3-40b1-87e2-4649a9401c07)


## Made for Gimp 3.0.

## Installation:

### Linux:

1. Install python

2. Rename the folder to `selection_refiner` and place it in your Gimp Plugins directory.
  To find it, go inside GIMP to `Edit`->`Preferences`->`Folders`->`Plugins`. The folder must be named `selection_refiner`!!!


3. make the python file executable, install dependencies and download model files with: 

```
bash ./setup.sh
```

### Windows:

1. Install python

2. Rename the folder to `selection_refiner` and place it in your Gimp Plugins directory.
  To find it, go inside GIMP to `Edit`->`Preferences`->`Folders`->`Plugins`. The folder must be named `selection_refiner`!!!


3. install dependencies and download model files by double clicking

```
setup.bat
```
 


## Usage:
1. Select the item roughly (make sure the entire object is in the selection)
2. In the top bar, go to
    `Select` -> `Refine Selection using SAM`


## Notes:
There are 4 different segment-anything-2 models, [`tiny`, `small`, `base`, `large`]. At the moment, `base` is used. If you want better quality or better speed, another one can be used. For this, uncomment the corresponding wget line in `setup.sh` 
e.g. 
```
#wget https://dl.fbaipublicfiles.com/segment_anything_2/092824/sam2.1_hiera_large.pt
```
to 
```
wget https://dl.fbaipublicfiles.com/segment_anything_2/092824/sam2.1_hiera_large.pt
```


and change line 28 in `selection_refiner.py` from 
```
SAM_SIZE = "base"
```
to e.g.  
```
SAM_SIZE = "large"
```