#!/usr/bin/env python3
"""口播脚本校验工具：检查字数范围和禁用词。

用法:
    python3 validate_script.py <脚本文本文件> [--duration 15]
    echo "脚本内容" | python3 validate_script.py --stdin [--duration 15]

校验规则:
    - 15秒视频: 75-90字（标准），不超过105字（高密度）
    - 30秒视频: 150-180字
    - 检查禁用词清单
"""
import sys
import argparse
import re

BANNED_WORDS = [
    "宝子", "家人们", "姐妹们", "铁子们",
    "绝绝子", "yyds", "YYDS", "封神", "天花板",
    "闭眼入", "无脑冲", "冲就完了",
    "谁懂啊", "真的会谢", "我不允许",
    "宝藏", "神器",
]

def count_chinese_chars(text):
    """统计中文字符数（不含标点、空格、英文）。"""
    return len(re.findall(r'[\u4e00-\u9fff]', text))

def check_banned_words(text):
    """检查禁用词，返回命中列表。"""
    found = []
    for word in BANNED_WORDS:
        if word.lower() in text.lower():
            found.append(word)
    return found

def validate(text, duration=15):
    """校验脚本，返回 (passed, messages)。"""
    messages = []
    passed = True
    char_count = count_chinese_chars(text)

    # 字数校验
    if duration == 15:
        std_min, std_max, hard_max = 75, 90, 105
    elif duration == 30:
        std_min, std_max, hard_max = 150, 180, 210
    else:
        # 按 5-6 字/秒估算
        std_min = int(duration * 5)
        std_max = int(duration * 6)
        hard_max = int(duration * 7)

    if char_count < std_min:
        messages.append(f"[WARN] 字数 {char_count} 偏少，标准范围 {std_min}-{std_max} 字")
    elif char_count > hard_max:
        messages.append(f"[ERROR] 字数 {char_count} 超出上限 {hard_max} 字，必须删减")
        passed = False
    elif char_count > std_max:
        messages.append(f"[WARN] 字数 {char_count} 偏多，标准范围 {std_min}-{std_max} 字，高密度上限 {hard_max}")
    else:
        messages.append(f"[OK] 字数 {char_count}，在标准范围 {std_min}-{std_max} 内")

    # 禁用词校验
    banned = check_banned_words(text)
    if banned:
        messages.append(f"[ERROR] 发现禁用词: {', '.join(banned)}，必须替换")
        passed = False
    else:
        messages.append("[OK] 未发现禁用词")

    return passed, messages

def main():
    parser = argparse.ArgumentParser(description="口播脚本校验工具")
    parser.add_argument("file", nargs="?", help="脚本文本文件路径")
    parser.add_argument("--stdin", action="store_true", help="从标准输入读取脚本")
    parser.add_argument("--duration", type=int, default=15, help="视频时长（秒），默认15")
    args = parser.parse_args()

    if args.stdin:
        text = sys.stdin.read()
    elif args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            text = f.read()
    else:
        parser.print_help()
        sys.exit(1)

    text = text.strip()
    if not text:
        print("[ERROR] 脚本内容为空")
        sys.exit(1)

    passed, messages = validate(text, args.duration)
    for msg in messages:
        print(msg)

    print(f"\n校验结果: {'通过' if passed else '未通过'}")
    sys.exit(0 if passed else 1)

if __name__ == "__main__":
    main()
