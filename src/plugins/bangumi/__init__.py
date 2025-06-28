from nonebot import get_plugin_config
from nonebot.plugin import PluginMetadata

__plugin_meta__ = PluginMetadata(
    name="bangumi",
    description="",
    usage="",
)

from . import search as search
