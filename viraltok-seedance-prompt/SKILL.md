---
name: viraltok-seedance-prompt
description: "Create, repair, and audit Seedance video prompts for Viraltok using five sections: subject, style, timeline, BGM, and constraints. Use for 15s or 30s original videos, multimodal references, video extensions, local edits, and prompt reviews."
---

# Viraltok Seedance Prompt

Turn a creative brief or source material into a concise, directly usable Seedance video prompt. Default to prompt delivery only; do not submit a generation job unless the user explicitly asks.

## Core Format

Use exactly these five top-level sections, in this order:

```text
主体 + 风格 + 时间线 + BGM + 限制
```

- `主体`: character or product, setting, core event, stable identity, and responsibilities for any references.
- `风格`: duration, aspect ratio, output style, lighting, color, material quality, and camera rhythm.
- `时间线`: continuous time ranges from 0 seconds to the end. Each range has one primary action and one camera treatment.
- `BGM`: music, pacing, instruments, emotional curve, ending, dialogue, and key sound effects.
- `限制`: the 3-8 risks most likely to harm this particular result.

## Route The Request

Always read [references/formula.md](references/formula.md) before writing. Then select one primary mode:

| Request | Read | Deliver |
| --- | --- | --- |
| New idea without source media | `formula.md` | Five-section prompt with a continuous timeline |
| Image, video, or audio references | `formula.md`, [references/modes.md](references/modes.md) | Declare each asset's responsibility, effective range, and non-transfer rules in `主体` |
| Recreate or reverse-engineer a video | `formula.md`, `modes.md` | Describe only observable cuts, actions, sound, and transitions; do not invent content |
| Extend an existing video | `formula.md`, `modes.md` | State the source final frame, added period, continuity action, and final frame |
| Local visual edit | `formula.md`, `modes.md` | State range, target, change, and preserved content |
| One continuous take or white-model render | `formula.md`, `modes.md` | Follow the corresponding mode rules |

When several signals coexist, preserve the most specific mode: edit, extend, or reverse-engineer takes priority over a generic new prompt.

## Prompt Rules

- For 15 seconds, use 4-6 ranges; for 30 seconds, use 5-8 ranges.
- Start at 0 seconds, avoid gaps and overlaps, and end at the requested duration.
- Keep characters, products, settings, lighting, and key props continuous unless the prompt explicitly changes them.
- For combat, pursuits, throws, sprays, or position swaps, describe origin, path, target, and final position.
- When dialogue exists, specify speaker, language, exact words, timing, emotion, and lip sync in `BGM`.
- When there is no music, explicitly state `无 BGM`; when there is no dialogue, explicitly state `无对白`.
- Do not create additional top-level sections such as `声音`, `连续性`, or `目标`; place that information in the relevant required section.

## Validation And Delivery

Deliver the entire prompt in one `text` code block, using the five required headings. Validate saved prompts with:

```bash
python3 scripts/check_prompt.py <prompt-file> --duration 15
```

For an explicitly unbranded brief, add `--unbranded`. The validator returns JSON: exit code `0` means no errors, `1` means validation errors, and `2` means the input file was unavailable. Warnings require judgment; they do not prove a prompt cannot generate.

The validator rejects missing, repeated, or extra top-level sections; empty timelines; invalid timestamps; gaps; overlaps; and duration mismatches. It warns about incomplete complex-action causality, BGM fields, and explicit dialogue fields.
