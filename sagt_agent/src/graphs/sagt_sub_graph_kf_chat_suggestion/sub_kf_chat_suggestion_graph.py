from langgraph.graph import START, END, StateGraph
from src.graphs.sagt_sub_graph_kf_chat_suggestion.sub_kf_chat_suggestion_state import SubKFChatSuggestionState
from src.graphs.sagt_sub_graph_kf_chat_suggestion.sub_kf_chat_suggestion_state import SubKFChatSuggestionInputState
from src.graphs.sagt_sub_graph_kf_chat_suggestion.sub_kf_chat_suggestion_state import SubKFChatSuggestionOutputState
from src.graphs.sagt_sub_graph_kf_chat_suggestion.sub_kf_chat_suggestion_node import generate_kf_chat_suggestion_node
from src.graphs.sagt_sub_graph_kf_chat_suggestion.sub_kf_chat_suggestion_node import welcome_message_node
from src.graphs.sagt_sub_graph_kf_chat_suggestion.sub_kf_chat_suggestion_node import NodeName
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
builder.add_edge(NodeName.WELCOME_MESSAGE.value, NodeName.GENERATE_KF_CHAT_SUGGESTION.value)
builder.add_edge(NodeName.GENERATE_KF_CHAT_SUGGESTION.value, END)

sub_kf_chat_suggestion_graph = builder.compile()