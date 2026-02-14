---
name: chat_logger_filter
version: '1.0.0'
description: '智能过滤RCore实验场景下的无效对话记录，仅保留有技术价值的核心信息'
author: 'OpenCode Agent'
created_at: '2026-02-13'
updated_at: '2026-02-13'
triggers:
  auto_trigger:
    event: 'conversation_ended'
    enabled: true
  manual_trigger:
    commands:
      - '清理对话记录'
      - '过滤无效信息'
      - '整理聊天记录'
    enabled: true
dependencies:
  python: '>=3.8'
  packages:
    - pyyaml>=6.0
    - python-dotenv>=1.0.0
executor:
  type: 'python'
  script_path: '.opencode/skills/chat_logger_filter/chat_logger_filter.py'
  entry_function: 'process_chat_logs'
config:
  min_content_length: 10
  enable_auto_filter: true
  enable_logging: true
  reserved_keywords:
    - '怎么'
    - '如何'
    - '为什么'
    - '帮我'
    - '请'
    - '创建'
    - '修改'
    - 'panic'
    - 'fault'
    - '报错'
    - 'cargo'
    - 'rustc'
    - 'QEMU'
    - '系统调用'
  filter_keywords:
    - '谢谢'
    - '收到'
    - '好的'
    - 'OK'
    - '辛苦了'
    - '不错'
    - '在吗'
    - '人呢'
  log_directory: 'blog-os-learning/chat_conversion'
  config_file: '.opencode/skills/chat_logger_filter/filter_config.yaml'
  log_file: '.opencode/logs/filter.log'
output_template: |
  ### 对话 {conversation_id} - [{topic}]
  **时间**: {time}
  **用户**: {user_content}
  **助手**: {assistant_content}
  **记录原因**: {reason}
metadata:
  category: 'log_management'
  tags: ['RCore', 'chat_filter', 'log_cleanup']
  experimental: false
---

# Chat Logger Filter Skill

智能过滤 RCore 实验场景下的无效对话记录，仅保留有技术价值的核心信息。

## 功能概述

自动识别并过滤对话中的寒暄、无实质内容的信息，保留技术相关的提问和回答。

## 工作原理

### 过滤逻辑

1. **长度过滤** - 内容少于指定字符数（默认10字符）被过滤
2. **关键词过滤** - 包含过滤关键词的内容被直接过滤
3. **保留关键词** - 包含保留关键词的内容被保留
4. **技术内容识别** - 包含技术词汇（rust/cargo/QEMU/RCore等）被保留
5. **对话保留规则** - 用户或助手内容任一有效，整条对话保留

### 过滤关键词（默认）

```
谢谢、收到、好的、OK、辛苦了、不错、在吗、人呢
```

### 保留关键词（默认）

```
怎么、如何、为什么、帮我、请、创建、修改、panic、fault、报错、cargo、rustc、QEMU、系统调用
```

### 技术内容识别

自动识别包含以下关键词的内容为技术相关内容：
- rust、cargo、rustc、QEMU、RCore
- 系统调用、panic、fault、报错
- 代码、编译、运行

## 支持格式

### JSON 格式

```json
[
  {
    "conversation_id": "001",
    "topic": "RCore实验",
    "time": "2026-02-13 10:00:00",
    "user_content": "怎么创建系统调用？",
    "assistant_content": "我来帮你..."
  }
]
```

### YAML 格式

```yaml
- conversation_id: "001"
  topic: "RCore实验"
  time: "2026-02-13 10:00:00"
  user_content: "怎么创建系统调用？"
  assistant_content: "我来帮你..."
```

### TXT 格式

每行按 `|` 分隔用户和助手内容：
```
用户输入|助手回复
```

## 使用方式

### 手动触发

对话结束时自动触发，或手动输入：
- "清理对话记录"
- "过滤无效信息"
- "整理聊天记录"

### 脚本运行

```bash
cd /path/to/project
python3 .opencode/skills/chat_logger_filter/chat_logger_filter.py
```

### Python 调用

```python
from chat_logger_filter import process_chat_logs

result = process_chat_logs(
    config_path=".opencode/skills/chat_logger_filter/filter_config.yaml",
    output_path=".opencode/skills/chat_logger_filter/filtered_logs.md"
)
print(result)
```

## 运行测试

```bash
cd .opencode/skills/chat_logger_filter
python3 -m pytest test_chat_logger_filter.py -v

# 或使用 unittest
python3 test_chat_logger_filter.py
```

## 输出结果

过滤结果保存为 Markdown 格式，示例：

```markdown
# RCore 实验对话过滤结果
**过滤时间**: 2026-02-13 10:00:00
**原始记录数**: 10
**保留记录数**: 3

---

### 对话 001 - [RCore实验]
**时间**: 2026-02-13 10:00:00
**用户**: 怎么创建系统调用？
**助手**: 我来帮你...
**记录原因**: 包含保留关键词: 怎么
```

## 目录结构

```
.opencode/skills/chat_logger_filter/
├── chat_logger_filter.py      # 主程序
├── filter_config.yaml         # 配置文件
├── SKILL.md                   # 说明文档
└── test_chat_logger_filter.py  # 测试代码
```
