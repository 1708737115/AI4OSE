import os
import re
import yaml
import logging
import json
import fcntl
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# ======================== 初始化配置 ========================
def load_config(config_path: str) -> Dict:
    """加载过滤配置文件"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        return config
    except FileNotFoundError:
        raise Exception(f"配置文件不存在: {config_path}")
    except Exception as e:
        raise Exception(f"加载配置失败: {str(e)}")

def setup_logging(log_file: str, enable_logging: bool = True) -> None:
    """配置日志系统"""
    if not enable_logging:
        return
    
    # 创建日志目录
    log_dir = os.path.dirname(log_file)
    os.makedirs(log_dir, exist_ok=True)
    
    # 配置日志格式
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()  # 同时输出到控制台
        ]
    )

# ======================== 核心过滤逻辑 ========================
def is_content_valid(
    content: str,
    min_length: int,
    reserved_keywords: List[str],
    filter_keywords: List[str]
) -> Tuple[bool, str]:
    """
    判断内容是否有效（保留）
    返回: (是否保留, 保留/过滤原因)
    """
    # 空内容直接过滤
    if not content or content.strip() == "":
        return False, "内容为空"
    
    # 长度不足过滤
    content_stripped = content.strip()
    if len(content_stripped) < min_length:
        return False, f"内容长度不足{min_length}个字符"
    
    # 包含过滤关键词直接过滤
    for keyword in filter_keywords:
        if keyword in content:
            return False, f"包含过滤关键词: {keyword}"
    
    # 包含保留关键词则保留
    for keyword in reserved_keywords:
        if keyword in content:
            return True, f"包含保留关键词: {keyword}"
    
    # 无保留/过滤关键词时，判断是否为技术相关内容（简单正则匹配）
    tech_pattern = re.compile(r'\b(rust|cargo|rustc|QEMU|RCore|系统调用|panic|fault|报错|代码|编译|运行)\b', re.IGNORECASE)
    if tech_pattern.search(content):
        return True, "包含技术相关内容"
    
    # 其他情况过滤
    return False, "无技术价值内容"

def process_single_conversation(
    conversation: Dict,
    config: Dict,
    output_template: str
) -> Optional[str]:
    """
    处理单条对话记录
    conversation 格式: {
        "conversation_id": "xxx",
        "topic": "xxx",
        "time": "2026-02-13 10:00:00",
        "user_content": "用户输入",
        "assistant_content": "助手回复"
    }
    """
    # 检查用户内容
    user_valid, user_reason = is_content_valid(
        conversation.get("user_content", ""),
        config["min_content_length"],
        config["reserved_keywords"],
        config["filter_keywords"]
    )
    
    # 检查助手内容
    assistant_valid, assistant_reason = is_content_valid(
        conversation.get("assistant_content", ""),
        config["min_content_length"],
        config["reserved_keywords"],
        config["filter_keywords"]
    )
    
    # 只要用户或助手内容有效，就保留这条记录
    if user_valid or assistant_valid:
        reason = user_reason if user_valid else assistant_reason
        # 填充输出模板
        output = output_template.format(
            conversation_id=conversation.get("conversation_id", "unknown"),
            topic=conversation.get("topic", "未命名"),
            time=conversation.get("time", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            user_content=conversation.get("user_content", ""),
            assistant_content=conversation.get("assistant_content", ""),
            reason=reason
        )
        logging.info(f"保留对话 {conversation.get('conversation_id')}: {reason}")
        return output
    else:
        logging.info(f"过滤对话 {conversation.get('conversation_id')}: {user_reason}/{assistant_reason}")
        return None

def load_conversations_from_directory(directory: str) -> List[Dict]:
    """
    从目录加载对话记录（支持 .txt/.yaml/.json 格式）
    这里假设对话文件是按行存储或YAML/JSON格式
    """
    conversations = []
    if not os.path.exists(directory):
        logging.warning(f"对话目录不存在: {directory}")
        return conversations
    
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if filename.endswith(".txt"):
            # 处理TXT格式（简单示例：每行一条对话，按分隔符拆分）
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                for i, line in enumerate(lines):
                    if line.strip():
                        conversations.append({
                            "conversation_id": f"{filename}_{i}",
                            "topic": filename.replace(".txt", ""),
                            "time": datetime.fromtimestamp(os.path.getmtime(file_path)).strftime("%Y-%m-%d %H:%M:%S"),
                            "user_content": line.split("|")[0] if "|" in line else line,
                            "assistant_content": line.split("|")[1] if "|" in line else ""
                        })
        elif filename.endswith((".yaml", ".yml")):
            # 处理YAML格式
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                if isinstance(data, list):
                    conversations.extend(data)
                elif isinstance(data, dict):
                    conversations.append(data)
        elif filename.endswith(".json"):
            # 处理JSON格式
            import json
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    conversations.extend(data)
                elif isinstance(data, dict):
                    conversations.append(data)
    
    return conversations

# ======================== 入口函数 ========================
def process_chat_logs(
    config_path: str = ".opencode/skills/chat_logger_filter/filter_config.yaml",
    output_path: str = ".opencode/skills/chat_logger_filter/filtered_logs.md"
) -> str:
    """
    Skill 入口函数：处理聊天记录过滤
    """
    # 1. 加载配置
    config = load_config(config_path)
    
    # 2. 初始化日志
    setup_logging(config["log_file"], config["enable_logging"])
    logger = logging.getLogger("chat_logger_filter")
    logger.info("开始执行对话记录过滤...")
    
    # 3. 加载对话记录
    conversations = load_conversations_from_directory(config["log_directory"])
    logger.info(f"加载到 {len(conversations)} 条对话记录")
    
    # 4. 处理所有对话
    filtered_results = []
    output_template = """### 对话 {conversation_id} - [{topic}]
**时间**: {time}
**用户**: {user_content}
**助手**: {assistant_content}
**记录原因**: {reason}
"""
    
    for conv in conversations:
        result = process_single_conversation(conv, config, output_template)
        if result:
            filtered_results.append(result)
    
    # 5. 保存过滤结果
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# RCore 实验对话过滤结果\n")
        f.write(f"**过滤时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**原始记录数**: {len(conversations)}\n")
        f.write(f"**保留记录数**: {len(filtered_results)}\n\n")
        f.write("\n---\n\n".join(filtered_results))
    
    # 6. 返回结果
    summary = f"过滤完成！共处理 {len(conversations)} 条记录，保留 {len(filtered_results)} 条有效记录，结果已保存至 {output_path}"
    logger.info(summary)
    return summary

# ======================== 实时记录函数 ========================
def log_conversation(
    user_content: str,
    assistant_content: str,
    config_path: str = ".opencode/skills/chat_logger_filter/filter_config.yaml"
) -> bool:
    """
    实时记录对话（支持多进程并发）
    先过滤，有效对话才写入当天文件
    
    Returns:
        bool: 是否成功写入
    """
    config = load_config(config_path)
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M:%S")
    
    user_valid, user_reason = is_content_valid(
        user_content,
        config["min_content_length"],
        config["reserved_keywords"],
        config["filter_keywords"]
    )
    
    assistant_valid, assistant_reason = is_content_valid(
        assistant_content,
        config["min_content_length"],
        config["reserved_keywords"],
        config["filter_keywords"]
    )
    
    if not user_valid and not assistant_valid:
        return False
    
    reason = user_reason if user_valid else assistant_reason
    output_dir = config.get("output_directory", config.get("log_directory", "blog-os-learning/chat_conversion"))
    os.makedirs(output_dir, exist_ok=True)
    
    output_file = os.path.join(output_dir, f"{date_str}.md")
    lock_file = f"{output_file}.lock"
    
    os.makedirs(os.path.dirname(lock_file), exist_ok=True)
    
    with open(lock_file, 'w') as lock_f:
        fcntl.flock(lock_f.fileno(), fcntl.LOCK_EX)
        try:
            with open(output_file, 'a', encoding='utf-8') as f:
                f.write(f"## {time_str}\n")
                f.write(f"**用户**: {user_content}\n")
                f.write(f"**助手**: {assistant_content}\n")
                f.write(f"**记录原因**: {reason}\n")
                f.write("\n---\n\n")
            return True
        finally:
            fcntl.flock(lock_f.fileno(), fcntl.LOCK_UN)

def merge_daily_logs(
    source_dir: str = "blog-os-learning/chat_conversion",
    output_dir: str = "blog-os-learning/chat_conversion"
) -> str:
    """
    汇总当天所有会话文件
    
    读取 source_dir 下所有 YYYY-MM-DD.md 文件，
    按时间排序后合并到 output_dir/YYYY-MM-DD-all.md
    """
    today = datetime.now().strftime("%Y-%m-%d")
    output_file = os.path.join(output_dir, f"{today}-all.md")
    
    md_files = []
    for f in os.listdir(source_dir):
        if f.endswith(".md") and f.startswith(today) and "-all" not in f:
            file_path = os.path.join(source_dir, f)
            md_files.append((file_path, os.path.getmtime(file_path)))
    
    md_files.sort(key=lambda x: x[1])
    
    with open(output_file, 'w', encoding='utf-8') as out:
        out.write(f"# {today} 对话记录汇总\n\n")
        out.write(f"> **汇总时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        out.write("---\n\n")
        
        for file_path, _ in md_files:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if content.strip():
                    out.write(content)
                    out.write("\n\n")
    
    return output_file

# ======================== 测试入口 ========================
if __name__ == "__main__":
    # 本地测试执行
    try:
        result = process_chat_logs()
        print(result)
    except Exception as e:
        print(f"执行失败: {str(e)}")
        logging.error(f"执行失败: {str(e)}")