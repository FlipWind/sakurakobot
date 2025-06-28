from ..utils import *
from ._request import *

bangumi_search = on_alconna(
    Alconna("#bangumi", Args["keyword", MultiVar(str)], Option("-n", Args["num?", int], default=10))
)

@bangumi_search.handle()
async def _(
    event: GroupMessageEvent,
    keyword: Match[str] = AlconnaMatch("keyword"),
    num: Match[int] = AlconnaMatch("num"),
):
    keywords = " ".join(list(keyword.result))
    nums = num.result
    if(COMMAND_OUTPUT):
        await bangumi_search.send(f"Handle [#bangumi] with keywords [{keywords}] and nums [{nums}]")
    
    if nums > 20:
        nums = 20
        await bangumi_search.send(f"搜索数量过多，已自动限制为 20 条喵")
    
    res = await get_bangumi(keys=keywords, nums=nums)
    append_list: List[Any] = [f"搜索了 [{keywords}] 的 {nums} 条结果喵~"]
    for i in range(len(res)):
        append_list.append(f"[{i+1}]. {res[i].type} - {res[i].title}\n大小 {round(res[i].size/1024, 2)} MB")
        append_list.append(f"{res[i].magnet}")

    try:
        await bangumi_search.finish(ListToNode(append_list))
    except ActionFailed as e:
        logger.error(f"Error in sending message: {e}")
        logger.error(append_list)
        await bangumi_search.send("发送转发消息失败，推测是可能该消息内含有屏蔽词喵~\n改为直接发送喵。")
        
        await bangumi_search.finish(Message("\n".join(append_list)))
