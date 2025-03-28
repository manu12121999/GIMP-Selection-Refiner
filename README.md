# GIMP-Selection-Refiner
GIMP Plugin to refine a selection using a neural network

![Image](https://github.com/user-attachments/assets/2c0d9aa9-73bc-40bd-adda-a3a42c7a1b7c)



## Made for Gimp3.0. Works only on Linux

## Installation:

### Linux: 
1. Install python

2. Rename the folder to `selection_refiner` and place it in your Gimp Plugins directory.
  To find it, go inside GIMP to `Edit`->`Preferences`->`Folders`->`Plugins`. The folder must be named `selection_refiner`!!!


3. make the python file executable and install dependencies with: 

```
bash ./setup.sh
```

 

## Usage:
1. Select the item roughly (make sure the entire object is in the selection)
2. In the top bar, go to
    `Select` -> `Refine Selection using SAM`

