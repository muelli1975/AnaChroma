"""Real CIELab execution when the platform's native tool has been built."""
from threading import Event
import numpy as np
from PIL import Image
import pytest
from anachroma.cielab import make_cielab
from anachroma.engine import Cancelled
from anachroma.export import SizeSpec, export_image
from anachroma.matrices import BUILTINS
from anachroma.resources import find_tool

pytestmark = pytest.mark.skipif(find_tool("cielab") is None, reason="Build native CIELab first")


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
