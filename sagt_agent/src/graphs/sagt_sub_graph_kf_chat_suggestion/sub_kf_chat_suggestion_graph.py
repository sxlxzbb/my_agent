from langgraph.graph import START, END, StateGraph
from src.graphs.sagt_sub_graph_kf_chat_suggestion.sub_kf_chat_suggestion_state import SubKFChatSuggestionState
from src.graphs.sagt_sub_graph_kf_chat_suggestion.sub_kf_chat_suggestion_state import SubKFChatSuggestionInputState
from src.graphs.sagt_sub_graph_kf_chat_suggestion.sub_kf_chat_suggestion_state import SubKFChatSuggestionOutputState
from src.graphs.sagt_sub_graph_kf_chat_suggestion.sub_kf_chat_suggestion_node import generate_kf_chat_suggestion_node
from src.graphs.sagt_sub_graph_kf_chat_suggestion.sub_kf_chat_suggestion_node import welcome_message_node
from src.graphs.sagt_sub_graph_kf_chat_suggestion.sub_kf_chat_suggestion_node import NodeName
from src.graphs.sagt_node_load_data import NodeName as LoadDataNodeName, load_customer_info_node, \
    load_kf_chat_history_node
from src.graphs.sagt_state import SagtConfig

builder = StateGraph(
    state_schema=SubKFChatSuggestionState, 
    input_schema=SubKFChatSuggestionInputState, 
    output_schema=SubKFChatSuggestionOutputState, 
    config_schema=SagtConfig
)

builder.add_node(NodeName.WELCOME_MESSAGE.value, welcome_message_node)
builder.add_node(LoadDataNodeName.LOAD_CUSTOMER_INFO.value, load_customer_info_node)     ## 加载客户信息
builder.add_node(LoadDataNodeName.LOAD_KF_CHAT_HISTORY.value, load_kf_chat_history_node) ## 加载微信客服信息
builder.add_node(NodeName.GENERATE_KF_CHAT_SUGGESTION.value, generate_kf_chat_suggestion_node)

builder.add_edge(START, NodeName.WELCOME_MESSAGE.value)
builder.add_edge(NodeName.WELCOME_MESSAGE.value, LoadDataNodeName.LOAD_CUSTOMER_INFO.value)
builder.add_edge(LoadDataNodeName.LOAD_CUSTOMER_INFO.value, LoadDataNodeName.LOAD_KF_CHAT_HISTORY.value)
builder.add_edge(LoadDataNodeName.LOAD_KF_CHAT_HISTORY.value, NodeName.GENERATE_KF_CHAT_SUGGESTION.value)
builder.add_edge(NodeName.GENERATE_KF_CHAT_SUGGESTION.value, END)

sub_kf_chat_suggestion_graph = builder.compile()