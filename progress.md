## 2026-09-04 - Task: Improve SD 2.5 prompt skill validation
### What was done
Improved the installed SD 2.5 prompt validator so that it rejects duplicate or extra top-level modules, validates clock-style timestamps, and limits dialogue checks to explicit dialogue descriptions in the timeline or BGM. Replaced serialization-only coverage with command-line regression tests covering successful validation, validation errors, and missing input files.

### Testing
`python3 -m unittest discover -s /Users/zhangweiping/.codex/skills/sd-2-5-prompt/tests -v` passed: 12 tests. `python3 -m py_compile` passed for the validator and tests. `quick_validate.py` reported `Skill is valid!`. A missing-file CLI invocation returned structured JSON and exit code 2.

### Notes
- `/Users/zhangweiping/.codex/skills/sd-2-5-prompt/scripts/check_prompt.py`: Added module, clock, and scoped dialogue validation.
- `/Users/zhangweiping/.codex/skills/sd-2-5-prompt/tests/test_check_prompt.py`: Added CLI and regression coverage for the new checks.
- `/Users/zhangweiping/.codex/skills/sd-2-5-prompt/SKILL.md`: Documented the validator's expanded error conditions.
- `docs/sd-2-5-prompt.md`: Documented validator usage, exit codes, and warning scope.
- `progress.md`: Recorded this task.

Rollback: restore the three skill files to their prior contents and delete `docs/sd-2-5-prompt.md` plus this appended progress entry.

## 2026-09-04 - Task: Package Viraltok Seedance prompt skill
### What was done
Created the self-contained `viraltok-seedance-prompt` skill in this repository. It packages the five-section Seedance prompt workflow, routing for common production modes, a standalone JSON validator, UI metadata, and regression tests without depending on the installed third-party skill directory.

### Testing
`python3 -m py_compile viraltok-seedance-prompt/scripts/check_prompt.py viraltok-seedance-prompt/tests/test_check_prompt.py` passed. `python3 -m unittest discover -s viraltok-seedance-prompt/tests -v` passed: 6 tests covering valid prompts, timeline errors, clock errors, extra modules, dialogue false positives, and missing input files. `quick_validate.py viraltok-seedance-prompt` passed.

### Notes
- `viraltok-seedance-prompt/SKILL.md`: Added the Viraltok-owned Seedance prompt workflow.
- `viraltok-seedance-prompt/agents/openai.yaml`: Added the skill UI metadata and default invocation prompt.
- `viraltok-seedance-prompt/references/formula.md`: Added the five-section writing formula.
- `viraltok-seedance-prompt/references/modes.md`: Added rules for references, reverse prompts, extensions, edits, continuous takes, and white-model renders.
- `viraltok-seedance-prompt/scripts/check_prompt.py`: Added standalone prompt validation with JSON output.
- `viraltok-seedance-prompt/tests/test_check_prompt.py`: Added CLI regression tests.
- `README.md`: Added the repository skill entry.
- `docs/viraltok-seedance-prompt.md`: Added usage and maintenance documentation.
- `progress.md`: Recorded this task.

Rollback: delete `viraltok-seedance-prompt/`, remove its README and documentation entries, and remove this appended progress entry.
