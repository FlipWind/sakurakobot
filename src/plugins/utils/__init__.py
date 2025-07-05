from typing import Dict, Any, Optional, List
from nonebot import logger, require, on_command, on_message, get_driver, on_notice, on_request
from nonebot.exception import IgnoredException
from nonebot.message import event_preprocessor
from nonebot.typing import T_State

from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from urllib.parse import urlparse
from fuzzywuzzy import fuzz
from pilmoji import Pilmoji
from enum import Enum
import os
import yaml
import datetime, time
import nonebot
import httpx
import json
import textwrap
import io
import base64
import json
import pathlib
import re
import random
import asyncio
import requests

require("nonebot_plugin_alconna")
from arclet.alconna import Alconna, Alconna, Args, Option, MultiVar
from nonebot_plugin_alconna import At, on_alconna, AlconnaMatch, Match, CommandMeta, At, Query

from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, Message, MessageSegment, Event, MessageEvent, GroupBanNoticeEvent, GroupRequestEvent
from nonebot.adapters.onebot.v11.exception import ActionFailed

require("nonebot_plugin_apscheduler")
from nonebot_plugin_apscheduler import scheduler

CONFIG_PATH = "config.yaml"
sakurako_state: Dict[str, Any] = {}
_config: Dict[str, Any] = {}

def get_config():
    global _config

    if _config == {}:
        logger.success(f"正在加载配置文件 {CONFIG_PATH}")
        with open(CONFIG_PATH, "r") as f:
            _config = yaml.load(f, Loader=yaml.FullLoader)
        logger.success(f"已加载配置文件。")

    return _config

VERSION = get_config().get("version", 0)

BANNED_GROUPS = get_config().get("banned_groups", [])
SUPPER_USERS = get_config().get("super_users", [])
BOTID = get_config().get("botid", 0)
BOTNICKNAME = get_config().get("botnickname", "Bot")

COMMAND_OUTPUT = get_config().get("command_output", False)
OUTPUT_GROUP = get_config().get("output_group", 0)

LLM_ALIYUN_APIKEY = get_config().get("llm", {}).get("aliyun-apikey", "")
driver = get_driver()

PJSK_ZHDBLINK = get_config().get("pjsk_tool", {}).get("zh_db_link", "")
PJSK_JADBLINK = get_config().get("pjsk_tool", {}).get("ja_db_link", "")
PJSK_DIFFI_CNLINK = get_config().get("pjsk_tool", {}).get("diffi_cndb_link", "")
PJSK_DIFFI_JPLINK = get_config().get("pjsk_tool", {}).get("diffi_jpdb_link", "")

TELEGRAM_REPEATER_ENABLE = get_config().get("telegram", {}).get("enable", False)
TELEGRAM_REPEATER_GROUPS = get_config().get("telegram", {}).get("repeater_groups", [])
TELEGRAM_FORWARD_GROUPS = get_config().get("telegram", {}).get("forward_groups", [])
TELEGRAM_APPID = get_config().get("telegram", {}).get("appid", "")
TELEGRAM_APIHASH = get_config().get("telegram", {}).get("apihash", "")

TELEGRAM_PROXY_TYPE = get_config().get("telegram", {}).get("proxy", {}).get("type", "HTTP")
TELEGRAM_PROXY_ADDR = get_config().get("telegram", {}).get("proxy", {}).get("addr", "")
TELEGRAM_PROXY_PORT = get_config().get("telegram", {}).get("proxy", {}).get("port", 7890)

TELEGRAM_ACC_PHONE = get_config().get("telegram", {}).get("account", {}).get("phone", "")
TELEGRAM_ACC_PASSWORD = get_config().get("telegram", {}).get("account", {}).get("password", "")

### Assets
ASSETS_PATH = pathlib.Path(__file__).parent.parent.parent.parent / "assets"

### Struct

class NodeMessage:
    def __init__(self, content: str, nickname: str, user_id: int):
        self.content = content
        self.nickname = nickname
        self.user_id = user_id

    def __self__(self):
        return f"NodeMessage(content={self.content}, nickname={self.nickname}, user_id={self.user_id})"

### Bot Initialization

@driver.on_bot_connect
async def _():
    global BOT
    global sakurako_state
    BOT = nonebot.get_bot()
    
    await BOT.send_group_msg(group_id=OUTPUT_GROUP, message="Sakurako Bot Started.")

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

async def send_node_messages(event: MessageEvent, messages: List[Any]):
    """
    Args:
        event (Event): 事件对象
        messages (List[NodeMessage]): 转发消息的列表
    """
    bot = BOT
    
    if not messages:
        return
    
    try:
        await bot.send(event, message=ListToNode(messages))
    except ActionFailed as e:
        logger.error(f"Error in sending message: {e}")
        logger.error(messages)
        await bot.send(event, "发送转发消息失败，推测是可能该消息内含有屏蔽词喵~\n改为直接发送喵。")
        
        await bot.send(event, Message("\n".join(messages)))

def get_user_is_admin(event: GroupMessageEvent):
    return event.sender.role != "member"

async def get_bot_is_admin(bot: Bot, group_id: int):
    info = await bot.get_group_member_info(group_id = group_id, user_id = BOTID)
    return info["role"] != "member"