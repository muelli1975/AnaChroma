from pathlib import Path
from queue import Queue, Empty
from threading import Event, Timer
import sys
import time
import numpy as np
from PIL import Image
import pytest

from anachroma.cielab import make_cielab
from anachroma.engine import Cancelled
from anachroma.processes import run_tool
from anachroma.worker import PreviewWorker
from anachroma.matrices import BUILTINS


def test_external_process_cancel_timeout_and_pipe_volume():
    code,text=run_tool([sys.executable,"-c","print('x'*200000)"],None,10)
    assert code==0 and len(text)<=8192
    cancel=Event()
    timer=Timer(.1,cancel.set);timer.start()
    with pytest.raises(Cancelled):
        run_tool([sys.executable,"-c","import time;time.sleep(20)"],cancel,10)
    timer.join()
    with pytest.raises(TimeoutError):
        run_tool([sys.executable,"-c","import time;time.sleep(20)"],None,.1)


def test_cielab_has_separate_inputs_and_cleans_temporary_files(monkeypatch):
    paths=[]
    def fake(args,cancel,timeout):
        _,l,r,flag,out=args
        assert flag=="-o"
        with Image.open(l) as left, Image.open(r) as right:
            assert left.size==right.size==(8,4)
            assert left.getpixel((0,0))!=(right.getpixel((0,0)))
            left.save(out)
        paths.append(Path(l).parent)
        return 0,""
    monkeypatch.setattr("anachroma.cielab.run_tool",fake)
    l=np.zeros((4,8,3),dtype=np.uint8); r=np.full_like(l,255)
    assert make_cielab(l,r,executable=Path("cielab-test")).size==(8,4)
    assert paths and not paths[0].exists()


def test_preview_only_returns_latest_request_and_reuses_pair(tmp_path,monkeypatch):
    path=tmp_path/"sbs.png";Image.new("RGB",(16,4)).save(path)
    entered,release=Event(),Event()
    calls=[]
    from anachroma import worker
    original=worker.make_anaglyph
    def delayed(l,r,m,cancel):
        calls.append(m.id)
        if len(calls)==1:
            entered.set(); assert release.wait(5)
        return original(l,r,m,cancel)
    monkeypatch.setattr(worker,"make_anaglyph",delayed)
    events=Queue(); preview=PreviewWorker(events)
    try:
        preview.request(1,path,BUILTINS[0])
        assert entered.wait(5)
        preview.request(2,path,BUILTINS[1])
        preview.request(3,path,BUILTINS[9])
        release.set()
        event=events.get(timeout=5)
        assert event[0:2]==("preview",3)
        assert calls==[BUILTINS[0].id,BUILTINS[9].id]
        with pytest.raises(Empty): events.get(timeout=.1)
    finally:
        release.set(); preview.close(); preview.thread.join(5)
        assert not preview.thread.is_alive()
