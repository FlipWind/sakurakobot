from ..utils import *
from ._request import *

bangumi_search = on_alconna(
    Alconna(
        "#bangumi",
        Args["keyword", MultiVar(str)],
        Option("-n", Args["num?", int], default=20),
    )
)


@bangumi_search.handle()
async def _(
    event: GroupMessageEvent,
    keyword: Match[str] = AlconnaMatch("keyword"),
    num: Match[int] = AlconnaMatch("num"),
):
    keywords = list(keyword.result)
    nums = num.result
    if COMMAND_OUTPUT:
        await bangumi_search.send(
            f"Handle [#bangumi] with keywords [{keywords}] and nums [{nums}]"
        )

    if nums > 40:
        nums = 40
        await bangumi_search.send(f"搜索数量过多，已自动限制为 40 条喵")
    
    # 重试机制
    for i in range(3):
        res = await get_bangumi(keys=keywords, nums=nums)
        if len(res) > 0:
            break
        if i == 2:
            await bangumi_search.send(f"搜索失败，请稍后再试喵~")
            return
        time.sleep(3)

    append_list: List[Any] = [f"搜索了 [{keywords}] 的 {nums} 条结果喵~"]
    for i in range(len(res)):
        append_list.append(
            f"[{i+1}]. {res[i].type} - {res[i].title}\n大小 {round(res[i].size/1024, 2)} MB"
        )
        append_list.append(f"{res[i].magnet}")

    await send_node_messages(event, append_list)
