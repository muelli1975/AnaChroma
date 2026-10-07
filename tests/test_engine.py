from dataclasses import replace
from pathlib import Path
import re
import shutil
import subprocess
from threading import Event
import numpy as np
from PIL import Image
import pytest

from anachroma.engine import Cancelled, make_anaglyph
from anachroma.matrices import BUILTINS, ZERO

REFERENCE = Path(__file__).with_name("reference_batch.bat").read_text(encoding="utf-8")


def batch_definition(number):
    section = REFERENCE.split(":set_matrix_definition\n", 1)[1]
    block = section.split(f'if "%~1"=="{number}" (', 1)[1].split("exit /b", 1)[0]
    return dict(re.findall(r'set "(\w+)=(.*?)"', block))


@pytest.mark.parametrize("number", range(1, 19))
def test_definitions_match_pinned_batch(number):
    reference = batch_definition(number)
    method = BUILTINS[number-1]
    assert method.suffix == reference["MATRIXNAME"]
    assert method.mode == reference["MATRIXMODE"]
    if "MATRIX_LEFT" in reference:
        for key, matrix in (("MATRIX_LEFT", method.left), ("MATRIX_RIGHT", method.right)):
            values = np.array([float(x) for x in reference[key].split(":")]).reshape(3, 4)[:, :3]
            np.testing.assert_array_equal(np.array(matrix), values)


def test_color_and_grey_channel_routing():
    left = np.array([[[255, 0, 0], [0, 255, 0]]], dtype=np.uint8)
    right = np.array([[[0, 64, 128], [255, 0, 0]]], dtype=np.uint8)
    np.testing.assert_array_equal(make_anaglyph(left, right, BUILTINS[9]), [[[255,64,128],[0,0,0]]])
    np.testing.assert_array_equal(make_anaglyph(left, right, BUILTINS[11]), [[[76,52,52],[150,76,76]]])


def test_linear_mix_is_not_srgb_mix():
    left = np.zeros((1,1,3), dtype=np.uint8)
    right = np.full((1,1,3), 255, dtype=np.uint8)
    base = BUILTINS[9].as_custom()
    m = replace(base, left=ZERO, right=((.5,0,0),(0,.5,0),(0,0,.5)))
    assert make_anaglyph(left, right, m)[0,0,0] == 128
    assert make_anaglyph(left, right, replace(m, mode="linear"))[0,0,0] == 188


def test_clip_each_contribution_before_addition():
    image = np.full((1,1,3), 255, dtype=np.uint8)
    m = replace(BUILTINS[9].as_custom(), left=((-1,0,0),(0,0,0),(0,0,0)),
                right=((1,0,0),(0,0,0),(0,0,0)))
    assert make_anaglyph(image, image, m)[0,0,0] == 255


def test_custom_template_preserves_pipeline():
    rng = np.random.default_rng(8)
    l, r = (rng.integers(0,256,(17,23,3), dtype=np.uint8) for _ in range(2))
    for m in BUILTINS:
        if m.editable:
            np.testing.assert_array_equal(make_anaglyph(l,r,m), make_anaglyph(l,r,m.as_custom()))
    with pytest.raises(ValueError):
        BUILTINS[6].as_custom()
    with pytest.raises(ValueError):
        BUILTINS[15].as_custom()


def test_powers_and_adjustment_neutral_and_cancellation():
    image = np.full((5,7,3), 64, dtype=np.uint8)
    base = BUILTINS[9].as_custom()
    corrected = replace(base, correct_rgb=True, powers=(.75,1,1))
    result = make_anaglyph(image, image, corrected)
    assert result[0,0,0] == round((64/255)**.75*255)
    assert result[0,0,1] == 64
    np.testing.assert_array_equal(make_anaglyph(image,image,replace(base,brightness=0)), np.zeros_like(image))
    cancel = Event(); cancel.set()
    with pytest.raises(Cancelled):
        make_anaglyph(image, image, base, cancel)


def test_joint_contrast_and_brightness_formula():
    left = np.full((1, 1, 3), 64, dtype=np.uint8)
    right = np.full((1, 1, 3), 192, dtype=np.uint8)
    base = BUILTINS[9].as_custom()
    # Joint luminance midpoint 128: halfway toward that midpoint is 96/160.
    result = make_anaglyph(left, right, replace(base, contrast=.5))
    np.testing.assert_array_equal(result, [[[96, 160, 160]]])
    result = make_anaglyph(left, right, replace(base, contrast=0, brightness=.5))
    np.testing.assert_array_equal(result, [[[64, 64, 64]]])
    with np.errstate(over="raise", invalid="raise"):
        result = make_anaglyph(left, right, replace(base, contrast=1e30, brightness=1e30))
    np.testing.assert_array_equal(result, [[[0, 255, 255]]])


def ffmpeg_filter(number):
    ref = batch_definition(number)
    mode = ref["MATRIXMODE"]
    if mode == "iaian7":
        return ("format=gbrp16,split[l][r]; [l]crop=iw/2:ih:0:0,"
                "colorchannelmixer=0.4:0.3:0.3:0:0:0:0:0:0:0:0:0,"
                "lutrgb=r='gammaval(0.87)':g='gammaval(0.87)':b='gammaval(0.87)'[left]; "
                "[r]crop=iw/2:ih:iw/2:0,colorchannelmixer=0:0:0:0:0.1:0.9:0:0:0.1:0:0.9:0,"
                "lutrgb=r='gammaval(1.176)':g='gammaval(1.176)':b='gammaval(1.176)'[right]; "
                "[left][right]blend=all_mode=addition,"
                "colorchannelmixer=1.16:-0.08:-0.08:0:-0.02:1.04:-0.02:0:-0.02:-0.02:1.04:0,format=rgb24")
    linear = "zscale=transferin=iec61966-2-1:transfer=linear," if mode == "linear" else ""
    back = ",zscale=transferin=linear:transfer=iec61966-2-1" if mode == "linear" else ""
    clip = ",lutrgb=r='clip(val,0,maxval)':g='clip(val,0,maxval)':b='clip(val,0,maxval)'" if mode == "rendepth" else ""
    return (f"format=gbrp16,split[l][r]; [l]crop=iw/2:ih:0:0,{linear}colorchannelmixer={ref['MATRIX_LEFT']}{clip}[left]; "
            f"[r]crop=iw/2:ih:iw/2:0,{linear}colorchannelmixer={ref['MATRIX_RIGHT']}{clip}[right]; "
            f"[left][right]blend=all_mode=addition{back}{ref.get('POSTFIX','')},format=rgb24")


@pytest.mark.skipif(shutil.which("ffmpeg") is None, reason="FFmpeg is used only to validate the pinned reference")
@pytest.mark.parametrize("number", [n for n in range(1,19) if n != 16])
def test_against_batch_ffmpeg_filter(tmp_path, number):
    rng = np.random.default_rng(1975)
    l, r = (rng.integers(0,256,(24,64,3), dtype=np.uint8) for _ in range(2))
    src, out = tmp_path/"sbs.png", tmp_path/"reference.png"
    Image.fromarray(np.concatenate((l,r),axis=1)).save(src)
    p = subprocess.run([shutil.which("ffmpeg"),"-y","-v","error","-filter_complex_threads","1",
                        "-filter_threads","1","-i",str(src),"-vf",ffmpeg_filter(number),
                        "-frames:v","1",str(out)], capture_output=True, text=True, timeout=30)
    if number in {1,2,4,5,17,18} and "No such filter: 'zscale'" in p.stderr:
        pytest.skip("FFmpeg was built without zscale")
    assert p.returncode == 0, p.stderr
    with Image.open(out) as image:
        reference = np.array(image.convert("RGB"))
    actual = make_anaglyph(l,r,BUILTINS[number-1])
    difference = np.abs(actual.astype(int)-reference.astype(int))
    # Independent PNG comparison before JPEG. Integer 16-bit stages in FFmpeg
    # may differ slightly from the Float32 core, especially around clipping.
    assert difference.max() <= 2, (number, difference.max(), difference.mean())
