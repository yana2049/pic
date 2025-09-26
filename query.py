import argparse
import json
import sys
from typing import Any, Dict, Iterable, List, Optional

import requests


def find_dicts_with_keys(root: Any, required_keys: Iterable[str]) -> List[Dict[str, Any]]:
    """
    深度优先在任意 JSON 结构中查找同时包含 required_keys 的字典集合。
    """
    matches: List[Dict[str, Any]] = []

    def _walk(node: Any) -> None:
        if isinstance(node, dict):
            if all(key in node for key in required_keys):
                matches.append(node)  # type: ignore[arg-type]
            for value in node.values():
                _walk(value)
        elif isinstance(node, list):
            for item in node:
                _walk(item)

    _walk(root)
    return matches


def fetch_platforms_for_type(
    base_url: str,
    gaming_type: int,
    equipment_id: int = 0,
    page_no: int = 1,
    page_size: int = 150,
    headers: Optional[Dict[str, str]] = None,
    timeout: float = 15.0,
) -> List[Dict[str, Any]]:
    """
    调用接口按 gamingType 拉取平台数据，返回原始字典列表。
    """
    params = {
        "equipmentId": equipment_id,
        "pageNo": page_no,
        "pageSize": page_size,
        "gamingType": gaming_type,
    }
    resp = requests.get(base_url, params=params, headers=headers, timeout=timeout)
    resp.raise_for_status()
    data = resp.json()

    # 在返回 JSON 中查找包含所需字段的字典
    required = {"gamingPlatformCode", "gamingPlatformId", "gamingType", "gamingPlatformName"}
    matches = find_dicts_with_keys(data, required)
    return matches


def fetch_items_for_platform(
    base_url: str,
    equipment_id: int,
    gaming_type: int,
    platform_code: str,
    page_no: int = 1,
    page_size: int = 500,
    headers: Optional[Dict[str, str]] = None,
    timeout: float = 15.0,
) -> List[Dict[str, Any]]:
    """
    调用接口按平台与类型拉取游戏项数据，返回原始字典列表。
    """
    params = {
        "equipmentId": equipment_id,
        "pageNo": page_no,
        "pageSize": page_size,
        "gamingType": gaming_type,
        "platformCode": platform_code,
    }
    resp = requests.get(base_url, params=params, headers=headers, timeout=timeout)
    resp.raise_for_status()
    data = resp.json()

    required = {"gamingItemName", "gamingItemCode", "gamingType"}
    matches = find_dicts_with_keys(data, required)
    return matches


def build_platform_dict(
    base_url: str,
    gaming_types: Iterable[int],
    equipment_id: int,
    page_no: int,
    page_size: int,
    items_base_url: str,
    items_page_no: int,
    items_page_size: int,
    headers: Optional[Dict[str, str]] = None,
) -> Dict[str, Dict[str, Any]]:
    """
    聚合多个 gamingType 的结果，生成以 gamingPlatformId 为键的字典。
    值仅保留 gamingPlatformCode、gamingPlatformId、gamingType、gamingPlatformName 四个字段。
    对于每个平台，若有游戏项返回，则在该平台对象下新增 items 列表，
    每个元素包含 gamingItemName、gamingItemCode、gamingType、gamingItemId。
    """
    result: Dict[str, Dict[str, Any]] = {}
    for gt in gaming_types:
        items = fetch_platforms_for_type(
            base_url,
            gt,
            equipment_id=equipment_id,
            page_no=page_no,
            page_size=page_size,
            headers=headers,
        )
        for item in items:
            try:
                platform_id = str(item["gamingPlatformId"])  # 统一为字符串 key
                platform_entry: Dict[str, Any] = {
                    "gamingPlatformCode": item["gamingPlatformCode"],
                    "gamingPlatformId": item["gamingPlatformId"],
                    "gamingType": item["gamingType"],
                    "gamingPlatformName": item["gamingPlatformName"],
                }
                # 二级接口：按平台与类型拉取游戏项
                try:
                    game_items = fetch_items_for_platform(
                        base_url=items_base_url,
                        equipment_id=equipment_id,
                        gaming_type=platform_entry["gamingType"],
                        platform_code=platform_entry["gamingPlatformCode"],
                        page_no=items_page_no,
                        page_size=items_page_size,
                        headers=headers,
                    )
                    if game_items:
                        platform_entry["items"] = [
                            {
                                "gamingItemName": gi["gamingItemName"],
                                "gamingItemCode": gi["gamingItemCode"],
                                "gamingType": gi["gamingType"],
                                "gamingItemId": gi.get("gamingItemId", ""),  # 添加gamingItemId字段
                            }
                            for gi in game_items
                            if all(k in gi for k in ("gamingItemName", "gamingItemCode", "gamingType"))
                        ]
                except requests.RequestException:
                    # 忽略子请求错误，不中断主流程
                    pass

                result[platform_id] = platform_entry
            except KeyError:
                # 若个别项缺字段则跳过
                continue
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="抓取平台数据并保存为 JSON 字典（默认 gamingType=1,2,3,4,5,6,8，pageNo=1，pageSize=150）"
    )
    parser.add_argument(
        "--base-url",
        default=(
            "http://admin.btest4wohjelay.com:3000/"
            "adminsystem/server/newgamemanager/findByGamePlatfromPageResult"
        ),
        help="接口基础 URL（无需附带查询参数）",
    )
    parser.add_argument(
        "--equipment-id", type=int, default=0, help="equipmentId 参数，默认 0"
    )
    parser.add_argument(
        "--types",
        type=str,
        default="1,2,3,4,5,6,8",
        help="gamingType 范围或列表，默认 1,2,3,4,5,6,8（可用 1-8 或 1,2,3）",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="gaming_platforms.json",
        help="输出 JSON 文件路径",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=15.0,
        help="请求超时时间（秒）",
    )
    # 平台分页参数
    parser.add_argument("--page-no", type=int, default=1, help="页码，默认 1")
    parser.add_argument("--page-size", type=int, default=150, help="分页大小，默认 150")
    # 游戏项接口与分页参数
    parser.add_argument(
        "--items-base-url",
        default=(
            "http://admin.btest4wohjelay.com:3000/"
            "adminsystem/server/newgamemanager/findGameItemPageResult"
        ),
        help="游戏项接口基础 URL（无需附带查询参数）",
    )
    parser.add_argument("--items-page-no", type=int, default=1, help="游戏项页码，默认 1")
    parser.add_argument(
        "--items-page-size", type=int, default=500, help="游戏项分页大小，默认 500"
    )
    return parser.parse_args()


def parse_types(spec: str) -> List[int]:
    spec = spec.strip()
    if "-" in spec:
        start_s, end_s = spec.split("-", 1)
        start = int(start_s)
        end = int(end_s)
        return list(range(start, end + 1))
    parts = [p.strip() for p in spec.split(",") if p.strip()]
    return [int(p) for p in parts]


def main() -> None:
    args = parse_args()
    gaming_types = parse_types(args.types)

    # 使用你提供的请求头
    headers: Dict[str, str] = {
        "Authorization": "9999e327-1b0c-4950-beae-c41ed78658ab",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-TW,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6,zh-CN;q=0.5",
    }

    try:
        platform_dict = build_platform_dict(
            base_url=args.base_url,
            gaming_types=gaming_types,
            equipment_id=args.equipment_id,
            page_no=args.page_no,
            page_size=args.page_size,
            items_base_url=args.items_base_url,
            items_page_no=args.items_page_no,
            items_page_size=args.items_page_size,
            headers=headers,
        )
    except requests.HTTPError as e:
        print(f"HTTP 错误: {e}", file=sys.stderr)
        sys.exit(2)
    except requests.RequestException as e:
        print(f"请求失败: {e}", file=sys.stderr)
        sys.exit(3)

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(platform_dict, f, ensure_ascii=False, indent=2)

    print(
        f"已保存 {len(platform_dict)} 条记录到 {args.output}，"
        f"gamingType: {gaming_types}，equipmentId: {args.equipment_id}"
    )


if __name__ == "__main__":
    main()


