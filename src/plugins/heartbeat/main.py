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
    
check = on_alconna(
    Alconna("#check", Args["domain?", str], meta=CommandMeta(compact=True))
)
@check.handle()
async def _(
    domain: Match[str] = AlconnaMatch("domain")
):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"https://{domain.result}", timeout=5.0, follow_redirects=True)
            if response.status_code == 200:
                await check.finish(group_id=OUTPUT_GROUP, message="Connection successfully with 200 OK.")
            else:
                await check.finish(group_id=OUTPUT_GROUP, message="Connection failed.")
    except Exception as e:
        await check.finish(group_id=OUTPUT_GROUP, message=f"Connection failed: {e}")
    