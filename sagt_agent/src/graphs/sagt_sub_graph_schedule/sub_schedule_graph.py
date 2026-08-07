from langgraph.graph import START, END, StateGraph
from src.graphs.sagt_sub_graph_schedule.sub_schedule_state import SubScheduleState, SubScheduleInputState, SubScheduleOutputState
from src.graphs.sagt_sub_graph_schedule.sub_schedule_node import generate_schedule_node, create_schedule_node, welcome_message_node
from src.graphs.sagt_sub_graph_schedule.sub_schedule_node import NodeName
from src.graphs.sagt_data_state import build_data_load_nodes, DataField
from src.graphs.sagt_state import SagtConfig

builder = StateGraph(state_schema=SubScheduleState, input_schema=SubScheduleInputState, output_schema=SubScheduleOutputState, config_schema=SagtConfig)

builder.add_node(NodeName.WELCOME_MESSAGE.value, welcome_message_node)
builder.add_node(NodeName.GENERATE_SCHEDULE.value, generate_schedule_node)
builder.add_node(NodeName.CREATE_SCHEDULE.value, create_schedule_node)

builder.add_edge(START, NodeName.WELCOME_MESSAGE.value)
# 按 schedule 子图需要加载的数据字段，自动装配 load 节点链：welcome -> customer_info -> chat -> generate
build_data_load_nodes(
    builder,
    needed_fields=[DataField.CUSTOMER_INFO, DataField.CHAT_HISTORY],
    entry=NodeName.WELCOME_MESSAGE.value,
    tail=NodeName.GENERATE_SCHEDULE.value,
)
builder.add_edge(NodeName.GENERATE_SCHEDULE.value, NodeName.CREATE_SCHEDULE.value)
builder.add_edge(NodeName.CREATE_SCHEDULE.value, END)

sub_schedule_graph = builder.compile()