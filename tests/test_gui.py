"""Real Tk widget checks; run under Xvfb on Linux CI."""
import os
import time
from dataclasses import replace
import numpy as np
from PIL import Image
import pytest

pytestmark = pytest.mark.skipif(not os.environ.get("DISPLAY") and os.name != "nt", reason="A Tk display is required")


@pytest.fixture
def app(tmp_path, monkeypatch):
    import customtkinter as ctk
    from anachroma import gui
    ctk.set_appearance_mode("dark")
    monkeypatch.setattr(gui,"user_dir",lambda:tmp_path)
    monkeypatch.setattr(gui.messagebox,"showwarning",lambda *a,**k:None)
    monkeypatch.setattr(gui.messagebox,"showerror",lambda *a,**k:None)
    root=gui.AnaChromaApp()
    callback_errors=[]
    root.report_callback_exception=lambda *error:callback_errors.append(error)
    root.update()
    yield root
    root.close()
    end=time.monotonic()+5
    while time.monotonic()<end:
        try:
            root.update()
            if not root.winfo_exists():break
        except Exception: break
        time.sleep(.01)
    assert not callback_errors, callback_errors


def wait_for(app, condition):
    end=time.monotonic()+8
    while time.monotonic()<end:
        app.update()
        if condition():return
        time.sleep(.01)
    raise AssertionError("GUI worker did not finish")


def test_exact_entry_slider_wheel_and_cancel(app):
    original=app.selected_method()
    app.create_custom();app.update()
    editor=app.editor
    untouched=editor.controls[0][0][1].get()
    cell=editor.controls[0][0][0]
    cell.var.set("0,456100123456")
    assert editor.draft().left[0][0]==.456100123456
    assert editor.draft().left[0][0] != cell.slider.get() or cell.get()==.456100123456
    assert editor.controls[0][0][1].get()==untouched
    cell.var.set("2.5")
    assert cell.get()==2.5 and cell.slider.cget("to")==2.5
    cell.entry.focus_force();app.update()
    cell.entry._entry.event_generate("<MouseWheel>", delta=120);app.update()
    assert cell.get()==pytest.approx(2.501)
    assert editor.controls[0][0][1].get()==untouched
    cell.var.set("-")
    assert editor.save_button.cget("state")=="disabled"
    editor.cancel();app.update()
    assert app.editor is None and app.draft is None
    assert app.selected_method()==original


def test_start_demo_live_preview_does_not_become_batch_input(app):
    wait_for(app, lambda: app.preview_image is not None)
    assert app.preview_image.size == (1024, 576)
    assert app.inputs is None
    assert app.save_button.cget("state") == "disabled"
    assert app.all_button.cget("state") == "disabled"
    assert app.previous_button.cget("state") == "disabled"
    assert "Beispielbild" in app.filename.cget("text")
    previous = np.asarray(app.preview_image).copy()
    gray = next(method for method in app.methods.values() if method.suffix == "grey")
    app._refresh_methods(gray.id); app._method_changed()
    wait_for(app, lambda: app.preview_image is not None and
             not np.array_equal(previous, np.asarray(app.preview_image)))


def test_preview_navigation_and_preset_roundtrip(app,tmp_path):
    for i in range(2):
        Image.new("RGB",(32,8),(64+i*80,90,180)).save(tmp_path/f"bild{i}.png")
    app.load_input(tmp_path/"bild1.png")
    wait_for(app,lambda: app.inputs is not None and app.preview_image is not None and app.preview_image.size==(16,8))
    assert app.index==1 and app.preview_image.size==(16,8)
    app.navigate(-1)
    wait_for(app,lambda: app.index==0 and app.preview_after is None)
    app.create_custom();app.update()
    editor=app.editor
    wait_for(app, lambda: editor.preview_image is not None)
    editor.name.set("Mein Rot/Cyan")
    editor.suffix.set("mein_rotcyan")
    editor.controls[0][0][0].var.set("0.456100123456")
    editor.save();app.update()
    assert app.editor is None
    assert app.selected_method().left[0][0]==.456100123456
    from anachroma.presets import load_presets
    assert load_presets(app.presets_path)[0]==app.selected_method()
    app.size_var.set("Benutzerdefiniert"); app._size_changed();app.update()
    assert app.custom_size.winfo_ismapped()
    app.size_var.set("Original");app._size_changed();app.update()
    assert not app.custom_size.winfo_ismapped()
    app.start_export(False)
    wait_for(app,lambda: not app.batch_running)
    assert (tmp_path/"output"/"bild0_mein_rotcyan.jpg").is_file()


def test_corrupt_preset_file_is_not_replaced(tmp_path,monkeypatch):
    from anachroma import gui
    from anachroma.matrices import BUILTINS
    path=tmp_path/"presets.json";path.write_text("broken")
    monkeypatch.setattr(gui,"user_dir",lambda:tmp_path)
    monkeypatch.setattr(gui.messagebox,"showwarning",lambda *a,**k:None)
    root=gui.AnaChromaApp()
    try:
        with pytest.raises(ValueError):root.save_custom(BUILTINS[0].as_custom())
        assert path.read_text()=="broken"
    finally:
        root.close()
        for _ in range(10):
            try:root.update()
            except Exception:break
            time.sleep(.01)
