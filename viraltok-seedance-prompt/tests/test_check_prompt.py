import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = SKILL_ROOT / "scripts" / "check_prompt.py"

VALID_PROMPT = """【主体】
同一位女孩在清晨厨房制作手工面。

【风格】
15秒、16:9、真人写实美食短片，暖光，节奏明快。

【时间线】
【0—2秒】女孩揉面，微距推进，面团拉成长条。
【2—5秒】女孩整理面条，侧面跟拍，面束位于锅上方。
【5—9秒】女孩下面煮熟，锅内特写，面条光滑。
【9—12秒】女孩装碗注汤，俯拍推进，汤面出现油花。
【12—15秒】女孩端面看向镜头，中近景推进，最终停在面碗。

【BGM】
轻快木吉他和手鼓，118 BPM，9秒上扬，15秒温暖和弦收束。女孩使用普通话说：“面做好啦。”口型同步。

【限制】
避免变脸、面条穿模、额外字幕、商标和水印。
"""


def run_cli(prompt: str | None, duration: int = 15) -> tuple[int, dict]:
    command = [sys.executable, str(SCRIPT)]
    if prompt is None:
        result = subprocess.run([*command, str(SKILL_ROOT / "tests" / "missing.txt")], capture_output=True, text=True, check=False)
        return result.returncode, json.loads(result.stdout)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".txt") as prompt_file:
        prompt_file.write(prompt)
        prompt_file.flush()
        result = subprocess.run([*command, prompt_file.name, "--duration", str(duration)], capture_output=True, text=True, check=False)
    return result.returncode, json.loads(result.stdout)


class CheckPromptTests(unittest.TestCase):
    def test_valid_prompt_passes(self):
        code, result = run_cli(VALID_PROMPT)
        self.assertEqual(code, 0)
        self.assertTrue(result["ok"])
        self.assertEqual(result["findings"], [])

    def test_gap_is_an_error(self):
        code, result = run_cli(VALID_PROMPT.replace("【2—5秒】", "【2.5—5秒】"))
        self.assertEqual(code, 1)
        self.assertIn("timeline.gap", {item["code"] for item in result["findings"]})

    def test_clock_notation_and_invalid_clock(self):
        code, result = run_cli(VALID_PROMPT.replace("【0—2秒】", "【0:00—0:75】"))
        self.assertEqual(code, 1)
        self.assertIn("timeline.clock", {item["code"] for item in result["findings"]})

    def test_extra_module_is_an_error(self):
        prompt = VALID_PROMPT.replace("【限制】", "【连续性】\n人物保持一致。\n\n【限制】")
        code, result = run_cli(prompt)
        self.assertEqual(code, 1)
        self.assertIn("sections.extra", {item["code"] for item in result["findings"]})

    def test_quoted_prop_is_not_dialogue(self):
        prompt = VALID_PROMPT.replace("同一位女孩在清晨厨房制作手工面。", "碗上写着“清晨”。")
        prompt = prompt.replace("女孩使用普通话说：“面做好啦。”口型同步。", "无对白。")
        code, result = run_cli(prompt)
        self.assertEqual(code, 0)
        self.assertNotIn("dialogue.language", {item["code"] for item in result["findings"]})

    def test_missing_file_returns_two(self):
        code, result = run_cli(None)
        self.assertEqual(code, 2)
        self.assertFalse(result["ok"])


if __name__ == "__main__":
    unittest.main()
