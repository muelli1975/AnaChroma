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


def wait_for(app, condition, timeout=20):
    end=time.monotonic()+timeout
    while time.monotonic()<end:
        app.update()
        if condition():return
        time.sleep(.01)
    raise AssertionError(f"GUI worker did not finish: {app.status.cget('text')}; "
                         f"input={app.preview_path()}; preview={getattr(app.preview_image, 'size', None)}")


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
    w, h = app.preview_image.size
    assert 0 < w <= 1024 and abs(w/h-16/9) < .01
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


def test_missing_cielab_can_switch_back_and_export(app, tmp_path, monkeypatch):
    from anachroma import gui
    monkeypatch.setattr(gui, "find_tool", lambda _: None)
    monkeypatch.setattr("anachroma.metadata.find_tool", lambda _: None)
    source = tmp_path / "sbs.png"
    Image.new("RGB", (32, 12), (60, 120, 180)).save(source)
    app.load_input(source)
    wait_for(app, lambda: app.inputs is not None and app.preview_image is not None)
    cielab = next(m for m in app.methods.values() if m.mode == "cielab")
    app._refresh_methods(cielab.id); app._method_changed()
    wait_for(app, lambda: "CIELab nicht gefunden" in app.status.cget("text"))
    assert app.method_menu.cget("state") == "normal"
    assert app.file_button.cget("state") == "normal"
    app._refresh_methods("builtin:10"); app._method_changed()
    wait_for(app, lambda: app.preview_image is not None)
    app.start_export(False)
    wait_for(app, lambda: not app.batch_running, timeout=45)
    assert list((tmp_path / "output").glob("*.jpg"))
    assert "Metadatenwarnung" in app.status.cget("text")


def test_language_switch_editor_template_and_slider_factors(app, tmp_path):
    app._language_changed("English"); app.update()
    assert app.action_button.cget("text") == "Save image"
    assert app.file_button.cget("text") == "Single image…"
    app._size_selected("Custom"); app.update()
    assert app.size_var.get() == "Benutzerdefiniert" and app.custom_size.winfo_ismapped()
    app.create_custom(); app.update()
    editor = app.editor
    template = next(m for m in editor.templates.values() if m.suffix == "wimmer")
    editor._template(template.name)
    assert "Wimmer" in editor.name.get() and editor.suffix.get() == "eigen_wimmer"
    assert editor.draft().left == template.left and editor.draft().right == template.right
    editor.brightness._slide(1.25)
    editor.contrast._slide(.85)
    assert editor.draft().brightness == 1.25 and editor.draft().contrast == .85
    # Template changes reset adjustments and update its proposed identity.
    editor._template(next(m.name for m in editor.templates.values() if m.suffix == "color"))
    assert editor.suffix.get() == "eigen_color"
    assert editor.draft().brightness == editor.draft().contrast == 1
    editor.cancel(); app._language_changed("Deutsch"); app.update()
    assert app.file_button.cget("text") == "Einzelbild…"
    assert app.settings.language == "de"


def test_input_mode_action_and_recursive_output(app, tmp_path):
    root = tmp_path / "Urlaub"
    (root / "Tag1").mkdir(parents=True)
    Image.new("RGB", (32, 8), (80, 90, 100)).save(root / "eins.png")
    Image.new("RGB", (32, 8), (80, 90, 100)).save(root / "Tag1" / "zwei.png")
    app.recursive.set(True)
    app.load_input(root)
    wait_for(app, lambda: app.inputs is not None and not app.scanning)
    assert app.inputs.folder_input and len(app.inputs.files) == 2
    assert "Bildordner" in app.input_label.cget("text")
    assert app.action_button.cget("text") == "Alle verarbeiten"
    app.primary_action()
    wait_for(app, lambda: not app.batch_running, timeout=45)
    assert list((tmp_path/"output"/"Urlaub"/"Tag1").glob("zwei_*.jpg"))
    app.load_input(root / "eins.png")
    wait_for(app, lambda: app.inputs is not None and not app.inputs.folder_input and not app.scanning)
    assert app.action_button.cget("text") == "Bild speichern"
    assert not app.save_button.winfo_ismapped()


def test_stereofine_output_selection_and_persistence(app, tmp_path, monkeypatch):
    from anachroma import gui
    from anachroma.settings import load_settings
    from anachroma.theme import DISABLED, TEXT
    assert app.use_program_output.get()
    assert app._effective_output() == (tmp_path / "output").resolve()
    assert app.output_status.cget("text") == str((tmp_path / "output").resolve())
    assert app.output_checkbox.cget("text") == "Unterordner im Programmordner verwenden"
    assert app.custom_output_label.cget("text") == "Eigener Ausgabeordner"
    assert app.output_button.cget("text") == "Auswählen"
    assert app.output_button.cget("state") == "normal"
    assert app.custom_output_label.cget("text_color") == DISABLED
    chosen = []
    custom = tmp_path / "Urlaub" / "fertig"
    monkeypatch.setattr(gui.filedialog, "askdirectory", lambda **kw: chosen.append(kw) or "")
    app.output_button.invoke()
    assert len(chosen) == 1
    assert app.use_program_output.get() and not app.output_var.get()
    assert app.output_button.cget("state") == "normal"
    monkeypatch.setattr(gui.filedialog, "askdirectory", lambda **kw: str(custom))
    app.output_button.invoke()
    assert not app.use_program_output.get()
    assert app._effective_output() == custom.resolve()
    assert app.output_status.cget("text") == str(custom.resolve())
    assert app.output_label.cget("text_color") == TEXT
    saved = load_settings(app.settings_path)
    assert not saved.use_program_output and saved.output == str(custom)
    app.output_checkbox.toggle()
    assert app._effective_output() == (tmp_path / "output").resolve()
    assert app.output_status.cget("text") == str((tmp_path / "output").resolve())
    assert app.output_var.get() == str(custom)
    assert app.output_label.cget("text_color") == DISABLED
    assert load_settings(app.settings_path).use_program_output
    app.output_checkbox.toggle()
    assert app._effective_output() == custom.resolve()
    root = tmp_path / "Urlaub"
    (root / "Tag1").mkdir(parents=True)
    custom.mkdir()
    Image.new("RGB", (32, 8)).save(root / "Tag1" / "original.png")
    Image.new("RGB", (32, 8)).save(custom / "already-created.png")
    app.recursive.set(True)
    app.load_input(root)
    assert app.output_button.cget("state") == "disabled"
    wait_for(app, lambda: not app.scanning)
    assert len(app.inputs.files) == 1
    assert app.output_status.cget("text") == str(custom.resolve() / root.name)
    assert app.output_button.cget("state") == "normal"
    app.output_checkbox.toggle()
    wait_for(app, lambda: not app.scanning)
    assert len(app.inputs.files) == 2
    assert app.output_status.cget("text") == str((tmp_path / "output" / root.name).resolve())
    assert app.output_button.cget("state") == "normal"
    app.output_checkbox.toggle()
    wait_for(app, lambda: not app.scanning)
    assert len(app.inputs.files) == 1 and app._effective_output() == custom.resolve()
    app._language_changed("English")
    assert app.output_checkbox.cget("text") == "Use subfolder in program folder"
    assert app.custom_output_label.cget("text") == "Custom output folder"
    assert app.output_button.cget("text") == "Choose"
    assert app.output_status.cget("text") == str(custom.resolve() / root.name)
    app.load_input(root / "Tag1" / "original.png")
    wait_for(app, lambda: not app.scanning)
    assert app.output_status.cget("text") == str(custom.resolve())
    app.output_var.set("")
    app._state()
    assert app.output_status.cget("text") == "No custom output folder selected"
    app._language_changed("Deutsch")
    assert app.output_status.cget("text") == "Kein eigener Ausgabeordner gewählt"


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
    # Real metadata copying has a 30-second tool timeout; allow it to finish.
    wait_for(app,lambda: not app.batch_running, timeout=45)
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


def assert_family_palette(root):
    """Inspect actual widget colors, including hidden controls and disabled states."""
    import tkinter as tk
    palette = {"#111111", "#181818", "#202020", "#282828", "#333333", "#f2f2f2",
               "#b8b8b8", "#727272", "#9c7c38", "#c6a95e", "#000000", "#7f3939", "#944545"}
    def visit(widget):
        if type(widget).__name__.startswith("CTk"):
            for option in ("fg_color", "bg_color", "border_color", "hover_color", "text_color",
                           "text_color_disabled", "button_color", "button_hover_color", "progress_color",
                           "scrollbar_button_color", "scrollbar_button_hover_color", "placeholder_text_color",
                           "dropdown_fg_color", "dropdown_hover_color", "dropdown_text_color"):
                try:
                    if option == "border_color" and widget.cget("border_width") == 0:
                        continue
                    color = widget.cget(option)
                except (ValueError, AttributeError, tk.TclError):
                    continue
                if isinstance(color, (list, tuple)):
                    color = color[-1]
                if not color or color == "transparent":
                    continue
                rgb = "#" + "".join(f"{part//257:02x}" for part in root.winfo_rgb(color))
                assert rgb in palette, (type(widget).__name__, option, color, rgb)
        for child in widget.winfo_children():
            visit(child)
    visit(root)


def test_family_palette_and_rectangular_preview_surround(app):
    assert_family_palette(app)
    assert app.file_button.cget("fg_color") == "#181818"
    assert app.file_button.cget("hover_color") == "#282828"
    assert app.file_button.cget("border_color") == "#333333"
    assert app.size_menu.cget("fg_color") == "#202020"
    assert app.size_menu.cget("text_color_disabled") == "#727272"
    assert app.preview_panel.cget("fg_color") == "#000000"
    assert app.preview_panel.cget("corner_radius") == 0
    app.scanning = True; app._state()
    for box in (app.recursive_box, app.output_checkbox, app.quality_box):
        assert box.cget("fg_color") == box.cget("hover_color") == "#727272"
    assert_family_palette(app)
    app.scanning = False; app._state()
    assert app.output_checkbox.cget("fg_color") == "#9c7c38"
    assert app.output_checkbox.cget("hover_color") == "#c6a95e"
    wait_for(app, lambda: app.preview_image is not None)
    # Use actual image widgets in both windows: the displayed width determines
    # StereoFine's surround (3% + 2 pixels, at least 16 pixels).
    def check_preview(panel, label, displayed):
        width, height = displayed.cget("size")
        border = max(16, round(width * .03) + 2)
        info = label.grid_info()
        assert info["padx"] == info["pady"] == border
        assert width + 2*border <= panel.winfo_width()
        assert height + 2*border <= panel.winfo_height()
        assert panel.cget("corner_radius") == 0
    for size in ((1600, 900), (900, 1600), (32, 8)):
        app.preview_image = Image.new("RGB", size)
        app._fit_preview(); app.update_idletasks()
        check_preview(app.preview_panel, app.preview_label, app.ctk_image)
    app.create_custom(); app.update()
    editor = app.editor
    wait_for(app, lambda: editor.preview_image is not None)
    assert_family_palette(editor)
    check_preview(editor.preview_panel, editor.live_preview, editor.preview_image)
    editor.cancel(); app.update()
