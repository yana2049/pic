import argparse
import os
import shutil
from pathlib import Path
from typing import Dict, Iterable


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"}


def is_image(path: Path) -> bool:
    return path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS


def collect_folder_map(base_dir: Path, recursive: bool) -> Dict[str, Path]:
    """
    收集文件夹名称到路径的映射（小写作为匹配键）。
    - recursive=False: 仅收集 base_dir 的第一层子目录
    - recursive=True: 递归收集 base_dir 下的所有目录
    """
    folder_map: Dict[str, Path] = {}
    if recursive:
        for p in base_dir.rglob("*"):
            if p.is_dir():
                folder_map[p.name.lower()] = p
    else:
        for p in base_dir.iterdir():
            if p.is_dir():
                folder_map[p.name.lower()] = p
    return folder_map


def iter_images(source_dir: Path, recursive: bool) -> Iterable[Path]:
    if recursive:
        yield from (p for p in source_dir.rglob("*") if is_image(p))
    else:
        yield from (p for p in source_dir.iterdir() if is_image(p))


def make_non_overwriting_path(target_dir: Path, filename: str) -> Path:
    """
    若目标目录已存在同名文件，则生成不覆盖的新文件名：name_1.ext, name_2.ext ...
    """
    candidate = target_dir / filename
    if not candidate.exists():
        return candidate
    stem = Path(filename).stem
    suffix = Path(filename).suffix
    index = 1
    while True:
        new_name = f"{stem}_{index}{suffix}"
        candidate = target_dir / new_name
        if not candidate.exists():
            return candidate
        index += 1


def move_images(base_dir: Path, source_dir: Path, recursive_folders: bool, recursive_images: bool) -> int:
    folder_map = collect_folder_map(base_dir, recursive=recursive_folders)
    moved = 0
    for img in iter_images(source_dir, recursive=recursive_images):
        key = img.stem.lower()
        dest_folder = folder_map.get(key)
        if not dest_folder:
            continue
        # 若目标资料夹内已存在任何图片，则跳过，避免重复图片
        try:
            has_image = any(
                p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS
                for p in dest_folder.iterdir()
            )
        except FileNotFoundError:
            # 目标目录在此刻不存在则视为无图片
            has_image = False
        if has_image:
            print(f"Skip: 已存在图片，跳过 -> {dest_folder}")
            continue
        dest_path = make_non_overwriting_path(dest_folder, img.name)
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(img), str(dest_path))
        moved += 1
        print(f"Moved: {img} -> {dest_path}")
    return moved


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "根据图片文件名与目录名相同的规则，将图片移动到匹配的目录内。"
        )
    )
    parser.add_argument(
        "--base-dir",
        type=str,
        default=r"C:\\Users\\USER\\Desktop\\picture\\gamingType\\4\\PG电子",
        help="用于匹配的目录（包含目标子目录，例如各游戏项目录）",
    )
    parser.add_argument(
        "--source-dir",
        type=str,
        default=None,
        help="图片所在目录（默认等于 --base-dir）",
    )
    parser.add_argument(
        "--recursive-folders",
        action="store_true",
        help="递归收集 base-dir 下所有层级的子目录用于匹配",
    )
    parser.add_argument(
        "--recursive-images",
        action="store_true",
        help="递归扫描 source-dir 下的所有图片",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    base_dir = Path(args.base_dir)
    source_dir = Path(args.source_dir) if args.source_dir else base_dir

    if not base_dir.exists():
        raise SystemExit(f"base-dir 不存在: {base_dir}")
    if not source_dir.exists():
        raise SystemExit(f"source-dir 不存在: {source_dir}")

    moved = move_images(
        base_dir=base_dir,
        source_dir=source_dir,
        recursive_folders=args.recursive_folders,
        recursive_images=args.recursive_images,
    )
    print(f"完成，移动了 {moved} 个文件。")


if __name__ == "__main__":
    main()


