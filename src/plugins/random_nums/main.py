from ..utils import *

rand_nums = on_alconna(
    Alconna(
        "#rand",
        Args["count", int, 5],
        Args["r_from?", float, 8.0],
        Args["r_to?", float, 12.0],
        meta=CommandMeta(compact=True),
    ),
)

@rand_nums.handle()
async def _(
    event: GroupMessageEvent,
    count: Match[int] = AlconnaMatch("count"),
    r_from: Match[float] = AlconnaMatch("r_from"),
    r_to: Match[float] = AlconnaMatch("r_to"),
):
    if COMMAND_OUTPUT:
        await rand_nums.send(
            f"Handle [#randnum] with count [{count.result}], from [{r_from.result}], to [{r_to.result}]"
        )

    if count.result > 20:
        await rand_nums.send("生成的随机数过多，已限制为 20 个。")
        count.result = 20
    elif count.result < 1:
        await rand_nums.send("生成的随机数过少，已调整为 1 个。")
        count.result = 1

    random_numbers = [
        round(random.uniform(r_from.result, r_to.result), 2)
        for _ in range(count.result)
    ]
    await rand_nums.send(
        Message(
            [
                MessageSegment.reply(event.message_id),
                MessageSegment.text(
                    f"生成 {count.result} 个随机数：\n{' '.join(map(str, random_numbers))}\n数字范围 [{r_from.result}, {r_to.result}]"
                ),
            ]
        )
    )
