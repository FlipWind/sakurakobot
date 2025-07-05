from ..utils import *
from .render import rend_quote, QuoteMessage, RankType

quote = on_alconna(Alconna("#qt"))

@quote.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    if not event.reply:
        await quote.finish("看起来你还没有指定消息喵。")
    
    if COMMAND_OUTPUT:
        await quote.send(f"Handle [#qt] with Message {event.reply.message_id}")
    profile = await bot.get_group_member_info(
        group_id=event.group_id, user_id=event.reply.sender.user_id, no_cache=True # type: ignore
    )
    
    rank_type = RankType.NORMAL
    if profile['role'] == 'owner':
        rank_type = RankType.HEAD
    elif profile['role'] == 'admin':
        rank_type = RankType.ADMIN
    else:
        rank_type = RankType.NORMAL
        
    header = profile["title"]
    if rank_type == RankType.NORMAL and header:
        rank_type = RankType.SPECIAL
    
    if not header:
        if profile['role'] == 'owner':
            header = "群主"
        elif profile['role'] == 'admin':
            header = "管理员"
        else:
            header = "成员"

    quote_message = QuoteMessage(
        nickname=profile['nickname'],
        rank=f"LV{profile['level']}",
        header=header,
        profile=f"http://q.qlogo.cn/headimg_dl?spec=640&dst_uin={event.reply.sender.user_id}",
        message=event.reply.message,
        rank_type=rank_type
    )

    quote_image = await rend_quote(quote_message)
    image_data = io.BytesIO()
    quote_image.save(image_data, format="PNG")
    image_data_bytes = image_data.getvalue()
    
    encoded_image = base64.b64encode(image_data_bytes).decode("utf-8")
    
    await quote.finish(Message([
        MessageSegment.reply(event.message_id),
        MessageSegment.image(f"base64://{encoded_image}")
    ]))
