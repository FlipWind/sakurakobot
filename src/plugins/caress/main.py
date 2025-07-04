from ..utils import *

caress_matcher = on_alconna(
    Alconna(
        "&", Args["action", str], Args["target?", At], Args["operate?", str], meta=CommandMeta(compact=True)
    )
)

@caress_matcher.handle()
async def handle_caress(
    bot: Bot,
    event: GroupMessageEvent,
    action: Match[str] = AlconnaMatch("action"),
    target: Match[At] = AlconnaMatch("target"),
    operate: Match[str] = AlconnaMatch("operate")
):
    _action = action.result
    _operater = event.sender.nickname
    if target.available:
        _target = await bot.get_group_member_info(
            group_id=event.group_id, user_id=int(target.result.target)
        )
        _target = _target["nickname"]
    else:
        _target = "自己"

    if event.reply:
        _target = event.reply.sender.nickname

    if operate.available:
        await caress_matcher.finish(f"{_operater} {_action} {_target} {operate.result}！")
    else:
        await caress_matcher.finish(f"{_operater} {_action}了 {_target} 喵！")
