"""Checks run only with --smoke-test against the real packaged application."""
from pathlib import Path
from tempfile import TemporaryDirectory
from PIL import Image
from .resources import find_tool


class PackagedSmokeCheck:
    def __init__(self, app, failures):
        self.app, self.failures = app, failures
        self.directory = TemporaryDirectory(prefix="anachroma-package-check-")
        self.root = Path(self.directory.name)
        self.stage = "demo"

    def poll(self):
        app = self.app
        if self.stage == "demo":
            if app.preview_image is None or app.preview_photo is None:
                return False
            w, h = app.preview_image.size
            if not (0 < w <= 1024 and abs(w/h-16/9) < .01) or app.inputs is not None:
                self.failures.append("Bundled SBS preview contract failed")
                return True
            if not all(find_tool(name) for name in ("cielab", "exiftool")):
                self.failures.append("Packaged CIELab or ExifTool is missing")
                return True
            source = self.root / "SBS_ä.png"
            image = Image.new("RGB", (32, 12), (70, 120, 180))
            exif = Image.Exif(); exif[315] = "AnaChroma package check"
            image.save(source, exif=exif)
            app.settings_path = self.root / "settings.json"
            app.output_var.set(str(self.root / "output"))
            app.use_program_output.set(False)
            app.preview_image = None
            app._refresh_methods(next(m.id for m in app.methods.values() if m.mode == "cielab"))
            app.load_input(source)
            self.stage = "cielab"
        elif self.stage == "cielab":
            if app.scanning or app.inputs is None or app.preview_image is None:
                return False
            if app.preview_image.size != (16, 12):
                self.failures.append("Packaged CIELab preview size failed")
                return True
            app.primary_action()
            self.stage = "export"
        elif self.stage == "export":
            if app.batch_running:
                return False
            outputs = list((self.root / "output").glob("*_cielab.jpg"))
            if len(outputs) != 1:
                self.failures.append("Packaged CIELab export failed")
            else:
                with Image.open(outputs[0]) as image:
                    if image.size != (2048, 1536) or image.getexif().get(315) != "AnaChroma package check":
                        self.failures.append("Packaged CIELab dimensions or ExifTool metadata copy failed")
            return True
        return False

    def close(self):
        self.directory.cleanup()
