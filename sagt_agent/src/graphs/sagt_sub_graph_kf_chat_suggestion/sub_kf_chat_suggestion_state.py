import operator
from typing import TypedDict, Annotated, List
from src.graphs.sagt_state import SagtStateField
from src.models.sagt_models import KFChatHistory, CustomerInfo, ReplySuggestion, TaskResult, NodeResult
from src.graphs.sagt_data_state import SagtDataState
from enum import Enum


class SubKFChatSuggestionStateField(str, Enum):
    """子图状态字段名称枚举"""
    
    ## 输入字段（来自 SagtDataState 基类，无需重复声明）

    ## 中间输出字段
    SUGGESTION_KF = SagtStateField.SUGGESTION_KF.value

    ## 输出字段
    TASK_RESULT = SagtStateField.TASK_RESULT.value
    NODE_RESULT = SagtStateField.NODE_RESULT.value

class SubKFChatSuggestionInputState(SagtDataState):
    """子图的输入状态（继承 SagtDataState，按需拥有全部业务数据字段）"""
    pass

class SubKFChatSuggestionIntermediateOutputState(TypedDict):
    """子图的中间输出状态"""
    suggestion_kf:      ReplySuggestion

class SubKFChatSuggestionOutputState(TypedDict):
    """子图的输出状态"""
    task_result:        TaskResult
    node_result:        Annotated[List[NodeResult], operator.add]
    
# 使用多重继承，自动合并所有字段
class SubKFChatSuggestionState(SubKFChatSuggestionInputState, SubKFChatSuggestionIntermediateOutputState, SubKFChatSuggestionOutputState):
    """
    完整的子图状态，包含输入和输出字段
    继承自 SubKFChatSuggestionInputState, SubKFChatSuggestionIntermediateOutputState 和 SubKFChatSuggestionOutputState
    """
    pass