"""Render the actual precision editor in both languages at 100/150 percent."""
import base64, io, json, tempfile
from pathlib import Path
from unittest.mock import patch
import customtkinter as ctk
from PIL import ImageGrab
from anachroma import gui
ctk.set_appearance_mode("dark")
screens=Path("build/editor-review")
screens.mkdir(parents=True,exist_ok=True)
with tempfile.TemporaryDirectory() as directory, patch.object(gui,"user_dir",return_value=Path(directory)):
    app=gui.AnaChromaApp()
    try:
        for scale in (1.,1.5):
            ctk.set_widget_scaling(scale);ctk.set_window_scaling(scale)
            for language in ("Deutsch","English"):
                app._language_changed(language);app.create_custom();app.update()
                editor=app.editor
                for grid in editor.controls:
                    for row in grid:
                        for cell,value in zip(row,("-0.12345678901234568","1.2345678901234567","-2.345678901234567e+20")):
                            cell.var.set(value)
                editor.correct.set(True)
                for cell in editor.powers:cell.var.set("0.6666666666666666")
                app.update();editor.lift();app.update()
                box=(editor.winfo_rootx(),editor.winfo_rooty(),editor.winfo_rootx()+editor.winfo_width(),editor.winfo_rooty()+editor.winfo_height())
                shot=ImageGrab.grab(bbox=box)
                path=screens/f"{language}-{scale}.png";shot.save(path)
                buffer=io.BytesIO();shot.save(buffer,format="PNG")
                print("EDITOR_REVIEW_JSON "+json.dumps({"language":language,"scale":scale,"size":shot.size,"image":base64.b64encode(buffer.getvalue()).decode()}),flush=True)
                editor.cancel();app.update()
    finally:
        app.close()
