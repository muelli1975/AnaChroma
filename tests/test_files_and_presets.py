from dataclasses import replace
from pathlib import Path
import json
from threading import Event
import numpy as np
from PIL import Image, JpegImagePlugin
import pytest

from anachroma.engine import Cancelled
from anachroma.export import SizeSpec, export_image, target_paths
from anachroma.inputs import discover, load_pair
from anachroma.matrices import BUILTINS
from anachroma.presets import load_presets, save_presets
from anachroma.worker import run_batch


def image(path, size=(12,4)):
    path.parent.mkdir(parents=True,exist_ok=True)
    Image.new("RGB",size,(60,120,180)).save(path)
    return path


def test_output_mode_settings_migrate_and_roundtrip(tmp_path):
    from anachroma.settings import load_settings, save_settings
    path = tmp_path / "settings.json"
    assert load_settings(path).use_program_output
    path.write_text(json.dumps({"output": str(tmp_path / "custom")}), encoding="utf-8")
    settings = load_settings(path)
    assert not settings.use_program_output
    settings.use_program_output = True
    save_settings(path, settings)
    restored = load_settings(path)
    assert restored.use_program_output and restored.output == str(tmp_path / "custom")


def test_orientation_and_odd_width(tmp_path):
    path=tmp_path/"oriented.jpg"
    im=Image.new("RGB",(6,4))
    exif=Image.Exif(); exif[274]=6
    im.save(path,exif=exif)
    l,r=load_pair(path)
    assert l.shape == r.shape == (6,2,3)
    with pytest.raises(ValueError,match="nicht gerade"):
        load_pair(image(tmp_path/"odd.png",(7,4)))
    alpha=tmp_path/"alpha.png"
    Image.new("RGBA",(4,2),(12,34,56,0)).save(alpha)
    assert tuple(load_pair(alpha)[0][0,0]) == (12,34,56)


def test_discovery_navigation_recursion_and_structure(tmp_path):
    root=tmp_path/"Urlaub"
    second=image(root/"bild2.png")
    image(root/"bild10.png"); image(root/"bild1.png")
    image(root/"Tag1"/"eins.png")
    image(root/"output"/"ignored.png")
    assert [p.name for p in discover(second).files] == ["bild1.png","bild2.png","bild10.png"]
    assert discover(second).selected == 1
    found=discover(root,recursive=True)
    assert len(found.files)==4
    targets=target_paths(found,found.files,tmp_path/"results",BUILTINS[0])
    assert tmp_path/"results"/"Tag1"/"eins_dubois_lcd.jpg" in targets


def test_collision_and_original_protection(tmp_path):
    root=tmp_path/"input"
    image(root/"same.jpg"); image(root/"same.png")
    found=discover(root)
    with pytest.raises(ValueError,match="dieselbe"):
        target_paths(found,found.files,tmp_path/"output",BUILTINS[0])
    root2=tmp_path/"input2"
    image(root2/"bild.png"); image(root2/"bild_color.jpg")
    found=discover(root2/"bild.png")
    with pytest.raises(ValueError,match="Original"):
        target_paths(found,found.files,root2,BUILTINS[9])


@pytest.mark.parametrize("kind,edge,pixels,original,expected",[
    ("1080p","long",2048,(4000,3000),(1440,1080)),
    ("2160p","long",2048,(3000,4000),(1620,2160)),
    ("2048 lange Seite","long",2048,(4000,3000),(2048,1536)),
    ("Benutzerdefiniert","short",1080,(1920,1080),(1920,1080)),
    ("1080p","long",2048,(640,360),(1920,1080)),
])
def test_sizes(kind,edge,pixels,original,expected):
    assert SizeSpec(kind,edge,pixels).dimensions(original)==expected


def test_preset_precision_schema_collision_and_corruption(tmp_path):
    path=tmp_path/"presets.json"
    m=replace(BUILTINS[0].as_custom(),left=((.456100123456,.500484,.176381),*BUILTINS[0].left[1:]))
    save_presets(path,[m])
    assert load_presets(path)==[m]
    prior=path.read_bytes()
    with pytest.raises(ValueError,match="vergeben"):
        save_presets(path,[m,replace(m,id="custom:other")])
    assert path.read_bytes()==prior
    path.write_text('{"schema_version":99,"presets":[]}')
    with pytest.raises(ValueError,match="Version"):
        load_presets(path)
    assert "99" in path.read_text()
    with pytest.raises(ValueError):
        replace(m,left=((float("nan"),0.,0.),*m.left[1:])).validate()


@pytest.mark.parametrize("quality",[90,95])
def test_jpeg_444_and_metadata_failure_keep_output(tmp_path,monkeypatch,quality):
    src=image(tmp_path/"sbs.png",(16,4)); target=tmp_path/"out.jpg"
    monkeypatch.setattr("anachroma.export.copy_metadata",lambda *args: "warning")
    assert export_image(src,target,BUILTINS[0],SizeSpec(),quality)=="warning"
    with Image.open(target) as out:
        assert out.size==(8,4)
        assert JpegImagePlugin.get_sampling(out)==0
        assert out.info.get("icc_profile")
        assert out.getexif().get(274) is None


def test_cancelled_export_preserves_previous_target(tmp_path,monkeypatch):
    source=image(tmp_path/"sbs.png"); target=tmp_path/"out.jpg"
    target.write_bytes(b"previous file")
    cancel=Event()
    def metadata(*args):
        cancel.set()
        return ""
    monkeypatch.setattr("anachroma.export.copy_metadata",metadata)
    with pytest.raises(Cancelled):
        export_image(source,target,BUILTINS[9],SizeSpec(),cancel=cancel)
    assert target.read_bytes()==b"previous file"
    assert not list(tmp_path.glob("*.partial.jpg"))


def test_batch_continues_after_error_and_reports_cancellation(tmp_path,monkeypatch):
    files=(Path("bad.png"),Path("good.png"))
    def export(src,*args):
        if src.name=="bad.png": raise ValueError("invalid SBS")
        return "metadata warning"
    monkeypatch.setattr("anachroma.worker.export_image",export)
    r=run_batch(files,files,BUILTINS[0],SizeSpec(),90,Event(),lambda _:None)
    assert r.processed==1 and len(r.errors)==len(r.warnings)==1
    cancel=Event();cancel.set()
    r=run_batch(files,files,BUILTINS[0],SizeSpec(),90,cancel,lambda _:None)
    assert r.cancelled and not r.errors and not r.processed


def test_development_adjustments_are_discarded(tmp_path):
    import json
    from dataclasses import asdict
    path=tmp_path/"presets.json"
    method=BUILTINS[0].as_custom()
    entry=asdict(method);entry.update(brightness=1.2, contrast=.9)
    path.write_text(json.dumps({"schema_version":1,"presets":[entry]}))
    original = path.read_bytes()
    notices = []
    assert load_presets(path, notices)==[method]
    assert notices == [method.name]
    assert path.read_bytes() == original
    save_presets(path,[method])
    assert "brightness" not in path.read_text() and "contrast" not in path.read_text()
    assert path.with_name("presets.json.pre-1.0.bak").read_bytes() == original
