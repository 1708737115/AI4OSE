# 对话记录系统 - 主索引

## 系统架构

采用**进程隔离方案**，每个 OpenCode 会话独立记录，每日自动汇总。

```
chat_conversion/                        # 记录根目录
├── session_88836_20260213/            # 会话1目录 (PID_日期)
│   ├── 2026-02-13.md                  # 当日对话记录
│   └── index.md                       # 会话索引
├── session_XXXXX_20260213/            # 会话2目录
│   └── ...
├── merge_daily.sh                     # 每日汇总脚本
└── README.md                          # 本文件

AI4OSE/blog-os-learning/               # 每日汇总目录
└── 2026-02-13.md                      # 汇总后的完整记录
```

## 使用说明

### 1. 自动记录
每个会话的助手会自动将对话记录到各自的 `session_PID_YYYYMMDD/` 目录中。

### 2. 每日汇总

**✅ 已配置自动定时任务**

系统已自动配置以下定时任务：
- **每天 23:59** - 自动汇总当日所有会话
- **每小时整点** - 额外备份，防止错过23:59

日志文件：`/home/fengxu/mylib/AI-Native OS/chat_conversion/merge.log`

**手动运行（如需立即汇总）**：
```bash
bash "/home/fengxu/mylib/AI-Native OS/chat_conversion/merge_daily.sh"
```

**查看定时任务**：
```bash
crontab -l
```

**查看运行日志**：
```bash
tail -f "/home/fengxu/mylib/AI-Native OS/chat_conversion/merge.log"
```

### 3. 查看记录
- **当前会话**: 查看 `chat_conversion/session_PID_YYYYMMDD/` 目录
- **每日汇总**: 查看 `AI4OSE/blog-os-learning/YYYY-MM-DD.md`

## 当前活跃会话

| 会话ID | PID | 开始日期 | 状态 |
|--------|-----|----------|------|
| session_88836_20260213 | 88836 | 2026-02-13 | 🟢 活跃 |

## 历史汇总

| 日期 | 文件 | 会话数 | 对话数 |
|------|------|--------|--------|
| - | - | - | - |

---

*系统初始化时间: 2026-02-13 00:57*
