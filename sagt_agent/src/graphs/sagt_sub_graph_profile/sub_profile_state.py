import operator
from typing import TypedDict, Annotated, List
from src.graphs.sagt_state import SagtStateField
from src.models.sagt_models import CustomerProfile, TaskResult, NodeResult
from src.graphs.sagt_data_state import SagtDataState
from enum import Enum


class SubProfileStateField(str, Enum):
    """子图状态字段名称枚举"""
    
    ## 输入字段（来自 SagtDataState 基类，无需重复声明）

    ## 中间输出字段
    NOTIFY_CONTENT = SagtStateField.NOTIFY_CONTENT.value
    SUGGESTION_PROFILE = SagtStateField.SUGGESTION_PROFILE.value

    ## 输出字段
    TASK_RESULT = SagtStateField.TASK_RESULT.value
    NODE_RESULT = SagtStateField.NODE_RESULT.value


class SubProfileInputState(SagtDataState):
    """子图的输入状态（继承 SagtDataState，按需拥有全部业务数据字段）"""
    pass

class SubProfileIntermediateOutputState(TypedDict):
    notify_content:     str
    suggestion_profile: CustomerProfile


class SubProfileOutputState(TypedDict):
    task_result: TaskResult
    node_result: Annotated[List[NodeResult], operator.add]

# 使用多重继承，自动合并所有字段
class SubProfileState(SubProfileInputState, SubProfileIntermediateOutputState, SubProfileOutputState):
    """
    完整的子图状态，包含输入和输出字段
    继承自 SubProfileInputState, SubProfileIntermediateOutputState 和 SubProfileOutputState
    """
    pass