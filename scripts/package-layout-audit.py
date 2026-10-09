import hashlib, json, pathlib, subprocess, tarfile, zipfile
plans = json.loads(pathlib.Path("scripts/package-layout-audit.json").read_text())
for plan in plans:
    directory = pathlib.Path("downloads") / plan["app"]
    directory.mkdir(parents=True, exist_ok=True)
    for asset in plan["assets"]:
        subprocess.run(["gh", "release", "download", plan["tag"], "--repo", plan["repo"], "--dir", str(directory), "--pattern", asset["name"]], check=True)
        path = directory / asset["name"]
        digest = "sha256:" + hashlib.file_digest(path.open("rb"), "sha256").hexdigest()
        assert digest == asset["digest"], (path, digest)
        if path.suffix == ".zip":
            with zipfile.ZipFile(path) as archive:
                names = archive.namelist()
        else:
            with tarfile.open(path) as archive:
                names = archive.getnames()
        roots = sorted({name.split("/")[0] for name in names})
        programs = sorted({name for name in names if name.lower().endswith(".exe") and name.count("/") <= 2})
        print(json.dumps({"app":plan["app"],"asset":asset["name"],"roots":roots,"programs":programs,"entries":len(names)},ensure_ascii=False), flush=True)
