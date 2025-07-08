from ..utils import *

like = on_alconna(Alconna("#点赞"), aliases=("#赞我", "#赞"))

@like.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    user_id = event.user_id
    count = 0
    
    try:
        for i in range(5):
            await bot.send_like(user_id=user_id, times=10)
            count += 10
    except Exception:
        pass
    
    if count == 0:
        await like.finish("咱今天点不了更多的赞了喵。")
    await like.finish(f"哼哼，本喵刚刚已经给你点了 {count} 个赞喵！")
