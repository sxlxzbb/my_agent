from langgraph.graph import START, END, StateGraph
from src.graphs.sagt_state import SagtState, InputState, OutputState, SagtConfig

from src.graphs.sagt_sub_graph_profile.sub_profile_graph import sub_profile_graph
from src.graphs.sagt_sub_graph_chat_suggestion.sub_chat_suggestion_graph import sub_chat_suggestion_graph
from src.graphs.sagt_sub_graph_kf_chat_suggestion.sub_kf_chat_suggestion_graph import sub_kf_chat_suggestion_graph
from src.graphs.sagt_sub_graph_tag.sub_tag_graph import sub_tag_graph
from src.graphs.sagt_sub_graph_schedule.sub_schedule_graph import sub_schedule_graph
from src.graphs.sagt_sub_graph_talk.sub_talk_graph import sub_talk_graph
from src.graphs.sagt_node import NodeName, intent_detection, task_result_confirm, welcome_message, cleanup_state_node
from src.graphs.sagt_node_load_data import NodeName as LoadDataNodeName, data_load_entry

import os
from dotenv import load_dotenv
load_dotenv()

# 父图加载数据是怎么传到子图的？
# 父图调用子图时，从父图 state 里取出所有"在子图 input_schema 中同名字段"的值传进去（注意，字段名必须一致，另外父图传数据给子图是浅拷贝，子图尽量不要改父图传过来的dict里对象的值）
# 子图执行完，返回数据给父图的时候也是同样的道理
builder = StateGraph(state_schema=SagtState, input_schema=InputState, output_schema=OutputState, config_schema=SagtConfig)

builder.add_node(NodeName.CLEANUP_STATE.value, cleanup_state_node) ## 清理状态
builder.add_node(NodeName.WELCOME_MESSAGE.value, welcome_message) ## 欢迎消息
builder.add_node(NodeName.INTENT_DETECTION.value, intent_detection) ## 意图检测
builder.add_node(NodeName.TASK_RESULT_CONFIRM.value, task_result_confirm) ## 任务结果确认

## 数据加载入口节点（优化1：仅在意图检测后、业务分支才会执行，闲聊分支不加载）
builder.add_node(LoadDataNodeName.DATA_LOAD_ENTRY.value, data_load_entry) ## 数据加载入口（统一加载后分流到业务子图）

## 生成建议节点
builder.add_node(NodeName.CHAT_SUGGESTION.value, sub_chat_suggestion_graph)         ## 生成客户聊天建议
builder.add_node(NodeName.KF_CHAT_SUGGESTION.value, sub_kf_chat_suggestion_graph)   ## 生成客服聊天建议
builder.add_node(NodeName.TAG_SUGGESTION.value, sub_tag_graph)                      ## 生成客户标签
builder.add_node(NodeName.PROFILE_SUGGESTION.value, sub_profile_graph)              ## 生成客户画像
builder.add_node(NodeName.SCHEDULE_SUGGESTION.value, sub_schedule_graph)            ## 生成客户日程
builder.add_node(NodeName.NO_CLEAR_INTENTION.value, sub_talk_graph)                 ## 未明确意图

## 执行顺序：清理状态 -> 欢迎消息 -> 意图检测
builder.add_edge(START, NodeName.CLEANUP_STATE.value)
builder.add_edge(NodeName.CLEANUP_STATE.value, NodeName.WELCOME_MESSAGE.value)
builder.add_edge(NodeName.WELCOME_MESSAGE.value, NodeName.INTENT_DETECTION.value)

## 意图检测后路由（由 intent_detection 节点的 Command(goto) 控制）：
## - 闲聊（未明确意图）：直接进 sub_talk_graph，不加载任何业务数据（优化1）
## - 5个业务意图：先进入 data_load_entry 统一加载数据，再由该节点按 current_intent 分流到对应子图
## 子图执行完成后，调用NodeName.TASK_RESULT_CONFIRM节点

builder.add_edge(NodeName.CHAT_SUGGESTION.value,     NodeName.TASK_RESULT_CONFIRM.value)
builder.add_edge(NodeName.KF_CHAT_SUGGESTION.value,  NodeName.TASK_RESULT_CONFIRM.value)
builder.add_edge(NodeName.TAG_SUGGESTION.value,      NodeName.TASK_RESULT_CONFIRM.value)
builder.add_edge(NodeName.PROFILE_SUGGESTION.value,  NodeName.TASK_RESULT_CONFIRM.value)
builder.add_edge(NodeName.SCHEDULE_SUGGESTION.value, NodeName.TASK_RESULT_CONFIRM.value)
builder.add_edge(NodeName.NO_CLEAR_INTENTION.value,  NodeName.TASK_RESULT_CONFIRM.value)
builder.add_edge(NodeName.TASK_RESULT_CONFIRM.value, END)

if os.getenv("LANGFUSE_ENABLED", "false").lower() == "true":
    from langfuse.langchain import CallbackHandler
    langfuse_handler = CallbackHandler()
    graph = builder.compile().with_config({"callbacks": [langfuse_handler]})
else:
    graph = builder.compile()