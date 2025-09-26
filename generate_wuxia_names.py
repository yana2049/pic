import random


def generate_wuxia_names(count: int = 100) -> list[str]:
    """
    生成武侠风格的名字
    """
    # 常见姓氏
    surnames = [
        "李", "王", "张", "刘", "陈", "杨", "赵", "黄", "周", "吴",
        "徐", "孙", "胡", "朱", "高", "林", "何", "郭", "马", "罗",
        "梁", "宋", "郑", "谢", "韩", "唐", "冯", "于", "董", "萧",
        "程", "曹", "袁", "邓", "许", "傅", "沈", "曾", "彭", "吕",
        "苏", "卢", "蒋", "蔡", "贾", "丁", "魏", "薛", "叶", "阎",
        "余", "潘", "杜", "戴", "夏", "钟", "汪", "田", "任", "姜",
        "范", "方", "石", "姚", "谭", "廖", "邹", "熊", "金", "陆",
        "郝", "孔", "白", "崔", "康", "毛", "邱", "秦", "江", "史",
        "顾", "侯", "邵", "孟", "龙", "万", "段", "雷", "钱", "汤",
        "尹", "黎", "易", "常", "武", "乔", "贺", "赖", "龚", "文"
    ]
    
    # 武侠风格的名字用字
    name_chars = [
        # 武功相关
        "剑", "刀", "枪", "拳", "掌", "腿", "指", "爪", "鞭", "锤",
        "棍", "斧", "钩", "叉", "戟", "矛", "盾", "弓", "箭", "弩",
        # 气势相关
        "天", "地", "山", "海", "风", "云", "雷", "电", "火", "水",
        "龙", "虎", "凤", "鹰", "鹤", "豹", "狼", "蛇", "鱼", "鸟",
        # 品德相关
        "仁", "义", "礼", "智", "信", "勇", "忠", "孝", "节", "廉",
        "正", "直", "刚", "毅", "温", "良", "恭", "俭", "让", "和",
        # 自然相关
        "春", "夏", "秋", "冬", "日", "月", "星", "辰", "花", "草",
        "松", "竹", "梅", "兰", "菊", "荷", "柳", "枫", "雪", "霜",
        # 动作相关
        "飞", "翔", "跃", "腾", "奔", "驰", "行", "走", "立", "坐",
        "卧", "起", "来", "去", "进", "退", "升", "降", "开", "合",
        # 其他武侠常用字
        "青", "白", "红", "紫", "金", "银", "铜", "铁", "石", "玉",
        "光", "影", "声", "色", "香", "味", "形", "神", "气", "力"
    ]
    
    # 生成名字
    names = []
    used_names = set()
    
    while len(names) < count:
        # 随机选择姓氏
        surname = random.choice(surnames)
        
        # 生成1-2个字的名字
        name_length = random.choice([1, 2])
        if name_length == 1:
            given_name = random.choice(name_chars)
        else:
            given_name = random.choice(name_chars) + random.choice(name_chars)
        
        full_name = surname + given_name
        
        # 避免重复名字
        if full_name not in used_names:
            used_names.add(full_name)
            names.append(full_name)
    
    return names


def main():
    print("=== 武侠名字生成器 ===\n")
    
    # 生成100个名字
    wuxia_names = generate_wuxia_names(100)
    
    # 按每行5个名字显示
    for i in range(0, len(wuxia_names), 5):
        row = wuxia_names[i:i+5]
        print("  ".join(f"{name:>4}" for name in row))
    
    print(f"\n共生成 {len(wuxia_names)} 个武侠名字")
    
    # 保存到文件
    with open("wuxia_names.txt", "w", encoding="utf-8") as f:
        f.write("武侠名字列表\n")
        f.write("=" * 20 + "\n\n")
        for i, name in enumerate(wuxia_names, 1):
            f.write(f"{i:3d}. {name}\n")
    
    print("名字已保存到 wuxia_names.txt 文件")


if __name__ == "__main__":
    main()
