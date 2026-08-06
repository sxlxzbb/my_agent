import operator
from typing import TypedDict, Annotated, List
from enum import Enum
from langgraph.graph import StateGraph, START, END
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import AnyMessage, HumanMessage, AIMessage, SystemMessage
from src.utils.agent_logger import get_logger
from src.llm.llm_just_talk import llm_just_talk
from src.llm.llm_summarize import llm_summarize
from src.graphs.sagt_state import SagtStateField
from src.graphs.sagt_state import SagtConfig
from src.models.sagt_models import TaskResult, NodeResult, JustTalkOutput

logger = get_logger("sub_talk_graph")

# 闲聊保留的最近对话轮数（可配置）。超过该轮数的早期历史会被压缩为一条摘要。
RECENT_TURN_LIMIT = 3

class SubTalkStateField(str, Enum):
    TASK_INPUT  = SagtStateField.TASK_INPUT.value
    TASK_RESULT = SagtStateField.TASK_RESULT.value
    NODE_RESULT = SagtStateField.NODE_RESULT.value
    MESSAGES    = "messages"

class SubTalkInputState(TypedDict):
    task_input: str
    messages: Annotated[List[AnyMessage], operator.add]

class SubTalkOutputState(TypedDict):
    task_result: TaskResult
    node_result: Annotated[List[NodeResult], operator.add]
    messages: Annotated[List[AnyMessage], operator.add]

# 使用多重继承，自动合并所有字段
class SubTalkState(SubTalkInputState, SubTalkOutputState):
    """
    完整的子图状态，包含输入和输出字段
    继承自 SubTagInputState 和 SubTagOutputState
    """
    pass


class NodeName(str, Enum):
    WELCOME_MESSAGE = "talk_welcome_node"
    JUST_TALK       = "talk_reply_node"

def welcome_message_node(state: SubTalkState, config: RunnableConfig):
    """欢迎消息节点"""
    
    logger.info("=== 欢迎消息 ===")
    
    return {
        SubTalkStateField.NODE_RESULT: [NodeResult(
            execute_node_name=NodeName.JUST_TALK.value,
            execute_result_code=0,
            execute_result_msg="正在为您生成回复，请稍等。",
            execute_exceptions=[]
        )]
    }

def just_talk_node(state: SubTalkState, config: RunnableConfig):
    """咨询回复节点"""
    
    logger.info("=== 咨询回复 ===")

    try:
        task_input = state.get(SubTalkStateField.TASK_INPUT, "")
        # 历史对话（来自 checkpointer 持久化的 messages）
        history: List[AnyMessage] = list(state.get(SubTalkStateField.MESSAGES, []))

        # 将历史中的 human/ai 消息按轮次划分：保留最近 RECENT_TURN_LIMIT 轮，
        # 更早的部分压缩为一条摘要（<=200字），避免上下文无限膨胀。
        # 摘要本身也以 SystemMessage 形式存在于 history 中，下一轮会被重新纳入
        # 早期部分一起再摘要，等价于“旧摘要 + 新对话 -> 新摘要”的增量更新。
        keep_turns = RECENT_TURN_LIMIT * 2  # 一轮 = 1 human + 1 ai
        keep_indices = set()
        human_ai_count = 0
        # range(start, stop, step)  比如range(9, -1, -1)
        # start (9)‌：序列的起始值，‌包含‌该值
        # stop (-1)‌：序列的终止值，‌不包含‌该值。因为步长是负数，所以序列会在大于 -1 的最小整数处停止，即停在 0
        # step (-1)‌：步长，表示每次迭代的变化量。负数表示递减
        for i in range(len(history) - 1, -1, -1):
            keep_indices.add(i)
            if history[i].type in ("human", "ai"):
                human_ai_count += 1
            if human_ai_count >= keep_turns:
                break
        early = [history[i] for i in range(len(history)) if i not in keep_indices]
        recent = [history[i] for i in range(len(history)) if i in keep_indices]

        summary_msg = None
        if early:
            summary_text = llm_summarize(early)
            if summary_text:
                summary_msg = SystemMessage(content=f"以下是之前的对话摘要：{summary_text}")
                logger.info(f"历史摘要(<=200字): {summary_text}")

        # 组装发给 LLM 的消息：摘要(若有) + 最近轮次 + 本轮用户输入
        messages: List[AnyMessage] = []
        if summary_msg is not None:
            messages.append(summary_msg)
        messages.extend(recent)
        messages.append(HumanMessage(content=task_input))

        generated_just_talk_output: JustTalkOutput = llm_just_talk(
            messages = messages
        )
        logger.info(f"generated_just_talk_output: {generated_just_talk_output}")

        if not generated_just_talk_output.just_talk_output:
            return {
                SubTalkStateField.TASK_RESULT: TaskResult(
                    task_result="我好像没有理解你的意思",
                    task_result_explain="生成回复失败",
                    task_result_code=1
                ),
                SubTalkStateField.NODE_RESULT: [NodeResult(
                    execute_node_name=NodeName.JUST_TALK.value,
                    execute_result_code=1,
                    execute_result_msg="生成回复失败",
                    execute_exceptions=["生成回复失败: 模型返回内容为空"]
                )]
            }

        # 写回的消息做同样压缩，保证持久化的 messages 长度恒定（摘要 + 最近轮次 + 本轮），
        # 由 checkpointer 持久化，实现多轮记忆且上下文不臃肿
        updated_messages: List[AnyMessage] = []
        if summary_msg is not None:
            updated_messages.append(summary_msg)
        updated_messages.extend(recent)
        updated_messages.append(HumanMessage(content=task_input))
        updated_messages.append(AIMessage(content=generated_just_talk_output.just_talk_output))

        return {
            SubTalkStateField.TASK_RESULT: TaskResult(
                task_result=generated_just_talk_output.just_talk_output,
                task_result_explain=f"生成回复成功",
                task_result_code=0
            ),
            SubTalkStateField.NODE_RESULT: [NodeResult(
                execute_node_name=NodeName.JUST_TALK.value,
                execute_result_code=0,
                execute_result_msg="生成回复成功",
                execute_exceptions=[]
            )],
            SubTalkStateField.MESSAGES: updated_messages,
        }
    except Exception as e:
        logger.error(f"生成回复失败: {e}")
        return {
            SubTalkStateField.TASK_RESULT: TaskResult(
                task_result="抱歉，我好像有故障，无法回答你的问题",
                task_result_explain="解析失败",
                task_result_code=1
            ),
            SubTalkStateField.NODE_RESULT: [NodeResult(
                execute_node_name=NodeName.JUST_TALK.value,
                execute_result_code=1,
                execute_result_msg="解析失败",
                execute_exceptions=[f"解析结果失败: {e}"]
            )]  
        }

builder = StateGraph(state_schema=SubTalkState, input_schema=SubTalkInputState, output_schema=SubTalkOutputState, config_schema=SagtConfig)

builder.add_node(NodeName.WELCOME_MESSAGE.value, welcome_message_node)
builder.add_node(NodeName.JUST_TALK.value, just_talk_node)

builder.add_edge(START, NodeName.WELCOME_MESSAGE.value)
builder.add_edge(NodeName.WELCOME_MESSAGE.value, NodeName.JUST_TALK.value)
builder.add_edge(NodeName.JUST_TALK.value, END)

sub_talk_graph = builder.compile()