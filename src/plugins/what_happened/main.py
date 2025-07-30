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

    all_models = [
        "qwen3-235b-a22b-instruct-2507",
        "qwen3-30b-a3b-instruct-2507",
        "qwen3-235b-a22b",
        "qwen3-30b-a3b",
        "qwen-plus-2025-07-14",
        "qwen-turbo-2025-07-15",
        "qwen-turbo-2025-04-28",
        "qwen-plus-2025-04-28",
        "qwen-plus",
        "qwen-turbo",
    ]

    modelerror = None
    for i, model in enumerate(all_models):
        current_model = model
        try:
            content = await chatapi.summarize_chat(p, model_name=model)
            break
        except RuntimeError as e:
            if i + 1 < len(all_models):
                await whathappened.send(
                    f"使用 {model} 模型总结失败，尝试调用 {all_models[i+1]} 模型喵……请稍等。"
                )
            else:
                await whathappened.send(f"使用 {model} 模型总结失败喵……")

            modelerror = e
            continue
    else:
        sakurako_state[group_key]["whathappened"] = "done"
        content = f"""呜呜，所有模型都总结失败了惹……
最常见的原因消息里可能含有不健康内容，你可以重新总结试试~
获取到错误如下：

```
{modelerror}
```

您可以重新使用「发生了啥」发起一个新的尝试以总结喵。"""

    messages = [
        f"下面是最近 {count.result} 条的总结喵。",
        content,
        f"使用 {current_model} 总结。",
    ]

    await send_node_messages(event, messages)
    sakurako_state[group_key]["whathappened"] = "done"


whathappened_debug = on_alconna(
    Alconna("#aidebug", Args["count?", int, 500], meta=CommandMeta(compact=True))
)

@whathappened_debug.handle()
async def _(
    event: GroupMessageEvent, bot: Bot, count: Match[int] = AlconnaMatch("count")
):
    if COMMAND_OUTPUT:
        await whathappened_debug.send(f"Handle [#aidebug] with count [{count.result}]")

    p = await bot.call_api(
        "get_group_msg_history", group_id=event.group_id, count=count.result
    )
    
    p = await chatapi.format_messages(p)

    with open(f"{TEMP_PATH}/temp.txt", "w", encoding="utf-8") as f:
        f.write(p)

    await bot.send_group_msg(
        group_id=event.group_id,
        message=Message(
            MessageSegment(
            type = "file", 
            data= {"file": f"file://{TEMP_PATH}/temp.txt", "name": "temp.txt"}
        ),
        )
    )