from ..utils import *
from .render import rend_multiple_quotes, QuoteMessage, RankType

quote = on_alconna(Alconna("#qt", Args["nums?", int, 1]))


@quote.handle()
async def _(
    bot: Bot, event: GroupMessageEvent, nums: Match[int] = AlconnaMatch("nums")
):
    if not event.reply:
        await quote.finish("看起来你还没有指定消息喵。")

    if COMMAND_OUTPUT:
        await quote.send(
            f"Handle [#qt] with Message {event.reply.message_id}, nums [{nums.result}]"
        )

    r = await bot.call_api(
        "get_group_msg_history",
        group_id=event.group_id,
        message_seq=event.reply.message_id,
        count=nums.result,
    )
    
    messages = r.get("messages", [])
    quote_messages = []
    for message in messages:
        profile = await bot.get_group_member_info(
            group_id=event.group_id, user_id=message["user_id"]
        )

        rank_type = RankType.NORMAL
        if profile["role"] == "owner":
            rank_type = RankType.HEAD
        elif profile["role"] == "admin":
            rank_type = RankType.ADMIN
        else:
            rank_type = RankType.NORMAL

        header = profile["title"]
        if rank_type == RankType.NORMAL and header:
            rank_type = RankType.SPECIAL

        if not header:
            if profile["role"] == "owner":
                header = "群主"
            elif profile["role"] == "admin":
                header = "管理员"
            else:
                header = "成员"

        quote_message = QuoteMessage(
            nickname=profile["card"] if profile["card"] else profile["nickname"],
            rank=f"LV{profile['level']}",
            header=header,
            profile=f"http://q.qlogo.cn/headimg_dl?spec=640&dst_uin={message['user_id']}",
            message=Message([
                MessageSegment(msg["type"], msg["data"]) for msg in message["message"]
            ]),
            rank_type=rank_type,
        )
        
        quote_messages.append(quote_message)

    quote_image = await rend_multiple_quotes(quote_messages)
    image_data = io.BytesIO()
    quote_image.save(image_data, format="PNG")
    image_data_bytes = image_data.getvalue()

    encoded_image = base64.b64encode(image_data_bytes).decode("utf-8")

    await quote.finish(Message(MessageSegment.image(f"base64://{encoded_image}")))
