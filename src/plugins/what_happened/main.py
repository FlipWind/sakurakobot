from ..utils import *
from . import chatapi as chatapi

whathappened = on_alconna(
    Alconna("发生了啥", Args["count?", int, 500], meta=CommandMeta(compact=True)),
    aliases=("#发生了啥", "#总结一下"),
)


@whathappened.handle()
async def _(
    event: GroupMessageEvent, bot: Bot, count: Match[int] = AlconnaMatch("count")
):
    if COMMAND_OUTPUT:
        await whathappened.send(f"Handle [#发生了啥] with count [{count.result}]")

    if count.result > 1500:
        await whathappened.send("消息过多，已限制为 1500 条消息。")
        count.result = 1500
    if count.result < 100:
        await whathappened.send("消息过少，已调整为 100 条消息。")
        count.result = 100

    # Ensure the group state exists in sakurako_state
    group_key = f"group_{event.group_id}"
    if group_key not in sakurako_state:
        sakurako_state[group_key] = {}
    
    if sakurako_state[group_key].get("whathappened") == "processing":
        await whathappened.finish(
            "盯——\n本喵发现本群已经有了一个总结进程，请等待该请求完成后再进行下一次请求喵。"
        )

    sakurako_state[group_key]["whathappened"] = "processing"

    p = await bot.call_api(
            "get_group_msg_history", group_id=event.group_id, count=count.result
        )

    await whathappened.send(
            f"知道你超急的喵。咱喵已经帮你抓到了最近 {count.result} 条消息喽，主人就乖乖在这里等本喵一下下啦，不要跑丢呜～"
        )

    content = await chatapi.summarize_chat(p)
    messages = [f"下面是最近 {count.result} 条的总结喵。", content, "使用 Qwen3-turbo 总结。"]
    
    await send_node_messages(event, messages)
    sakurako_state[group_key]["whathappened"] = "done"
