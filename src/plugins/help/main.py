from ..utils import *

help = on_alconna(Alconna("#help"))

@help.handle()
async def _(bot: Bot, event: Event):
    help_msg = Message(MessageSegment.image(f"file://{ASSETS_PATH}/help/content.png"))
    await help.finish(help_msg)
