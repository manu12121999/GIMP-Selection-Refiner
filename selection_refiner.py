#!/usr/bin/env python3
import os
from os.path import join
import sys
import subprocess

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


baseLoc = os.path.dirname(os.path.realpath(__file__))

class SelectionRefinerSAM(Gimp.PlugIn):

    ## GimpPlugIn virtual methods ##
    def do_query_procedures(self):
        return [ 'python-plugin-selection-refiner-sam-win' ]


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
        args = [str(x1), str(y1), str(x2), str(y2), str(new_w), str(new_h), str(w), str(h), baseLoc]

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
        
 
    
                
Gimp.main(SelectionRefinerSAM.__gtype__, sys.argv)
