from langgraph.graph import START, END, StateGraph
from src.graphs.sagt_sub_graph_tag.sub_tag_state import SubTagState, SubTagInputState, SubTagOutputState
from src.graphs.sagt_sub_graph_tag.sub_tag_node import generate_customer_tag, update_customer_tag, human_feedback, welcome_message_node, notify_human_feedback, notify_human_result
from src.graphs.sagt_sub_graph_tag.sub_tag_node import NodeName
from src.graphs.sagt_node_load_data import NodeName as LoadDataNodeName, load_tag_setting_node, load_customer_info_node, \
    load_chat_history_node, load_kf_chat_history_node, load_order_history_node
from src.graphs.sagt_state import SagtConfig

builder = StateGraph(state_schema=SubTagState, input_schema=SubTagInputState, output_schema=SubTagOutputState, config_schema=SagtConfig)

builder.add_node(NodeName.WELCOME_MESSAGE.value, welcome_message_node)
builder.add_node(LoadDataNodeName.LOAD_TAG_SETTING.value, load_tag_setting_node)        ## 加载标签设置
builder.add_node(LoadDataNodeName.LOAD_CUSTOMER_INFO.value, load_customer_info_node)    ## 加载客户信息
builder.add_node(LoadDataNodeName.LOAD_CHAT_HISTORY.value, load_chat_history_node)      ## 加载聊天消息
builder.add_node(LoadDataNodeName.LOAD_KF_CHAT_HISTORY.value, load_kf_chat_history_node) ## 加载微信客服信息
builder.add_node(LoadDataNodeName.LOAD_ORDER_HISTORY.value, load_order_history_node)    ## 加载订单信息
builder.add_node(NodeName.GENERATE_TAG.value, generate_customer_tag)
builder.add_node(NodeName.NOTIFY_FEEDBACK.value, notify_human_feedback)
builder.add_node(NodeName.HUMAN_FEEDBACK.value, human_feedback)
builder.add_node(NodeName.UPDATE_TAG.value, update_customer_tag)
builder.add_node(NodeName.NOTIFY_RESULT.value, notify_human_result)

builder.add_edge(START, NodeName.WELCOME_MESSAGE.value) ## 欢迎消息节点
builder.add_edge(NodeName.WELCOME_MESSAGE.value, LoadDataNodeName.LOAD_TAG_SETTING.value)
builder.add_edge(LoadDataNodeName.LOAD_TAG_SETTING.value, LoadDataNodeName.LOAD_CUSTOMER_INFO.value)
builder.add_edge(LoadDataNodeName.LOAD_CUSTOMER_INFO.value, LoadDataNodeName.LOAD_CHAT_HISTORY.value)
builder.add_edge(LoadDataNodeName.LOAD_CHAT_HISTORY.value, LoadDataNodeName.LOAD_KF_CHAT_HISTORY.value)
builder.add_edge(LoadDataNodeName.LOAD_KF_CHAT_HISTORY.value, LoadDataNodeName.LOAD_ORDER_HISTORY.value)
builder.add_edge(LoadDataNodeName.LOAD_ORDER_HISTORY.value, NodeName.GENERATE_TAG.value)   ## 生成客户标签节点
builder.add_edge(NodeName.GENERATE_TAG.value, NodeName.NOTIFY_FEEDBACK.value)   ## 发送人工确认通知节点
builder.add_edge(NodeName.NOTIFY_FEEDBACK.value, NodeName.HUMAN_FEEDBACK.value) ## 人工反馈节点
# 人工反馈节点，如果人工反馈为ok，则跳转到update_tag节点，如果人工反馈为discard，则跳转到end，如果人工反馈为recreate，则跳转到generate_tag节点。
builder.add_edge(NodeName.UPDATE_TAG.value, NodeName.NOTIFY_RESULT.value)  ## 发送任务结果通知节点
builder.add_edge(NodeName.NOTIFY_RESULT.value, END) ## 结束节点

sub_tag_graph = builder.compile()