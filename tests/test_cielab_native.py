"""Real CIELab execution when the platform's native tool has been built."""
from threading import Event
from pathlib import Path
import base64
import hashlib
import io
import json
import numpy as np
from PIL import Image
import pytest
from anachroma.cielab import make_cielab
from anachroma.engine import Cancelled
from anachroma.export import SizeSpec, export_image
from anachroma.matrices import BUILTINS
from anachroma.resources import find_tool

pytestmark = pytest.mark.skipif(find_tool("cielab") is None, reason="Build native CIELab first")


@pytest.mark.parametrize("name", ("random", "gray", "colors", "demo"))
def test_native_matches_recorded_batch_executable_on_every_platform(name):
    fixture = json.loads((Path(__file__).parent / "fixtures" / "cielab_reference.json").read_text())
    arrays = {}
    for side, recorded in fixture["cases"][name].items():
        data = base64.b64decode(recorded["png_base64"])
        assert hashlib.sha256(data).hexdigest() == recorded["sha256"]
        with Image.open(io.BytesIO(data)) as image:
            arrays[side] = np.array(image.convert("RGB"))
    actual = np.asarray(make_cielab(arrays["left"], arrays["right"]))
    difference = np.abs(actual.astype(np.int16) - arrays["reference"].astype(np.int16))
    assert difference.max() <= 2, (name, difference.max(), difference.mean())


def test_real_cielab_rgb_grayscale_and_repeatability():
    ramp = np.repeat(np.arange(0, 256, 16, dtype=np.uint8)[None, :, None], 3, axis=2)
    first = make_cielab(ramp, ramp)
    assert first.size == (16, 1) and first.mode == "RGB"
    actual = np.asarray(first)
    assert actual[0, 0].max() == 0
    assert actual[0, -1].min() > actual[0, 1].max()
    assert np.array_equal(actual, np.asarray(make_cielab(ramp, ramp)))


def test_real_cielab_export_resizes_halves_and_jpeg_444(tmp_path):
    rng = np.random.default_rng(2026)
    source = tmp_path / "stereo.png"
    Image.fromarray(rng.integers(0, 256, (12, 48, 3), dtype=np.uint8)).save(source)
    output = tmp_path / "anaglyphe.jpg"
    method = next(m for m in BUILTINS if m.mode == "cielab")
    export_image(source, output, method, SizeSpec("Benutzerdefiniert", "long", 12), 90)
    with Image.open(output) as image:
        assert image.size == (12, 6)
        assert all(component[1:3] == (1, 1) for component in image.layer)


def test_real_cielab_cancelled_before_launch():
    event = Event(); event.set()
    with pytest.raises(Cancelled):
        make_cielab(np.zeros((1, 1, 3), dtype=np.uint8), np.zeros((1, 1, 3), dtype=np.uint8), event)
