from ..utils import *

ban = on_alconna(
    Alconna(
        "#ban", Args["user?", At], Args["time?", int, 0], meta=CommandMeta(compact=True)
    ),
    aliases=("#kill", "/kill"),
)


@ban.handle()
async def _(
    bot: Bot,
    event: GroupMessageEvent,
    user: Match[At] = AlconnaMatch("user"),
    time: Match[int] = AlconnaMatch("time"),
):
    banned_user = int(user.result.target) if user.available else None
    if event.reply:
        banned_user = event.reply.sender.user_id

    if COMMAND_OUTPUT:
        await ban.send(
            f"Handle [#ban] with target user [{banned_user}], time [{time.result}]s"
        )

    if banned_user == None:
        await ban.finish("请指定要封禁的用户喵~")

    time.result = max(time.result, 0)

    if not get_user_is_admin(event):
        await ban.finish("倒反天罡喵~ 你暂时没有权限喵。")

    await bot.set_group_ban(
        group_id=event.group_id,
        user_id=banned_user,
        duration=int(time.result),
    )


ban_self = on_alconna(
    Alconna("/kill @s", Args["time?", int, 60], meta=CommandMeta(compact=True))
)


@ban_self.handle()
async def _(
    bot: Bot, event: GroupMessageEvent, time: Match[int] = AlconnaMatch("time")
):
    if COMMAND_OUTPUT:
        await ban_self.send(f"Handle [/kill @s] with time [{time.result}]s")

    if get_user_is_admin(event):
        await ban_self.finish("额，请你自助。")

    time.result = time.result

    await bot.set_group_ban(
        group_id=event.group_id,
        user_id=event.user_id,
        duration=int(time.result),
    )


ban_all = on_alconna(
    Alconna("/kill @a", Args["time?", int, 60], meta=CommandMeta(compact=True))
)

@ban_all.handle()
async def _(
    bot: Bot, event: GroupMessageEvent, time: Match[int] = AlconnaMatch("time")
):
    if COMMAND_OUTPUT:
        await ban_all.send(f"Handle [/kill @a] with enabled [{'true' if time.result != 0 else 'false'}]")

    repeat_on_whole_banned = [
        "？干什么（感叹号）",
        "想干嘛！",
        "？"
    ]
    
    if not get_user_is_admin(event):
        await ban_all.finish(random.choice(repeat_on_whole_banned))
    
    await bot.set_group_whole_ban(
        group_id=event.group_id,
        enable=True if time.result != 0 else False,
    )


ban_repeat = on_notice()

@ban_repeat.handle()
async def _(bot: Bot, event: GroupBanNoticeEvent):
    user_id = event.user_id
    from_id = event.operator_id
    banned_type = event.sub_type
    duartion_time = event.duration

    hint_message_ban = [
        Message(
            [
                MessageSegment.at(user_id),
                MessageSegment.text(
                    f" 被打入大牢 {duartion_time} 秒喵~\n呐呐，我说杂鱼，只有🌟😡才会被禁言叭~\n嘻嘻 /v\\"
                ),
            ]
        ),
        Message(
            [
                MessageSegment.at(user_id),
                MessageSegment.text(" 似了喵。"),
            ]
        ),
        Message(
            [
                MessageSegment.at(user_id),
                MessageSegment.text("，你在吗？怎么不说句话喵？是不是不喜欢我喵？"),
            ]
        ),
        Message(
            [
                MessageSegment.at(user_id),
                MessageSegment.text("，你在哪喵？"),
            ]
        ),
        Message(
            [
                MessageSegment.at(user_id),
                MessageSegment.text(" 被口球塞起来惹♡"),
            ]
        ),
    ]

    hint_message_unban = [
        Message(
            [
                MessageSegment.at(user_id),
                MessageSegment.text(" 被 "),
                MessageSegment.at(from_id),
                MessageSegment.text(" 释放，还不赶紧给磕一个喵。"),
            ]
        ),
        Message(
            [
                MessageSegment.at(user_id),
                MessageSegment.text(" 终于被大赦了！"),
            ]
        ),
        Message(
            [
                MessageSegment.at(user_id),
                MessageSegment.text("，欢迎回来喵。"),
            ]
        ),
        Message(
            [
                MessageSegment.at(user_id),
                MessageSegment.text(" 终于重见光日了喵！"),
            ]
        ),
        Message(
            [
                MessageSegment.at(user_id),
                MessageSegment.text(" 被摘下了口球喵。"),
            ]
        ),
    ]

    if banned_type == "ban":
        if not user_id:
            await ban_repeat.finish("大家，果然都是杂鱼呢~")
        message = random.choice(hint_message_ban)
        await ban_repeat.finish(message)

    elif banned_type == "lift_ban":
        if not user_id:
            await ban_repeat.finish("大家好呀~ 欢迎回来！")
        message = random.choice(hint_message_unban)
        await ban_repeat.finish(message)
