#!/bin/bash

# 每日对话记录汇总脚本
# 将所有会话目录的当日记录合并到 blog-os-learning 目录

set -e

# 配置
SOURCE_DIR="/home/fengxu/mylib/AI-Native OS/chat_exchange"
TARGET_DIR="/home/fengxu/mylib/AI-Native OS/AI4OSE/blog-os-learning"
DATE=$(date +%Y-%m-%d)
DATE_SHORT=$(date +%Y%m%d)

# 确保目标目录存在
mkdir -p "$TARGET_DIR"

# 输出文件
OUTPUT_FILE="$TARGET_DIR/$DATE.md"
TEMP_FILE=$(mktemp)

# 写入汇总文件头部
cat > "$TEMP_FILE" << EOF
# 对话记录汇总 - $DATE

> **汇总时间**: $(date '+%Y-%m-%d %H:%M:%S')  
> **来源**: OpenCode 多会话记录  
> **生成方式**: 自动汇总

## 今日会话概览

| 会话ID | 进程PID | 对话数 | 主要主题 |
|--------|---------|--------|----------|
EOF

# 统计今日所有会话
SESSION_COUNT=0
TOTAL_DIALOGUES=0

for session_dir in "$SOURCE_DIR"/session_*_${DATE_SHORT}; do
    if [ -d "$session_dir" ]; then
        SESSION_ID=$(basename "$session_dir")
        PID=$(echo "$SESSION_ID" | cut -d'_' -f2)
        
        # 检查当天的记录文件
        if [ -f "$session_dir/$DATE.md" ]; then
            SESSION_COUNT=$((SESSION_COUNT + 1))
            
            # 提取对话数（简单计数）
            DIALOGUE_COUNT=$(grep -c "^### 对话" "$session_dir/$DATE.md" 2>/dev/null || echo "0")
            TOTAL_DIALOGUES=$((TOTAL_DIALOGUES + DIALOGUE_COUNT))
            
            # 提取主要内容（前50个字符）
            MAIN_TOPIC=$(grep -A 1 "主要内容" "$session_dir/$DATE.md" | tail -1 | cut -c 1-50)
            if [ -z "$MAIN_TOPIC" ]; then
                MAIN_TOPIC="日常对话"
            fi
            
            echo "| $SESSION_ID | $PID | $DIALOGUE_COUNT | $MAIN_TOPIC |" >> "$TEMP_FILE"
        fi
    fi
done

# 写入统计信息
cat >> "$TEMP_FILE" << EOF

**统计**: 今日共 $SESSION_COUNT 个会话，$TOTAL_DIALOGUES 次对话

---

## 详细对话记录

EOF

# 合并所有会话的详细内容
for session_dir in "$SOURCE_DIR"/session_*_${DATE_SHORT}; do
    if [ -d "$session_dir" ]; then
        if [ -f "$session_dir/$DATE.md" ]; then
            SESSION_ID=$(basename "$session_dir")
            echo "<!-- 来源: $SESSION_ID -->" >> "$TEMP_FILE"
            echo "" >> "$TEMP_FILE"
            
            # 提取对话详情部分（从"## 对话详情"开始到"## 待办事项"之前）
            awk '/^## 对话详情/,/^## 待办事项/' "$session_dir/$DATE.md" | head -n -1 >> "$TEMP_FILE"
            
            echo "" >> "$TEMP_FILE"
            echo "---" >> "$TEMP_FILE"
            echo "" >> "$TEMP_FILE"
        fi
    fi
done

# 合并待办事项
cat >> "$TEMP_FILE" << EOF

## 今日所有待办事项

EOF

for session_dir in "$SOURCE_DIR"/session_*_${DATE_SHORT}; do
    if [ -d "$session_dir" ]; then
        if [ -f "$session_dir/$DATE.md" ]; then
            SESSION_ID=$(basename "$session_dir")
            echo "### 来自 $SESSION_ID" >> "$TEMP_FILE"
            
            # 提取待办事项
            awk '/^## 待办事项/,/^---/' "$session_dir/$DATE.md" | grep "^- \[" >> "$TEMP_FILE" || echo "- 无待办事项"
            
            echo "" >> "$TEMP_FILE"
        fi
    fi
done

# 写入页脚
cat >> "$TEMP_FILE" << EOF

---

*汇总文件生成时间: $(date '+%Y-%m-%d %H:%M:%S')*  
*原始记录位置: $SOURCE_DIR*
EOF

# 移动到最终位置
mv "$TEMP_FILE" "$OUTPUT_FILE"

echo "✅ 汇总完成: $OUTPUT_FILE"
echo "   - 会话数: $SESSION_COUNT"
echo "   - 对话数: $TOTAL_DIALOGUES"
