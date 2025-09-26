import argparse
import json
import os
import re
import sys
from typing import Any, Dict, List


INVALID_WIN_CHARS = re.compile(r'[<>:"/\\|?*]')


def sanitize_name(name: str) -> str:
    """
    将名称清洗为 Windows 允许的目录名：
    - 去除非法字符 <>:"/\|?*
    - 去除首尾空白与句点
    - 将连续空白压缩为一个空格
    - 名称为空时回退为 'Unnamed'
    """
    name = INVALID_WIN_CHARS.sub(" ", str(name))
    name = re.sub(r"\s+", " ", name).strip().strip(".")
    return name or "Unnamed"


def create_directories_from_json(data: Dict[str, Any], base_dir: str) -> List[str]:
    created_paths: List[str] = []
    os.makedirs(base_dir, exist_ok=True)

    for platform_id, platform in data.items():
        platform_name = platform.get("gamingPlatformName") or f"platform_{platform_id}"
        platform_dir = os.path.join(base_dir, sanitize_name(platform_name))
        os.makedirs(platform_dir, exist_ok=True)
        created_paths.append(platform_dir)

        items = platform.get("items") or []
        for item in items:
            item_name = item.get("gamingItemName")
            if not item_name:
                continue
            item_dir = os.path.join(platform_dir, sanitize_name(item_name))
            os.makedirs(item_dir, exist_ok=True)
            created_paths.append(item_dir)

    return created_paths


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="根据 gaming_platforms.json 创建平台与游戏项目录")
    parser.add_argument(
        "--json",
        default="gaming_platforms.json",
        help="输入 JSON 文件路径（默认为 gaming_platforms.json）",
    )
    parser.add_argument(
        "--output-dir",
        default=".",
        help="创建目录的根路径（默认为当前目录）",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    try:
        with open(args.json, "r", encoding="utf-8") as f:
            data = json.load(f)
            if not isinstance(data, dict):
                print("JSON 根节点应为对象（以平台ID为键）", file=sys.stderr)
                sys.exit(2)
    except FileNotFoundError:
        print(f"未找到 JSON 文件: {args.json}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"JSON 解析失败: {e}", file=sys.stderr)
        sys.exit(1)

    created = create_directories_from_json(data, args.output_dir)
    print(f"已创建/确认存在 {len(created)} 个目录。根路径: {os.path.abspath(args.output_dir)}")


if __name__ == "__main__":
    main()

