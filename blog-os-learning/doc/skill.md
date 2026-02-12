# Chat Logger Filter Skill

智能过滤对话记录并按日期汇总

## 概述

用于 OpenCode 的对话记录管理 skill，具备以下功能：
- 智能过滤无效对话（寒暄、无实质内容）
- 多 agent 并发安全写入
- 按日期分别存储
- 每日自动汇总

## 目录结构

```
.opencode/skills/chat_logger_filter/
├── chat_logger_filter.py      # 主程序
├── filter_config.yaml         # 配置文件
├── SKILL.md                   # Skill 定义文件
└── test_chat_logger_filter.py # 测试代码

blog-os-learning/
├── chat_conversion/           # 对话记录存储目录
│   ├── 2026-02-13.md         # 当天对话记录
│   ├── 2026-02-13-all.md     # 当天汇总（合并后）
│   └── merge_daily.sh        # 每日汇总脚本
└── doc/
    └── skill.md              # 本文档
```

## 配置文件

`filter_config.yaml` 配置说明：

```yaml
min_content_length: 10       # 最小内容长度
enable_auto_filter: true      # 是否自动过滤
enable_logging: true         # 是否记录日志
output_directory: "blog-os-learning/chat_conversion"  # 输出目录
reserved_keywords:           # 保留关键词
  - "怎么"
  - "如何"
  - "为什么"
  - "帮我"
  - "请"
  - "创建"
  - "修改"
  - "panic"
  - "fault"
  - "报错"
  - "cargo"
  - "rustc"
  - "QEMU"
  - "系统调用"
filter_keywords:             # 过滤关键词
  - "谢谢"
  - "收到"
  - "好的"
  - "OK"
  - "辛苦了"
  - "不错"
  - "在吗"
  - "人呢"
log_file: ".opencode/logs/filter.log"
```

## 核心函数

### 1. 实时记录对话

```python
from chat_logger_filter import log_conversation

log_conversation(
    user_content="怎么创建系统调用？",
    assistant_content="我来帮你..."
)
```

- 支持多进程并发（文件锁）
- 自动按日期创建文件
- 写入前自动过滤

### 2. 过滤对话记录

```python
from chat_logger_filter import process_chat_logs

result = process_chat_logs(
    config_path=".opencode/skills/chat_logger_filter/filter_config.yaml",
    output_path="output.md"
)
```

### 3. 每日汇总

```python
from chat_logger_filter import merge_daily_logs

output_file = merge_daily_logs(
    source_dir="blog-os-learning/chat_conversion",
    output_dir="blog-os-learning/chat_conversion"
)
```

## 过滤逻辑

1. **长度过滤** - 内容少于指定字符数（默认10字符）被过滤
2. **关键词过滤** - 包含过滤关键词的内容被直接过滤
3. **保留关键词** - 包含保留关键词的内容被保留
4. **技术内容识别** - 包含技术词汇（rust/cargo/QEMU/RCore等）被保留

## 文件格式

### 当天记录 (2026-02-13.md)

```markdown
## 10:30:00
**用户**: 怎么创建系统调用？
**助手**: 我来帮你实现...
**记录原因**: 包含保留关键词: 怎么

---

## 10:31:00
**用户**: cargo build 报错
**助手**: 这个错误是...
**记录原因**: 包含保留关键词: 报错

---
```

### 每日汇总 (2026-02-13-all.md)

```markdown
# 2026-02-13 对话记录汇总

> **汇总时间**: 2026-02-13 23:59:00
> **来源**: OpenCode 多会话记录
> **文件数**: 3

---

## 10:30:00
**用户**: 怎么创建系统调用？
**助手**: 我来帮你实现...
**记录原因**: 包含保留关键词: 怎么

---

...
```

## 每日汇总脚本

### 手动运行

```bash
cd blog-os-learning/chat_conversion
./merge_daily.sh
```

### 自动运行（crontab）

```bash
# 每天 23:59 自动汇总
59 23 * * * /home/fengxu/mylib/AI-Native\ OS/AI4OSE/blog-os-learning/chat_conversion/merge_daily.sh
```

## 使用方式

### 手动触发

在 OpenCode 中输入：
- "保存对话" - 触发记录
- "过滤无效信息" - 过滤处理
- "汇总今天对话" - 每日汇总

### Python 调用

```python
from chat_logger_filter import log_conversation, merge_daily_logs

# 记录对话
log_conversation(
    user_content="你的问题",
    assistant_content="我的回答"
)

# 汇总当天
merge_daily_logs()
```

## 运行测试

```bash
cd .opencode/skills/chat_logger_filter
python3 -m pytest test_chat_logger_filter.py -v
```

## 依赖

- Python 3.8+
- pyyaml >= 6.0
