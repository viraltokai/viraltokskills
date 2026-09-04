#!/usr/bin/env python3
"""Validate a Viraltok Seedance five-section prompt."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


SECTIONS = ("主体", "风格", "时间线", "BGM", "限制")
TIME_TOKEN = r"(?:\d{1,2}:\d{1,2}(?::\d{1,2})?(?:\.\d+)?|\d+(?:\.\d+)?)"
TIME_RANGE = re.compile(
    rf"(?P<start>{TIME_TOKEN})\s*(?:秒|s)?\s*[—–~～-]\s*"
    rf"(?P<end>{TIME_TOKEN})\s*(?:秒|s)?", re.IGNORECASE
)
SECTION_RE = re.compile(
    r"^\s*(?:#{1,6}\s*)?(?:【\s*)?(主体|风格|时间线|BGM|限制)(?:\s*】)?\s*:?[ \t]*$",
    re.IGNORECASE,
)
MODULE_RE = re.compile(
    r"^\s*(?:#{1,6}\s*)?【\s*(?P<bracket>[^】]+?)\s*】\s*:?[ \t]*$"
    r"|^\s*#{1,6}\s*(?P<markdown>.+?)\s*$",
    re.IGNORECASE,
)
DIALOGUE_RE = re.compile(r"对白|台词|说(?:[：:]|出|道|着)?\s*[“‘]", re.IGNORECASE)
NO_DIALOGUE_RE = re.compile(r"(?:无|没有)\s*(?:任何|额外)?(?:对白|台词)", re.IGNORECASE)
BRANDS = ("fanta", "芬达", "coca-cola", "可口可乐", "pepsi", "百事", "sprite", "雪碧", "mcdonald", "麦当劳", "kfc", "肯德基", "logitech", "罗技")


def add(findings: list[dict[str, str]], level: str, code: str, message: str) -> None:
    findings.append({"level": level, "code": code, "message": message})


def parse_time(value: str) -> float | None:
    if ":" not in value:
        return float(value)
    parts = [float(part) for part in value.split(":")]
    if len(parts) == 2:
        minutes, seconds = parts
        return None if seconds >= 60 else minutes * 60 + seconds
    hours, minutes, seconds = parts
    return None if minutes >= 60 or seconds >= 60 else hours * 3600 + minutes * 60 + seconds


def range_matches(text: str) -> list[re.Match[str]]:
    return list(TIME_RANGE.finditer(text))


def ranges(text: str) -> list[tuple[float, float, int]]:
    result = []
    for match in range_matches(text):
        start, end = parse_time(match.group("start")), parse_time(match.group("end"))
        if start is not None and end is not None:
            result.append((start, end, match.start()))
    return result


def section_headings(text: str) -> list[tuple[str, int, int]]:
    found = []
    for match in re.finditer(r"(?m)^.*$", text):
        heading = SECTION_RE.match(match.group(0))
        if heading:
            found.append((heading.group(1).upper(), match.start(), match.end()))
    return found


def section_bodies(text: str, headings: list[tuple[str, int, int]]) -> dict[str, str]:
    bodies = {}
    for index, (name, _, end) in enumerate(headings):
        next_start = headings[index + 1][1] if index + 1 < len(headings) else len(text)
        bodies[name] = text[end:next_start].strip()
    return bodies


def check_sections(text: str, findings: list[dict[str, str]]) -> dict[str, str]:
    headings = section_headings(text)
    bodies = section_bodies(text, headings)
    names = [name for name, _, _ in headings]
    expected = [name.upper() for name in SECTIONS]

    for name in expected:
        count = names.count(name)
        chinese_name = SECTIONS[expected.index(name)]
        if count == 0:
            add(findings, "error", f"{chinese_name}.missing", f"缺少“{chinese_name}”部分。")
        elif count > 1:
            add(findings, "error", "sections.duplicate", f"“{chinese_name}”部分重复出现。")
        elif not bodies.get(name):
            add(findings, "error", f"{chinese_name}.empty", f"“{chinese_name}”部分没有内容。")

    if names and names != expected:
        add(findings, "error", "sections.order", "五个部分应按“主体、风格、时间线、BGM、限制”顺序排列。")

    known = {name.upper() for name in SECTIONS}
    for line in text.splitlines():
        match = MODULE_RE.match(line)
        if not match:
            continue
        module = (match.group("bracket") or match.group("markdown") or "").strip()
        if module.upper() not in known:
            add(findings, "error", "sections.extra", f"不应新增“{module}”一级模块，应归入五段式。")
    return bodies


def check_timeline(text: str, duration: float | None, findings: list[dict[str, str]]) -> None:
    for match in range_matches(text):
        if parse_time(match.group("start")) is None or parse_time(match.group("end")) is None:
            add(findings, "error", "timeline.clock", f"时间格式超出时钟范围：{match.group(0)}。")

    timeline = ranges(text)
    if not timeline:
        add(findings, "error", "timeline.missing", "未识别到时间线段落中的“开始—结束”时间段。")
        return
    ordered = [(start, end) for start, end, _ in timeline]
    if ordered != sorted(ordered):
        add(findings, "error", "timeline.order", "时间段没有按开始时间递增排列。")
    if abs(timeline[0][0]) > 0.01:
        add(findings, "error", "timeline.start", f"时间轴从 {timeline[0][0]:g} 秒开始，而不是 0 秒。")

    previous_end = None
    for start, end, _ in timeline:
        if end <= start:
            add(findings, "error", "timeline.invalid", f"时间段 {start:g}—{end:g} 秒无效。")
        if previous_end is not None:
            if start > previous_end + 0.01:
                add(findings, "error", "timeline.gap", f"时间轴在 {previous_end:g}—{start:g} 秒之间有空档。")
            elif start < previous_end - 0.01:
                add(findings, "error", "timeline.overlap", f"时间轴在 {start:g} 秒附近重叠。")
        previous_end = max(previous_end or end, end)
    if duration is not None and abs(max(end for _, end, _ in timeline) - duration) > 0.05:
        add(findings, "error", "timeline.duration", f"时间轴未在目标时长 {duration:g} 秒结束。")


def check_actions(text: str, findings: list[dict[str, str]]) -> None:
    complex_terms = ("攻击", "打斗", "追逐", "抛接", "飞向", "射流", "换位", "格挡", "击中")
    needed = {
        "发起位置": ("发起", "出发", "从", "由", "自"),
        "运动路径": ("路径", "沿", "经过", "穿过", "轨迹", "向"),
        "作用目标": ("作用于", "击中", "落入", "对准", "朝向", "目标", "接触"),
        "最终落点": ("落点", "落在", "停在", "最终落", "停稳"),
    }
    timeline = ranges(text)
    for index, (start, end, position) in enumerate(timeline):
        next_position = timeline[index + 1][2] if index + 1 < len(timeline) else len(text)
        segment = text[position:next_position]
        if any(term in segment for term in complex_terms):
            missing = [name for name, terms in needed.items() if not any(term in segment for term in terms)]
            if missing:
                add(findings, "warning", "action.causality", f"{start:g}—{end:g} 秒的复杂动作缺少：" + "、".join(missing) + "。")


def check_audio(bodies: dict[str, str], findings: list[dict[str, str]]) -> None:
    bgm = bodies.get("BGM", "")
    if not re.search(r"无\s*BGM|无背景音乐|没有背景音乐", bgm, re.IGNORECASE):
        checks = (("bgm.tempo", r"BPM|速度|节奏", "BGM 未明确速度或 BPM。"), ("bgm.instrument", r"乐器|鼓|琴|贝斯|弦乐|电子", "BGM 未明确核心乐器或声音构成。"), ("bgm.ending", r"结尾|收束|淡出|停止|定音", "BGM 未明确结尾收束方式。"))
        for code, pattern, message in checks:
            if not re.search(pattern, bgm, re.IGNORECASE):
                add(findings, "warning", code, message)
    dialogue_text = NO_DIALOGUE_RE.sub("", "\n".join((bodies.get("时间线", ""), bgm)))
    if DIALOGUE_RE.search(dialogue_text):
        if not re.search(r"普通话|中文|粤语|英语|日语|韩语|语言", bgm):
            add(findings, "warning", "dialogue.language", "包含对白，但未明确对白语言。")
        if not re.search(r"口型|唇形|同步", bgm):
            add(findings, "warning", "dialogue.sync", "包含对白，但未明确口型同步要求。")


def check_unbranded(text: str, findings: list[dict[str, str]]) -> None:
    hits = [brand for brand in BRANDS if brand.lower() in text.lower()]
    if hits:
        add(findings, "error", "brand.detected", "无品牌模式发现现实品牌词：" + "、".join(sorted(set(hits))))
    if not any(term in text for term in ("无品牌", "无商标", "不出现任何文字", "不出现现实品牌")):
        add(findings, "warning", "brand.lock", "无品牌模式缺少明确的无品牌或无商标约束。")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("prompt", type=Path, help="UTF-8 prompt text or Markdown file")
    parser.add_argument("--duration", type=float, help="Expected duration in seconds")
    parser.add_argument("--unbranded", action="store_true", help="Flag brands in an unbranded prompt")
    args = parser.parse_args()
    if not args.prompt.is_file():
        print(json.dumps({"ok": False, "error": f"文件不存在：{args.prompt}"}, ensure_ascii=False))
        return 2

    text = args.prompt.read_text(encoding="utf-8")
    findings: list[dict[str, str]] = []
    bodies = check_sections(text, findings)
    timeline = bodies.get("时间线", "")
    if timeline:
        check_timeline(timeline, args.duration, findings)
        check_actions(timeline, findings)
    check_audio(bodies, findings)
    if args.unbranded:
        check_unbranded(text, findings)
    errors = sum(item["level"] == "error" for item in findings)
    print(json.dumps({"ok": errors == 0, "file": str(args.prompt), "errors": errors, "warnings": len(findings) - errors, "findings": findings}, ensure_ascii=False, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
