from langgraph.graph import START, END, StateGraph
from src.graphs.sagt_sub_graph_kf_chat_suggestion.sub_kf_chat_suggestion_state import SubKFChatSuggestionState
from src.graphs.sagt_sub_graph_kf_chat_suggestion.sub_kf_chat_suggestion_state import SubKFChatSuggestionInputState
from src.graphs.sagt_sub_graph_kf_chat_suggestion.sub_kf_chat_suggestion_state import SubKFChatSuggestionOutputState
from src.graphs.sagt_sub_graph_kf_chat_suggestion.sub_kf_chat_suggestion_node import generate_kf_chat_suggestion_node
from src.graphs.sagt_sub_graph_kf_chat_suggestion.sub_kf_chat_suggestion_node import welcome_message_node
from src.graphs.sagt_sub_graph_kf_chat_suggestion.sub_kf_chat_suggestion_node import NodeName
from src.graphs.sagt_data_state import build_data_load_nodes, DataField
from src.graphs.sagt_state import SagtConfig

builder = StateGraph(
    state_schema=SubKFChatSuggestionState, 
    input_schema=SubKFChatSuggestionInputState, 
    output_schema=SubKFChatSuggestionOutputState, 
    config_schema=SagtConfig
)

builder.add_node(NodeName.WELCOME_MESSAGE.value, welcome_message_node)
builder.add_node(NodeName.GENERATE_KF_CHAT_SUGGESTION.value, generate_kf_chat_suggestion_node)

builder.add_edge(START, NodeName.WELCOME_MESSAGE.value)
# 按 kf_chat_suggestion 子图需要加载的数据字段，自动装配 load 节点链：welcome -> customer_info -> kf_chat -> generate
build_data_load_nodes(
    builder,
    needed_fields=[DataField.CUSTOMER_INFO, DataField.KF_CHAT_HISTORY],
    entry=NodeName.WELCOME_MESSAGE.value,
    tail=NodeName.GENERATE_KF_CHAT_SUGGESTION.value,
)
builder.add_edge(NodeName.GENERATE_KF_CHAT_SUGGESTION.value, END)

sub_kf_chat_suggestion_graph = builder.compile()