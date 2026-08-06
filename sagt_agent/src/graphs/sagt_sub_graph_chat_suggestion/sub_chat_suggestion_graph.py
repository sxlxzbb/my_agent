from langgraph.graph import START, END, StateGraph
from src.graphs.sagt_sub_graph_chat_suggestion.sub_chat_suggestion_state import SubChatSuggestionState
from src.graphs.sagt_sub_graph_chat_suggestion.sub_chat_suggestion_state import SubChatSuggestionInputState
from src.graphs.sagt_sub_graph_chat_suggestion.sub_chat_suggestion_state import SubChatSuggestionOutputState
from src.graphs.sagt_sub_graph_chat_suggestion.sub_chat_suggestion_node import generate_chat_suggestion_node
from src.graphs.sagt_sub_graph_chat_suggestion.sub_chat_suggestion_node import welcome_message_node
from src.graphs.sagt_sub_graph_chat_suggestion.sub_chat_suggestion_node import NodeName
from src.graphs.sagt_node_load_data import NodeName as LoadDataNodeName, load_employee_info_node, \
    load_customer_info_node, load_chat_history_node
from src.graphs.sagt_state import SagtConfig

builder = StateGraph(
    state_schema=SubChatSuggestionState, 
    input_schema=SubChatSuggestionInputState,  
    output_schema=SubChatSuggestionOutputState, 
    config_schema=SagtConfig
)

builder.add_node(NodeName.WELCOME_MESSAGE.value, welcome_message_node)
builder.add_node(LoadDataNodeName.LOAD_EMPLOYEE_INFO.value, load_employee_info_node) ## 加载员工信息
builder.add_node(LoadDataNodeName.LOAD_CUSTOMER_INFO.value, load_customer_info_node) ## 加载客户信息
builder.add_node(LoadDataNodeName.LOAD_CHAT_HISTORY.value, load_chat_history_node)   ## 加载聊天消息
builder.add_node(NodeName.GENERATE_CHAT_SUGGESTION.value, generate_chat_suggestion_node)

builder.add_edge(START, NodeName.WELCOME_MESSAGE.value)
builder.add_edge(NodeName.WELCOME_MESSAGE.value, LoadDataNodeName.LOAD_EMPLOYEE_INFO.value)
builder.add_edge(LoadDataNodeName.LOAD_EMPLOYEE_INFO.value, LoadDataNodeName.LOAD_CUSTOMER_INFO.value)
builder.add_edge(LoadDataNodeName.LOAD_CUSTOMER_INFO.value, LoadDataNodeName.LOAD_CHAT_HISTORY.value)
builder.add_edge(LoadDataNodeName.LOAD_CHAT_HISTORY.value, NodeName.GENERATE_CHAT_SUGGESTION.value)
builder.add_edge(NodeName.GENERATE_CHAT_SUGGESTION.value, END)

sub_chat_suggestion_graph = builder.compile()