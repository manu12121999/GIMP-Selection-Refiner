#!/usr/bin/env python3
import os
import sys
import tempfile

# This Plugin is only for GIMP Version >= 3.0.0 and linux
import gi
gi.require_version('Gimp', '3.0')
from gi.repository import Gimp
gi.require_version('GimpUi', '3.0')
from gi.repository import GimpUi
from gi.repository import GObject
from gi.repository import GLib
from gi.repository import Gegl
from gi.repository import Gio

baseLoc = os.path.dirname(os.path.realpath(__file__))+'/'
for version in range(6,20):
    sys.path.extend([baseLoc+f'gimpenv/lib/python3.{version}', baseLoc+f'gimpenv/lib/python3.{version}/site-packages', baseLoc+f'gimpenv/lib/python3.{version}/site-packages/setuptools'])
sys.path.extend([baseLoc+'gimpenv/Lib', baseLoc+'gimpenv/Lib/site-packages', baseLoc+'gimpenv/Lib/site-packages/setuptools'])
sys.path.extend([baseLoc])


import numpy as np
import torch
from PIL import Image
from segment_anything import SamPredictor, sam_model_registry


class SelectionRefinerSAM(Gimp.PlugIn):

    ## GimpPlugIn virtual methods ##
    def do_query_procedures(self):
        return [ 'python-plugin-selection-refiner-sam' ]


    def do_create_procedure(self, name):
        self.mode = "select"
        procedure = None
        
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
        
    def refine_selection(self, procedure, run_mode, image, drawables, config, data):
        
        image.undo_group_start()

        mask_file = Gio.file_new_for_path(os.path.join(tempfile.gettempdir(), "image_out.png"))
        
        #GimpUi.init("python-plugin-selection-refiner-sam")
        #dialog = GimpUi.ProcedureDialog.new(procedure, config, "Run Plugin")
        #dialog.fill(["please wait"])
        #dialog.run()
        #dialog.fill(["please wait"])

        selection = Gimp.Selection.bounds(image)
        selection_bounds = np.array([selection.x1, selection.y1, selection.x2, selection.y2])
        
        # drawables[0].remove_mask(1)

        layer = drawables[0]
        # get the image as numpy array (https://gitlab.gnome.org/GNOME/gimp/-/issues/8686)
        w,h = layer.get_width(), layer.get_height()
        rect = Gegl.Rectangle.new(0, 0, w, h)
        buffer = layer.get_buffer()
        buffer_bytes = buffer.get(rect, 1.0, None, Gegl.AbyssPolicy(0))
        image_arr = np.frombuffer(buffer_bytes, dtype=np.uint8).reshape((h,w,-1))

        #Inference
        result_layer_arr = self.sam_inference(image_arr[:,:,:3], selection_bounds)
        
        
        #print(result_layer_arr.shape)
        #result_layer_arr_4channels = np.repeat(result_layer_arr[:, :, np.newaxis], 4, axis=2)
        #buffer.set(rect, TODO , result_layer_arr_4channels.tobytes())
        #buffer.flush()

        #output
        result_layer = Gimp.file_load_layer(Gimp.RunMode.NONINTERACTIVE, image, mask_file)
        if self.mode == "remove":
            mask = result_layer.create_mask(5)
            drawables[0].add_mask(mask)
        elif self.mode == "select":
            image.insert_layer(result_layer, None, 1)
            image.select_item(Gimp.ChannelOps.REPLACE, result_layer)
            image.remove_layer(result_layer)
        
        #dialog.destroy()
        image.undo_group_end()
        Gimp.displays_flush()

        return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, None)
        
 
    def sam_inference(self, image_array, bounds):
            
        image = Image.fromarray(image_array)
        w, h = image.size

        # scale the image to have the longer side 1024
        scale = 1024 / max(w, h)
        new_w, new_h = int(w * scale), int(h * scale)
        im = np.array(image.resize((new_w, new_h)))

        # load SAM
        sam = sam_model_registry["vit_l"](checkpoint=os.path.join(baseLoc, "sam_vit_l_0b3195.pth"))
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        sam.to(device=device)
        predictor = SamPredictor(sam)
        predictor.set_image(im)

        # sam prediction
        masks, _, _ = predictor.predict(box=bounds*scale, multimask_output=False)
        mask_rgba = np.zeros((masks[0].shape[0], masks[0].shape[1], 4), dtype=np.uint8)

        if self.mode == "select": #  make it transparent and white
            # Set white (255, 255, 255) where the mask is True, and full opacity (alpha = 255)
            mask_rgba[masks[0] == 1] = [255, 255, 255, 255]  # White with full opacity
        elif self.mode == "remove": #  make it black and white
            mask_rgba[masks[0] == 1] = [255, 255, 255, 255]  # White with full opacity
            mask_rgba[masks[0] == 0] = [0, 0, 0, 255]        # Black with full opacity

        # Convert the numpy array to an Image object
        mask_image = Image.fromarray(mask_rgba)

        # Save the mask as a PNG
        mask_image.resize((w, h)).save(os.path.join(tempfile.gettempdir(), "image_out.png"))
        
        return np.array(mask_image.resize((w, h)))
                
Gimp.main(SelectionRefinerSAM.__gtype__, sys.argv)
