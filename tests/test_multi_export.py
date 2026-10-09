from dataclasses import replace
from pathlib import Path
from threading import Event
import numpy as np
from PIL import Image
import pytest
from anachroma.inputs import discover, load_pair
from anachroma.export import export_jobs, SizeSpec
from anachroma.matrices import BUILTINS
from anachroma.worker import run_jobs


def test_output_ancestor_same_folder_and_generated_exclusion(tmp_path):
    source = tmp_path/'input'; source.mkdir()
    Image.new('RGB', (32, 8)).save(source/'one.png')
    assert len(discover(source, True, (tmp_path,)).files) == 1
    Image.new('RGB', (16, 8)).save(source/'one_dubois.jpg')
    Image.new('RGB', (16, 8)).save(source/'one_mine.jpg')
    (source/'input').mkdir()
    Image.new('RGB', (16, 8)).save(source/'input'/'generated.png')
    result = discover(source, True, (source,), generated_suffixes=('mine',))
    assert {p.relative_to(source).as_posix() for p in result.files} == {'one.png', 'input/generated.png'}
    assert discover(source/'one_dubois.jpg', exclude=(source,)).files[result.selected].exists()


def test_multi_export_progress_errors_cancel_and_collisions(tmp_path, monkeypatch):
    source=tmp_path/'input';source.mkdir()
    Image.new('RGB',(32,8),(100,90,150)).save(source/'good.png')
    (source/'bad.png').write_bytes(b'bad image')
    inputs=discover(source)
    methods=(BUILTINS[0],BUILTINS[1])
    jobs=export_jobs(inputs, inputs.files, tmp_path/'output', methods)
    events=[]
    monkeypatch.setattr('anachroma.export.copy_metadata',lambda *a,**k:'')
    result=run_jobs(jobs,SizeSpec(),90,Event(),events.append)
    assert result.processed==2 and len(result.errors)==2
    assert [event[1] for event in events if event[0]=='batch_file_done']==[1,2,3,4]
    assert len(list((tmp_path/'output').glob('*.jpg')))==2
    with pytest.raises(ValueError):export_jobs(inputs,inputs.files,tmp_path/'output',(methods[0],replace(methods[1],suffix=methods[0].suffix)))
    cancel=Event(); cancel.set()
    assert run_jobs(jobs,SizeSpec(),90,cancel,events.append).cancelled
    # A selected image must not overwrite a different navigable input original.
    Image.new('RGB',(32,8)).save(source/'good_dubois.jpg')
    inputs=discover(source/'good.png')
    with pytest.raises(ValueError):export_jobs(inputs,(source/'good.png',),source,(BUILTINS[1],))


@pytest.mark.parametrize('extension', ['jpg','png','tiff','webp'])
@pytest.mark.parametrize('orientation', range(1,9))
def test_exif_orientation_exactly_once(tmp_path, extension, orientation):
    from PIL import ImageOps
    source=Image.fromarray(np.arange(24*16*3,dtype=np.uint8).reshape(16,24,3))
    exif=Image.Exif(); exif[274]=orientation
    path=tmp_path/f'image.{extension}';source.save(path,exif=exif)
    with Image.open(path) as image: expected=np.asarray(ImageOps.exif_transpose(image).convert('RGB'))
    left,right=load_pair(path)
    assert np.array_equal(np.concatenate((left,right),axis=1),expected)
