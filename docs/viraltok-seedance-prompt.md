# Viraltok Seedance Prompt

`viraltok-seedance-prompt` 是仓库自维护的 Seedance 视频提示词 skill，位于 `viraltok-seedance-prompt/`。它不依赖本机安装目录，可随仓库一起分发和维护。

## 使用

直接调用 `$viraltok-seedance-prompt`。交付格式固定为五个一级模块：`主体`、`风格`、`时间线`、`BGM`、`限制`。

保存提示词后运行：

```bash
python3 viraltok-seedance-prompt/scripts/check_prompt.py <prompt-file> --duration 15
```

对于明确要求无品牌的任务，追加 `--unbranded`。

## 校验结果

校验器输出 JSON：退出码 `0` 表示无错误，`1` 表示提示词结构不通过，`2` 表示输入文件不可用。它会拒绝缺失、重复或额外的一级模块，以及时间轴空档、重叠、非法时钟值和时长不匹配；对复杂动作、BGM 与明确对白字段给出 warning。

## 维护验证

```bash
python3 -m unittest discover -s viraltok-seedance-prompt/tests -v
python3 /Users/zhangweiping/.codex/skills/.system/skill-creator/scripts/quick_validate.py viraltok-seedance-prompt
```
