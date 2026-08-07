import operator
from typing import TypedDict, Annotated, List
from enum import Enum

from src.models.sagt_models import (
    EmployeeInfo, TagSetting, CustomerInfo, CustomerProfile, CustomerTags,
    ChatHistory, KFChatHistory, OrderHistory, NodeResult,
)
from src.graphs.sagt_node_load_data import (
    NodeName as LoadDataNodeName,
    load_employee_info_node, load_tag_setting_node, load_customer_info_node,
    load_chat_history_node, load_kf_chat_history_node, load_order_history_node,
)
from src.graphs.sagt_state import SagtStateField


class SagtDataState(TypedDict):
    """
    业务数据状态基类（思路C）。

    把所有"需要从 store 加载的业务数据字段"集中声明在这里，
    各子图的 InputState 继承本类即可按需拥有这些字段，无需每子图重复声明。

    注意：字段名必须与主图 SagtStateField 的值保持一致，
    否则主图调用子图时无法按同名字段把数据传入子图。
    """
    employee_info:    EmployeeInfo
    tag_setting:      TagSetting
    customer_info:    CustomerInfo
    customer_profile: CustomerProfile
    customer_tags:    CustomerTags
    chat_history:     ChatHistory
    kf_chat_history:  KFChatHistory
    order_history:    OrderHistory


class DataField(str, Enum):
    """业务数据字段名枚举，与 SagtDataState 字段一一对应"""
    EMPLOYEE_INFO    = SagtStateField.EMPLOYEE_INFO.value     # "employee_info"
    TAG_SETTING      = SagtStateField.TAG_SETTING.value       # "tag_setting"
    CUSTOMER_INFO    = SagtStateField.CUSTOMER_INFO.value     # "customer_info"
    CHAT_HISTORY     = SagtStateField.CHAT_HISTORY.value      # "chat_history"
    KF_CHAT_HISTORY  = SagtStateField.KF_CHAT_HISTORY.value    # "kf_chat_history"
    ORDER_HISTORY    = SagtStateField.ORDER_HISTORY.value     # "order_history"


# 字段 -> (load 节点函数, load 节点在图里的名称)
# 新增/调整某个数据的加载方式，只改这里即可
LOAD_FIELD_MAP = {
    DataField.EMPLOYEE_INFO:   (load_employee_info_node,   LoadDataNodeName.LOAD_EMPLOYEE_INFO.value),
    DataField.TAG_SETTING:     (load_tag_setting_node,     LoadDataNodeName.LOAD_TAG_SETTING.value),
    DataField.CUSTOMER_INFO:   (load_customer_info_node,   LoadDataNodeName.LOAD_CUSTOMER_INFO.value),
    DataField.CHAT_HISTORY:    (load_chat_history_node,    LoadDataNodeName.LOAD_CHAT_HISTORY.value),
    DataField.KF_CHAT_HISTORY: (load_kf_chat_history_node, LoadDataNodeName.LOAD_KF_CHAT_HISTORY.value),
    DataField.ORDER_HISTORY:   (load_order_history_node,   LoadDataNodeName.LOAD_ORDER_HISTORY.value),
}


def build_data_load_nodes(builder, needed_fields: List[DataField], entry: str, tail: str = None):
    """
    按需把 load 节点装配进子图，并串成一条链：
        entry -> load1 -> load2 -> ... -> (tail)

    :param builder:      子图的 StateGraph builder
    :param needed_fields:本子图需要加载的字段列表（DataField 枚举）
    :param entry:        链的起点节点名（如 welcome_message 节点名）
    :param tail:         链终点后接续的节点名；为 None 时链尾即为最后一个 load 节点
    """
    prev = entry
    for field in needed_fields:
        load_fn, load_name = LOAD_FIELD_MAP[field]
        builder.add_node(load_name, load_fn)
        builder.add_edge(prev, load_name)
        prev = load_name
    if tail is not None:
        builder.add_edge(prev, tail)


def get_user_context(state: dict) -> dict:
    """
    从子图 state 里取出所有已加载的业务数据字段，打包成 dict，
    供 LLM 拼 prompt 使用。状态里没有的字段会自动跳过。

    :param state: 子图当前 state（dict）
    :return: 仅包含已存在业务数据字段的 dict
    """
    return {
        field.value: state[field.value]
        for field in DataField
        if field.value in state and state[field.value] is not None
    }
