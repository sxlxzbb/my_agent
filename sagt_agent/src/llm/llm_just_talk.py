from src.llm.llm_setting import chat_model as llm
from langchain_core.messages import AIMessage, SystemMessage, AnyMessage
from src.utils.agent_logger import get_logger
from src.models.sagt_models import JustTalkOutput

logger = get_logger("llm_just_talk")

def llm_just_talk(messages: list[AnyMessage]) -> JustTalkOutput:

    chat_history = '\n\n'.join(message.content for message in messages if messages)

    # 系统指令（含 JustTalkOutput 的 JSON schema 与示例）作为首条消息，
    # 其后追加历史对话（已包含本轮用户输入），实现多轮上下文感知
    prompt = _just_talk_instructions.format(
        schema_json=JustTalkOutput.get_schema_json(),
        example_json=JustTalkOutput.get_example_json(),
        input=chat_history
    )

    logger.info(f"prompt: {prompt}")

    generated_result: AIMessage = llm.invoke(prompt)
    logger.info(f"generated_result: {generated_result}")

    if generated_result and generated_result.content:
        just_talk_json = generated_result.content
    else:
        just_talk_json = "{}"

    logger.debug(f"just_talk_json: {just_talk_json}")

    try:
        just_talk = JustTalkOutput.model_validate_json(just_talk_json)
    except Exception as e:
        logger.error(f"解析JustTalkOutput失败: {e}")
        just_talk = JustTalkOutput()

    logger.info(f"just_talk: {just_talk.model_dump_json()}")

    return just_talk


_just_talk_instructions = """
你是一个出色的助手，可以帮助公司员工解决/回答各种问题。如果是其他讨论/闲聊的内容，你也可以提供有意思的回答或者建议。

你需要结合对话上下文回答用户最新提出的问题，并按照 JustTalkOutput 数据结构定义返回JSON。

【注意】请不要在JSON对象前后包含任何文本。也不要包含“```json”或者“```”这样的文本。
【注意】请不要在json对象中包含任何未定义的字段。

这里是JustTalkOutput的数据结构定义：
-------------------
{schema_json}
-------------------

json对象示例：
-------------------
{example_json}
-------------------

下面是与员工的对话历史（最后一条为用户当前的问题）：
-------------------
{input}
-------------------

"""