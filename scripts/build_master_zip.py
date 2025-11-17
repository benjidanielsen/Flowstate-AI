"""Utility script to build a master ZIP archive of the repository.

This script walks the repository root, collects all files, and stores them in
an archive alongside a manifest and checksum file. Directories that correspond
to build artefacts or other large, generated content (e.g. ``node_modules``)
are automatically excluded from the archive to keep the bundle small and
reproducible.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, List
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = ROOT / "archive" / "packages"
DEFAULT_ARCHIVE_NAME = "Flowstate-AI-master.zip"

IGNORE_PARTS = {
    ".git",
    ".hg",
    ".svn",
    ".tox",
    ".venv",
    "venv",
    "env",
    "__pycache__",
    "archive",
    "node_modules",
    "bower_components",
    "dist",
    "build",
    "builds",
    "site",
    "coverage",
    ".pytest_cache",
    ".mypy_cache",
    "tmp",
    "temp",
    "logs",
    "__generated__",
}
IGNORE_FILE_NAMES = {".DS_Store"}


def should_ignore(path: Path) -> bool:
    """Return ``True`` if the given path should be skipped.

    The check is performed on the relative path components so that any nested
    directory with one of the ignored names is skipped entirely.
    """

    parts = path.parts
    if any(part in IGNORE_PARTS for part in parts):
        return True
    if path.name in IGNORE_FILE_NAMES:
        return True
    return False


def add_dir(zf: ZipFile, directory: Path, manifest: List[dict[str, object]]) -> None:
    """Add a directory to the ZIP file, skipping ignored paths."""

    for entry in sorted(directory.iterdir()):
        relative_path = entry.relative_to(ROOT)
        if should_ignore(relative_path):
            # Skip ignored directories and files entirely.
            continue
        if entry.is_symlink():
            # Skip symlinks to avoid broken references in the archive.
            continue
        if entry.is_dir():
            add_dir(zf, entry, manifest)
        elif entry.is_file():
            arcname = relative_path.as_posix()
            zf.write(entry, arcname)
            manifest.append(
                {
                    "path": arcname,
                    "size": entry.stat().st_size,
                    "modified": datetime.fromtimestamp(entry.stat().st_mtime, timezone.utc).isoformat(),
                }
            )


def compute_sha256(file_path: Path, chunk_size: int = 1024 * 1024) -> str:
    sha256 = hashlib.sha256()
    with file_path.open("rb") as fp:
        for chunk in iter(lambda: fp.read(chunk_size), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def write_manifest(manifest_path: Path, entries: Iterable[dict[str, object]]) -> None:
    entries_list = sorted(entries, key=lambda item: item["path"])
    data = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "file_count": len(entries_list),
        "files": entries_list,
    }
    manifest_path.write_text(json.dumps(data, indent=2))


def write_checksum(checksum_path: Path, archive_path: Path) -> None:
    checksum = compute_sha256(archive_path)
    checksum_path.write_text(f"{checksum}  {archive_path.name}\n")


def build_master_zip(output_dir: Path, archive_name: str) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    archive_path = output_dir / archive_name
    manifest: List[dict[str, object]] = []

    with ZipFile(archive_path, "w", compression=ZIP_DEFLATED) as zf:
        add_dir(zf, ROOT, manifest)

    manifest_path = archive_path.with_suffix(".manifest.json")
    checksum_path = archive_path.with_suffix(".sha256")

    write_manifest(manifest_path, manifest)
    write_checksum(checksum_path, archive_path)

    return archive_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build the Flowstate master ZIP archive")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory where the archive and accompanying files will be written.",
    )
    parser.add_argument(
        "--name",
        default=DEFAULT_ARCHIVE_NAME,
        help="Name of the archive file (defaults to Flowstate-AI-master.zip)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    archive_path = build_master_zip(args.output_dir, args.name)
    print(f"Archive written to {archive_path}")
    print(f"Manifest written to {archive_path.with_suffix('.manifest.json')}")
    print(f"Checksum written to {archive_path.with_suffix('.sha256')}")


if __name__ == "__main__":
    main()
