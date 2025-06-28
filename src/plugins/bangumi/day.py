from ..utils import *
from ._request import *

bangumi_today = on_alconna(Alconna("#bangumiday", Args["day?", int, datetime.datetime.today().weekday() + 1]))


@bangumi_today.handle()
async def _(
    event: GroupMessageEvent,
    day: Match[int] = AlconnaMatch("day"),
):
    if COMMAND_OUTPUT:
        await bangumi_today.send(f"Handle [#bangumitoday] with day [{day.result}]")

    res = await get_day_bangumi(day.result)
    append_list: List[Any] = [f"已知 周{" 一二三四五六日"[day.result]} 番剧如下喵！"] + res

    try:
        await bangumi_today.finish(ListToNode(append_list))
    except ActionFailed as e:
        logger.error(f"Error in sending message: {e}")
        logger.error(append_list)
        await bangumi_today.send("发送转发消息失败，推测是可能该消息内含有屏蔽词喵~\n改为直接发送喵。")
        
        await bangumi_today.finish(Message("\n".join(append_list)))