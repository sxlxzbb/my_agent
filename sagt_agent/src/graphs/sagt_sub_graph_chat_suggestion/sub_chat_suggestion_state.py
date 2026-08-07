import operator
from typing import TypedDict, Annotated, List
from src.graphs.sagt_state import SagtStateField
from src.models.sagt_models import CustomerInfo, CustomerProfile, ReplySuggestion, CustomerTags, TaskResult, \
    EmployeeInfo, NodeResult, ChatHistory
from enum import Enum

class SubChatSuggestionStateField(str, Enum):
    """子图状态字段名称枚举"""
    
    ## 输入字段（字段值引用主图 SagtStateField，确保与主图/基类同名字段一致）
    EMPLOYEE_INFO    = SagtStateField.EMPLOYEE_INFO.value
    CHAT_HISTORY     = SagtStateField.CHAT_HISTORY.value
    CUSTOMER_INFO    = SagtStateField.CUSTOMER_INFO.value

    ## 中间输出字段
    SUGGESTION_CHAT     = SagtStateField.SUGGESTION_CHAT.value

    ## 输出字段
    TASK_RESULT         = SagtStateField.TASK_RESULT.value
    NODE_RESULT         = SagtStateField.NODE_RESULT.value

class SubChatSuggestionInputState(TypedDict):
    """子图的输入状态"""
    employee_info:      EmployeeInfo
    chat_history:       ChatHistory
    customer_info:      CustomerInfo

class SubChatSuggestionIntermediateOutputState(TypedDict):
    """子图的中间输出状态"""
    suggestion_chat:    ReplySuggestion

class SubChatSuggestionOutputState(TypedDict):
    """子图的输出状态"""
    task_result:        TaskResult  # 任务结果
    node_result:        Annotated[List[NodeResult], operator.add]  # 节点执行结果

# 使用多重继承，自动合并所有字段
class SubChatSuggestionState(SubChatSuggestionInputState, SubChatSuggestionIntermediateOutputState, SubChatSuggestionOutputState):
    """
    完整的子图状态，包含输入和输出字段
    继承自 SubChatSuggestionInputState, SubChatSuggestionIntermediateOutputState 和 SubChatSuggestionOutputState
    """
    pass