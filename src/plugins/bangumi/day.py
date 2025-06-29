from ..utils import *
from ._request import *

bangumi_today = on_alconna(
    Alconna(
        "#bangumiday",
        Args["day?", int, datetime.datetime.today().weekday() + 1],
        meta=CommandMeta(compact=True),
    )
)


@bangumi_today.handle()
async def _(
    event: GroupMessageEvent,
    day: Match[int] = AlconnaMatch("day"),
):
    if COMMAND_OUTPUT:
        await bangumi_today.send(f"Handle [#bangumitoday] with day [{day.result}]")

    res = await get_day_bangumi(day.result)
    append_list: List[Any] = [
        f"已知 周{' 一二三四五六日'[day.result]} 番剧如下喵！"
    ] + res

    await send_node_messages(event, append_list)
