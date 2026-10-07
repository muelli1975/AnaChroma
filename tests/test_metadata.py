from pathlib import Path
import json
import subprocess
from PIL import Image
import pytest

from anachroma.export import SizeSpec, export_image
from anachroma.matrices import BUILTINS
from anachroma.resources import find_tool


@pytest.mark.skipif(find_tool("exiftool") is None, reason="External ExifTool installation required")
def test_real_exiftool_orientation_dimensions_profile_and_artist(tmp_path):
    source=tmp_path/"sbs.jpg";target=tmp_path/"anaglyph.jpg"
    image=Image.new("RGB",(6,4),(70,120,180))
    exif=Image.Exif();exif[274]=6;exif[315]="Christoph Test"
    image.save(source,exif=exif)
    assert export_image(source,target,BUILTINS[9],SizeSpec())==""
    tool=find_tool("exiftool")
    p=subprocess.run([str(tool),"-j","-Orientation","-ExifImageWidth","-ExifImageHeight", "-Artist",
                      "-PreviewImage","-ThumbnailImage",str(target)],capture_output=True,text=True,check=True)
    tags=json.loads(p.stdout)[0]
    assert tags["Artist"]=="Christoph Test"
    assert tags["ExifImageWidth"]==2 and tags["ExifImageHeight"]==6
    assert not any(k in tags for k in ("Orientation","PreviewImage","ThumbnailImage"))
    with Image.open(target) as result:
        assert result.size==(2,6) and result.info.get("icc_profile")
