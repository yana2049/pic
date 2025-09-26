import argparse
import json
import os
from pathlib import Path
from typing import Dict, Optional, Tuple


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"}


def is_image(path: Path) -> bool:
    """检查文件是否为图片"""
    return path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS


def load_gaming_data(json_path: Path, gaming_type_filter: Optional[str] = None) -> Dict[str, int]:
    """
    从JSON文件加载游戏数据，返回游戏名称到gamingItemId的映射
    """
    gaming_map: Dict[str, int] = {}
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 遍历所有平台
        for platform_id, platform_data in data.items():
            if 'items' in platform_data:
                # 遍历每个平台下的游戏项目
                for item in platform_data['items']:
                    gaming_item_name = item.get('gamingItemName', '').strip()
                    gaming_item_id = item.get('gamingItemId')
                    gaming_type = item.get('gamingType', '').strip()
                    
                    # 如果设置了gamingType过滤，只加载匹配的游戏
                    if gaming_type_filter and gaming_type != gaming_type_filter:
                        continue
                    
                    if gaming_item_name and gaming_item_id:
                        # 使用小写名称作为匹配键，避免大小写问题
                        gaming_map[gaming_item_name.lower()] = gaming_item_id
                        # 也保存原始名称，以防需要精确匹配
                        gaming_map[gaming_item_name] = gaming_item_id
        
        filter_info = f" (gamingType: {gaming_type_filter})" if gaming_type_filter else ""
        print(f"已加载 {len(gaming_map)} 个游戏项目{filter_info}")
        return gaming_map
        
    except FileNotFoundError:
        print(f"错误：找不到JSON文件 {json_path}")
        return {}
    except json.JSONDecodeError as e:
        print(f"错误：JSON文件格式错误 - {e}")
        return {}


def find_matching_gaming_id(image_name: str, gaming_map: Dict[str, int]) -> Optional[int]:
    """
    根据图片名称查找匹配的gamingItemId
    支持多种匹配策略：
    1. 精确匹配（去除扩展名后）
    2. 包含匹配
    3. 模糊匹配
    """
    # 去除扩展名
    name_without_ext = Path(image_name).stem
    
    # 策略1：精确匹配（小写）
    if name_without_ext.lower() in gaming_map:
        return gaming_map[name_without_ext.lower()]
    
    # 策略2：精确匹配（原始大小写）
    if name_without_ext in gaming_map:
        return gaming_map[name_without_ext]
    
    # 策略3：包含匹配（图片名称包含游戏名称）
    for gaming_name, gaming_id in gaming_map.items():
        if gaming_name.lower() in name_without_ext.lower():
            return gaming_id
    
    # 策略4：包含匹配（游戏名称包含图片名称）
    for gaming_name, gaming_id in gaming_map.items():
        if name_without_ext.lower() in gaming_name.lower():
            return gaming_id
    
    return None


def rename_images_by_gaming_id(source_dir: Path, gaming_map: Dict[str, int], dry_run: bool = False) -> int:
    """
    根据JSON数据重命名图片
    """
    renamed = 0
    
    for img_path in source_dir.iterdir():
        if not is_image(img_path):
            continue
        
        gaming_id = find_matching_gaming_id(img_path.name, gaming_map)
        if gaming_id is None:
            print(f"未找到匹配: {img_path.name}")
            continue
        
        # 构建新的文件名：gamingItemId + 原扩展名
        new_name = f"{gaming_id}{img_path.suffix}"
        new_path = img_path.parent / new_name
        
        # 检查新文件名是否已存在
        if new_path.exists():
            print(f"跳过: 目标文件已存在 {new_path}")
            continue
        
        if dry_run:
            print(f"[预览] {img_path.name} -> {new_name}")
        else:
            try:
                img_path.rename(new_path)
                print(f"重命名: {img_path.name} -> {new_name}")
            except Exception as e:
                print(f"错误: 无法重命名 {img_path.name} - {e}")
                continue
        
        renamed += 1
    
    return renamed


def parse_args():
    parser = argparse.ArgumentParser(
        description="根据JSON文件中的游戏信息重命名图片为对应的gamingItemId"
    )
    parser.add_argument(
        "--source-dir",
        type=str,
        default=r"C:\Users\USER\Desktop\picture\gamingType\4\YGR电子",
        help="包含图片的目录"
    )
    parser.add_argument(
        "--json-file",
        type=str,
        default="gaming_platforms.json",
        help="包含游戏数据的JSON文件路径"
    )
    parser.add_argument(
        "--gaming-type",
        type=str,
        default="4",
        help="只匹配指定gamingType的游戏（例如：'4' 表示只匹配PG电子游戏）"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="预览模式，只显示将要进行的重命名操作，不实际执行"
    )
    return parser.parse_args()


def main():
    args = parse_args()
    
    source_dir = Path(args.source_dir)
    json_file = Path(args.json_file)
    
    if not source_dir.exists():
        print(f"错误：源目录不存在 {source_dir}")
        return
    
    if not json_file.exists():
        print(f"错误：JSON文件不存在 {json_file}")
        return
    
    print(f"源目录: {source_dir}")
    print(f"JSON文件: {json_file}")
    print(f"游戏类型过滤: {args.gaming_type if args.gaming_type else '无'}")
    print(f"模式: {'预览模式' if args.dry_run else '执行模式'}")
    print("-" * 50)
    
    # 加载游戏数据
    gaming_map = load_gaming_data(json_file, args.gaming_type)
    if not gaming_map:
        print("无法加载游戏数据，退出")
        return
    
    # 重命名图片
    renamed_count = rename_images_by_gaming_id(source_dir, gaming_map, args.dry_run)
    
    print("-" * 50)
    if args.dry_run:
        print(f"预览完成，将重命名 {renamed_count} 个文件")
    else:
        print(f"完成，成功重命名 {renamed_count} 个文件")


if __name__ == "__main__":
    main()
