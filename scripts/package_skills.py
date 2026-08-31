#!/usr/bin/env python3
"""Build deterministic portable .skill archives from workspace packages."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import tempfile
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "root",
        nargs="?",
        type=Path,
        default=Path("."),
        help="Repository root (default: current directory)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Archive directory (default: knowledge-base/skills/dist)",
    )
    parser.add_argument(
        "--prune",
        action="store_true",
        help="Remove stale .skill files from the output directory",
    )
    return parser.parse_args()


def package_files(package_dir: Path) -> list[Path]:
    paths: list[Path] = []
    for path in sorted(package_dir.rglob("*")):
        if path.is_symlink():
            raise ValueError(f"symbolic link is not portable: {path}")
        if not path.is_file() or path.name == ".DS_Store" or "__pycache__" in path.parts:
            continue
        if path.suffix == ".pyc":
            continue
        paths.append(path)
    return paths


def write_archive(package_dir: Path, output_path: Path) -> int:
    package_name = package_dir.name
    files = package_files(package_dir)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        prefix=f".{package_name}.", suffix=".tmp", dir=output_path.parent, delete=False
    ) as temporary:
        temporary_path = Path(temporary.name)
    try:
        with ZipFile(temporary_path, "w", compression=ZIP_DEFLATED, compresslevel=9) as archive:
            for path in files:
                relative = path.relative_to(package_dir).as_posix()
                archive_path = f"{package_name}/{relative}"
                info = ZipInfo(archive_path, date_time=(2020, 1, 1, 0, 0, 0))
                info.compress_type = ZIP_DEFLATED
                info.create_system = 3
                info.external_attr = (path.stat().st_mode & 0o777) << 16
                archive.writestr(info, path.read_bytes())
        os.replace(temporary_path, output_path)
    finally:
        temporary_path.unlink(missing_ok=True)
    return len(files)


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    packages_root = root / "knowledge-base" / "skills" / "packages"
    output = (args.output or root / "knowledge-base" / "skills" / "dist").resolve()
    package_dirs = sorted(
        path for path in packages_root.iterdir() if path.is_dir() and (path / "SKILL.md").is_file()
    ) if packages_root.is_dir() else []
    output.mkdir(parents=True, exist_ok=True)

    expected = {f"{path.name}.skill" for path in package_dirs}
    if args.prune:
        for stale in sorted(output.glob("*.skill")):
            if stale.name not in expected:
                stale.unlink()

    total_files = 0
    for package_dir in package_dirs:
        archive_path = output / f"{package_dir.name}.skill"
        count = write_archive(package_dir, archive_path)
        total_files += count
        print(f"PACKAGED {package_dir.name} files={count}")
    print(f"PACKAGE_BUILD_OK packages={len(package_dirs)} files={total_files} output={output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
