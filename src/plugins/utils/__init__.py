from typing import Dict, Any, Optional, List
from nonebot import logger
from nonebot import require
import os
import yaml

require("nonebot_plugin_alconna")
from arclet.alconna import Alconna, Alconna, Args, Option, MultiVar
from nonebot_plugin_alconna import At, on_alconna, AlconnaMatch, Match, CommandMeta

from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, Message, MessageSegment


CONFIG_PATH = "config.yaml"
_config: Dict[str, Any] = {}

def get_config():
    global _config

    if _config == {}:
        logger.success(f"正在加载配置文件 {CONFIG_PATH}")
        with open(CONFIG_PATH, "r") as f:
            _config = yaml.load(f, Loader=yaml.FullLoader)
        logger.success(f"已加载配置文件。")

    return _config


BANNED_GROUPS = get_config().get("banned_groups", [])
SUPPER_USERS = get_config().get("super_users", [])
BOTID = get_config().get("botid", 0)
BOTNICKNAME = get_config().get("botnickname", "Bot")

COMMAND_OUTPUT = get_config().get("command_output", False)

### Struct


class NodeMessage:
    def __init__(self, content: str, nickname: str, user_id: int):
        self.content = content
        self.nickname = nickname
        self.user_id = user_id

    def __self__(self):
        return f"NodeMessage(content={self.content}, nickname={self.nickname}, user_id={self.user_id})"


### Functions

def ListToNode(list: List[str] | List[NodeMessage]) -> Message:
    """
    Args:
        list (List[str] | List[NodeMessage]): 转发消息的列表

    Returns:
        Message: 返回一个关于转发消息的 Message 对象
    """
    messages = Message()

    for item in list:
        if isinstance(item, str):
            item = NodeMessage(item, BOTNICKNAME, BOTID)

        messages.append(
            MessageSegment.node_custom(
                content=item.content, nickname=item.nickname, user_id=item.user_id
            )
        )

    return messages
