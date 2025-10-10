#!/usr/bin/env python3
import hashlib, json, zipfile
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "Flowstate-AI_Codex_v1.0_Master.zip"

def sha256(p: Path) -> str:
    import hashlib
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024*1024), b""):
            h.update(chunk)
    return h.hexdigest()

def add_dir(zf, base: Path, arc_prefix: Path):
    for p in sorted(base.rglob("*")):
        if p.is_file():
            zf.write(p, arc_prefix / p.relative_to(base))

if __name__ == "__main__":
    if OUT.exists(): OUT.unlink()
    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as zf:
        add_dir(zf, ROOT, Path("Flowstate-AI"))
    (ROOT / "Flowstate-AI_Codex_v1.0_Master_SHA256.txt").write_text(
        f"{sha256(OUT)}  {OUT.name}\n", encoding="utf-8"
    )
    manifest = {
        "generated_utc": datetime.utcnow().isoformat()+"Z",
        "algorithm": "SHA-256",
        "files": [{"path": OUT.name, "sha256": sha256(OUT), "size": OUT.stat().st_size}],
    }
    (ROOT / "MANIFEST.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
