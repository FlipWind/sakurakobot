from ..utils import *

group_add = on_request()

@group_add.handle()
async def _(bot: Bot, event: GroupRequestEvent):
    if not get_bot_is_admin(bot, event.group_id):
        return
    
    user_id = event.user_id
    comment = event.comment
    flag = event.flag
    
    nickname = await bot.get_stranger_info(user_id=user_id, no_cache=True)
    nickname = nickname.get("nickname", "未知用户")
    
    await group_add.finish(f"""倪群收到了一个新的加群请求。
来自 {nickname}({user_id})。
验证消息：「{comment}」

对此条消息回复 y 以同意，n 为拒绝。
""")