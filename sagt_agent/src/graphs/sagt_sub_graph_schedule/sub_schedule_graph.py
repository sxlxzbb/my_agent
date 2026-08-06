from langgraph.graph import START, END, StateGraph
from src.graphs.sagt_sub_graph_schedule.sub_schedule_state import SubScheduleState, SubScheduleInputState, SubScheduleOutputState
from src.graphs.sagt_sub_graph_schedule.sub_schedule_node import generate_schedule_node, create_schedule_node, welcome_message_node
from src.graphs.sagt_sub_graph_schedule.sub_schedule_node import NodeName
from src.graphs.sagt_node_load_data import NodeName as LoadDataNodeName, load_customer_info_node, load_chat_history_node
from src.graphs.sagt_state import SagtConfig

builder = StateGraph(state_schema=SubScheduleState, input_schema=SubScheduleInputState, output_schema=SubScheduleOutputState, config_schema=SagtConfig)

builder.add_node(NodeName.WELCOME_MESSAGE.value, welcome_message_node)
builder.add_node(LoadDataNodeName.LOAD_CUSTOMER_INFO.value, load_customer_info_node) ## 加载客户信息
builder.add_node(LoadDataNodeName.LOAD_CHAT_HISTORY.value, load_chat_history_node)   ## 加载聊天消息
builder.add_node(NodeName.GENERATE_SCHEDULE.value, generate_schedule_node)
builder.add_node(NodeName.CREATE_SCHEDULE.value, create_schedule_node)

builder.add_edge(START, NodeName.WELCOME_MESSAGE.value)
builder.add_edge(NodeName.WELCOME_MESSAGE.value, LoadDataNodeName.LOAD_CUSTOMER_INFO.value)
builder.add_edge(LoadDataNodeName.LOAD_CUSTOMER_INFO.value, LoadDataNodeName.LOAD_CHAT_HISTORY.value)
builder.add_edge(LoadDataNodeName.LOAD_CHAT_HISTORY.value, NodeName.GENERATE_SCHEDULE.value)
builder.add_edge(NodeName.GENERATE_SCHEDULE.value, NodeName.CREATE_SCHEDULE.value)
builder.add_edge(NodeName.CREATE_SCHEDULE.value, END)

sub_schedule_graph = builder.compile()