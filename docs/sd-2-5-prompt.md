# SD 2.5 Prompt Skill Validation

The installed `sd-2-5-prompt` skill validates prompt structure with:

```bash
python3 /Users/zhangweiping/.codex/skills/sd-2-5-prompt/scripts/check_prompt.py <prompt-file> --duration 15
```

The validator returns JSON. Exit code `0` means no errors, `1` means the prompt has errors, and `2` means the input file could not be read.

The five required modules are `主体`、`风格`、`时间线`、`BGM`、`限制`, in that order. Missing, duplicated, or additional top-level modules are errors. Invalid clock values, timeline gaps, overlaps, and duration mismatches are also errors.

Warnings identify incomplete complex-action causality, incomplete BGM fields, or incomplete explicit dialogue fields. Quoted text outside the timeline and BGM sections is not treated as dialogue.

Run the regression suite after changing the validator:

```bash
python3 -m unittest discover -s /Users/zhangweiping/.codex/skills/sd-2-5-prompt/tests -v
```
