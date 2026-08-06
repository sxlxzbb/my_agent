from src.llm.llm_setting import chat_model as llm
from langchain_core.messages import AIMessage, SystemMessage, AnyMessage
from src.utils.agent_logger import get_logger

logger = get_logger("llm_summarize")

# 历史摘要，约束在 200 字以内
_MAX_SUMMARY_CHARS = 200


def llm_summarize(messages: list[AnyMessage]) -> str:
    """将早期对话历史压缩为一条不超过 200 字的摘要。

    messages: 需要被压缩的（较早的）对话消息列表
    返回: 摘要文本字符串
    """
    if not messages:
        return ""

    history_text = "\n".join(
        f"{m.type}: {m.content}" for m in messages if hasattr(m, "content") and m.content
    )
    if not history_text.strip():
        return ""

    system_instruction = (
        "你是一个对话历史压缩助手。请将下面的对话历史总结为一段连贯的摘要，"
        f"用于帮助后续对话理解上下文。严格要求：摘要不超过 {_MAX_SUMMARY_CHARS} 个字，"
        "只保留关键信息（如用户身份、偏好、已确认的事项、待办等），不要编造内容，"
        "不要包含任何解释性文字。"
    )

    try:
        result: AIMessage = llm.invoke([
            SystemMessage(content=system_instruction),
            SystemMessage(content=f"对话历史：\n{history_text}"),
        ])
        summary = (result.content or "").strip()
    except Exception as e:
        logger.error(f"生成历史摘要失败: {e}")
        summary = ""

    # 兜底截断，确保不超过上限
    if len(summary) > _MAX_SUMMARY_CHARS:
        summary = summary[:_MAX_SUMMARY_CHARS]
        logger.warning(f"摘要超出 {_MAX_SUMMARY_CHARS} 字，已截断")

    return summary
