from ..utils import *

ban = on_alconna(
    Alconna(
        "#ban", Args["user", At], Args["time?", int, 0], meta=CommandMeta(compact=True)
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
    if COMMAND_OUTPUT:
        await ban.send(
            f"Handle [#ban] with target user [{user.result.target}], time [{time.result}]s"
        )

    if not user.available:
        await ban.finish("请指定要封禁的用户喵~")

    time.result = max(time.result, 0)

    if not get_user_is_admin(event):
        await ban.finish("倒反天罡喵~ 你暂时没有权限喵。")

    await bot.set_group_ban(
        group_id=event.group_id,
        user_id=int(user.result.target),
        duration=int(time.result),
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
    ]

    if banned_type == "ban":
        message = random.choice(hint_message_ban)
        await ban_repeat.finish(message)

    elif banned_type == "lift_ban":
        message = random.choice(hint_message_unban)
        await ban_repeat.finish(message)
