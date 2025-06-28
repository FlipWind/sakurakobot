from ..utils import *

@scheduler.scheduled_job("cron", hour="*/6", id="check")
async def run():
    bot = nonebot.get_bot()
    await bot.send_group_msg(group_id=OUTPUT_GROUP, message="我的心脏还在跳动着啊")

heartbeat = on_alconna(Alconna("#beat"))
@heartbeat.handle()
async def _(event: GroupMessageEvent):
    await heartbeat.finish("我的心脏还在跳动着啊。")

version = on_alconna(Alconna("#ver"))
@version.handle()
async def _(event: GroupMessageEvent):
    await version.finish(f"""Sakurako Bot
Version {VERSION}

Developed by FlipWind""")
    
driver = get_driver()

@driver.on_bot_connect
async def _(bot: Bot):
    await bot.send_group_msg(group_id=OUTPUT_GROUP, message="Sakurako Bot Started.")
