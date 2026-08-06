from langgraph.graph import START, END, StateGraph
from src.graphs.sagt_sub_graph_profile.sub_profile_state import SubProfileState, SubProfileInputState, SubProfileOutputState
from src.graphs.sagt_sub_graph_profile.sub_profile_node import generate_customer_profile, update_customer_profile, human_feedback, notify_human_feedback, welcome_message, notify_human_result
from src.graphs.sagt_sub_graph_profile.sub_profile_node import NodeName
from src.graphs.sagt_node_load_data import NodeName as LoadDataNodeName, load_kf_chat_history_node, \
    load_order_history_node, load_tag_setting_node, load_customer_info_node
from src.graphs.sagt_state import SagtConfig

builder = StateGraph(state_schema=SubProfileState, input_schema=SubProfileInputState, output_schema=SubProfileOutputState, config_schema=SagtConfig)

builder.add_node(NodeName.WELCOME_MESSAGE.value, welcome_message)
builder.add_node(LoadDataNodeName.LOAD_KF_CHAT_HISTORY.value, load_kf_chat_history_node)    ## 加载微信客服信息
builder.add_node(LoadDataNodeName.LOAD_ORDER_HISTORY.value, load_order_history_node)        ## 加载订单信息
builder.add_node(LoadDataNodeName.LOAD_CUSTOMER_INFO.value, load_customer_info_node)        ## 加载客户信息
builder.add_node(NodeName.PROFILE_SUGGEST.value, generate_customer_profile)
builder.add_node(NodeName.PROFILE_UPDATE.value, update_customer_profile)
builder.add_node(NodeName.PROFILE_FEEDBACK.value, human_feedback)
builder.add_node(NodeName.PROFILE_NOTIFY_FEEDBACK.value, notify_human_feedback)
builder.add_node(NodeName.PROFILE_NOTIFY_RESULT.value, notify_human_result)

builder.add_edge(START, NodeName.WELCOME_MESSAGE.value)     ## 欢迎消息节点
builder.add_edge(NodeName.WELCOME_MESSAGE.value, LoadDataNodeName.LOAD_KF_CHAT_HISTORY.value)
builder.add_edge(LoadDataNodeName.LOAD_KF_CHAT_HISTORY.value, LoadDataNodeName.LOAD_ORDER_HISTORY.value)
builder.add_edge(LoadDataNodeName.LOAD_ORDER_HISTORY.value, LoadDataNodeName.LOAD_CUSTOMER_INFO.value)
builder.add_edge(LoadDataNodeName.LOAD_CUSTOMER_INFO.value, NodeName.PROFILE_SUGGEST.value)  ## 生成客户profile节点
builder.add_edge(NodeName.PROFILE_SUGGEST.value, NodeName.PROFILE_NOTIFY_FEEDBACK.value)     ## 发送人工确认通知节点
builder.add_edge(NodeName.PROFILE_NOTIFY_FEEDBACK.value, NodeName.PROFILE_FEEDBACK.value)    ## 人工反馈节点
## 人工反馈节点，如果人工反馈为ok，则跳转到profile_update节点，如果人工反馈为discard，则跳转到end，如果人工反馈为recreate，则跳转到profile_suggest节点。
builder.add_edge(NodeName.PROFILE_UPDATE.value, NodeName.PROFILE_NOTIFY_RESULT.value)        ## 发送任务结果通知节点
builder.add_edge(NodeName.PROFILE_NOTIFY_RESULT.value, END) ## 结束节点

sub_profile_graph = builder.compile()