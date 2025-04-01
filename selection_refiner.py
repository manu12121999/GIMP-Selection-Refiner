#!/usr/bin/env python3
import os
from os.path import join
import sys
import subprocess
import platform


# This Plugin is only for GIMP Version >= 3.0.0 and windows
import gi
gi.require_version('Gimp', '3.0')
from gi.repository import Gimp
gi.require_version('GimpUi', '3.0')
from gi.repository import GimpUi
from gi.repository import GObject
from gi.repository import GLib
from gi.repository import Gegl
from gi.repository import Gio

current_platform = platform.system().lower()
baseLoc = os.path.dirname(os.path.realpath(__file__))


if current_platform != "windows":
    for version in range(6,20):
        sys.path.extend([join(baseLoc,f'gimpenv/lib/python3.{version}'), 
                         join(baseLoc,f'gimpenv/lib/python3.{version}/site-packages'), 
                         join(baseLoc,f'gimpenv/lib/python3.{version}/site-packages/setuptools')])
    sys.path.extend([join(baseLoc,'gimpenv/Lib'), join(baseLoc,'gimpenv/Lib/site-packages'), join(baseLoc,'gimpenv/Lib/site-packages/setuptools')])
    sys.path.extend([baseLoc])


    import numpy as np
    import torch
    from PIL import Image

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




class SelectionRefinerSAM(Gimp.PlugIn):

    ## GimpPlugIn virtual methods ##
    def do_query_procedures(self):
        procedure = 'python-plugin-selection-refiner-sam-win' if current_platform == "windows" else 'python-plugin-selection-refiner-sam'
        return [procedure ]


    def do_create_procedure(self, name):
        self.mode = "select"
        procedure = None
        
        if name == 'python-plugin-selection-refiner-sam-win':
            procedure = Gimp.ImageProcedure.new(self, name,
                                                Gimp.PDBProcType.PLUGIN,
                                                self.refine_selection_win, None)
        else:
            procedure = Gimp.ImageProcedure.new(self, name,
                                    Gimp.PDBProcType.PLUGIN,
                                    self.refine_selection, None)
            
        procedure.set_sensitivity_mask(Gimp.ProcedureSensitivityMask.ALWAYS)

        procedure.set_documentation(
            "Improve the selection using segment anything (SAM)",
            "Improve the selection using segment anything (SAM)",  
            None)
        procedure.set_menu_label("Refine Selection using SAM")
        procedure.set_attribution("Manuel Vogel",
                                  "Manuel Vogel",
                                  "2025")
        procedure.add_menu_path("<Image>/Select/")

        return procedure
        
    # call external python interpreter (for windows)
    def refine_selection_win(self, procedure, run_mode, image, drawables, config, data):
        
        image.undo_group_start()


        #GimpUi.init("python-plugin-selection-refiner-sam-win")
        #dialog = GimpUi.ProcedureDialog.new(procedure, config, "Run Plugin")
        #dialog.fill(["please wait"])
        #dialog.run()
        #dialog.fill(["please wait"])
        layer = drawables[0]
        w,h = layer.get_width(), layer.get_height()
        scale = 1024 / max(w, h)
        new_w, new_h = int(w*scale), int(h*scale)

        selection = Gimp.Selection.bounds(image)
        x1, y1 = int(selection.x1 * scale), int(selection.y1 * scale)
        x2, y2 = int(selection.x2 * scale), int(selection.y2 * scale)

        rgb_file = Gio.file_new_for_path(join(baseLoc, "rgb.png"))
        mask_file = Gio.file_new_for_path(join(baseLoc, "mask.png"))


        Gimp.file_save(Gimp.RunMode.NONINTERACTIVE, image, rgb_file, None)

        
        #Inference
        python_path = join(baseLoc, "gimpenv", "Scripts", "python.exe")
        inference_script = join(baseLoc, "sam_inference.py")
        args = [str(x1), str(y1), str(x2), str(y2), str(new_w), str(new_h), str(w), str(h)]

        command = [python_path, inference_script] + args

        # Run the script using subprocess
        subprocess.run(command)
        
        result_layer = Gimp.file_load_layer(Gimp.RunMode.NONINTERACTIVE, image, mask_file)

        # insert layer because you cannot scale without adding the layer
        image.insert_layer(result_layer, None, 1)

        image.select_item(Gimp.ChannelOps.REPLACE, result_layer)
        image.remove_layer(result_layer)

        #dialog.destroy()
        image.undo_group_end()
        Gimp.displays_flush()

        return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, None)
        

    # direct execution (for linux)
    def refine_selection(self, procedure, run_mode, image, drawables, config, data):
        
        image.undo_group_start()

        #GimpUi.init("python-plugin-selection-refiner-sam")
        #dialog = GimpUi.ProcedureDialog.new(procedure, config, "Run Plugin")
        #dialog.fill(["please wait"])
        #dialog.run()
        #dialog.fill(["please wait"])
        layer = drawables[0]
        w,h = layer.get_width(), layer.get_height()
        scale = 1024 / max(w, h)
        new_w, new_h = int(w*scale), int(h*scale)

        selection = Gimp.Selection.bounds(image)
        selection_bounds = np.array([selection.x1 * scale, selection.y1 * scale, 
                                     selection.x2 * scale, selection.y2 * scale], dtype=np.int64)

        
        # get the image as numpy array (https://gitlab.gnome.org/GNOME/gimp/-/issues/8686)
        rect = Gegl.Rectangle.new(0, 0, w, h)
        buffer1 = layer.get_buffer()
        buffer_bytes = buffer1.get(rect, 1.0, "RGBA u8", Gegl.AbyssPolicy(0))
        image_arr = np.frombuffer(buffer_bytes, dtype=np.uint8).reshape((h,w,-1))

        #Inference
        result_layer_arr = self.sam_infer(image_arr[:,:,:3], selection_bounds, new_w, new_h, w, h)
        
        result_layer = Gimp.Layer().new(image, "result", w, h, Gimp.ImageType.RGBA_IMAGE, 1, Gimp.LayerMode.NORMAL)
        image.insert_layer(result_layer, None, 1)
        buffer2 = result_layer.get_buffer()
        if self.mode == "select":
            rect = Gegl.Rectangle.new(0, 0, w, h)
            buffer2.set(rect, "RGBA u8" , result_layer_arr.tobytes())
            buffer2.flush()
            result_layer.update(0,0,w,h)
            image.select_item(Gimp.ChannelOps.REPLACE, result_layer)
        elif self.mode == "remove":
            pass #TODO
        
        image.remove_layer(result_layer)

        #dialog.destroy()
        image.undo_group_end()
        Gimp.displays_flush()

        return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, None)
        
 
    # linux only. windows uses "sam_inference.py"
    def sam_infer(self, image_array, bounds, new_w, new_h, original_w, original_h):
            
        image = Image.fromarray(image_array)
        im = np.array(image.resize((new_w, new_h)))

        # load SAM
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        if SAM_VERSION == 1:
            sam = sam_model_registry["vit_l"](checkpoint=sam_checkpoint)
            sam.to(device=device)
            predictor = SamPredictor(sam)
        elif SAM_VERSION == 2:
            sam2_model = build_sam2(sam_cfg, sam_checkpoint, device=device)
            predictor = SAM2ImagePredictor(sam2_model)
        predictor.set_image(im)

        # sam prediction
        masks, _, _ = predictor.predict(box=bounds, multimask_output=False)
        mask_rgba = np.zeros((masks[0].shape[0], masks[0].shape[1], 4), dtype=np.uint8)

        if self.mode == "select": #  make it transparent and white
            # Set white (255, 255, 255) where the mask is True, and full opacity (alpha = 255)
            mask_rgba[masks[0] == 1] = [255, 255, 255, 255]  # White with full opacity
        elif self.mode == "remove": #  make it black and white
            mask_rgba[masks[0] == 1] = [255, 255, 255, 255]  # White with full opacity
            mask_rgba[masks[0] == 0] = [0, 0, 0, 255]        # Black with full opacity

        # Convert the numpy array to an Image object
        mask_image = Image.fromarray(mask_rgba)

        return np.array(mask_image.resize((original_w, original_h)))


                
Gimp.main(SelectionRefinerSAM.__gtype__, sys.argv)
