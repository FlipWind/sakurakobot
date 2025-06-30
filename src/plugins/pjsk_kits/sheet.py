from ..utils import *

zh_db_link = PJSK_ZHDBLINK
ja_db_link = PJSK_JADBLINK
diffi_cndb_link = PJSK_DIFFI_CNLINK
diffi_jpdb_link = PJSK_DIFFI_JPLINK

sheet_query = on_alconna(
    Alconna(
        "#pjsheet",
        Args["title", MultiVar(str)],
        Option("-d", Args["diffi", str, "master"]),
    ),
)


def reverse_dict(data):
    """将字典键值对反转，值相同的键合并为列表"""
    reversed_data = {}
    for k, v in data.items():
        reversed_data.setdefault(v, []).append(k)
    return reversed_data


@sheet_query.handle()
async def _(
    event: GroupMessageEvent | MessageEvent,
    bot: Bot,
    title: Match[str] = AlconnaMatch("title"),
    diffi: Match[str] = AlconnaMatch("diffi"),
):
    if COMMAND_OUTPUT:
        await sheet_query.send(
            f"Handle [#pjsheet] with keywords [{title.result}] and difficulty [{diffi.result}]"
        )

    if title.available == False:
        await sheet_query.finish("用来获取歌曲铺面~\n\n请使用 #pjsheet <歌曲名称> 或 #pjsheet <歌曲名称> -d <难度> 来获取歌曲铺面~\n")

    async with httpx.AsyncClient() as client:
        try:
            response_diffi_cn = await client.get(
                diffi_cndb_link, timeout=100, follow_redirects=True
            )
            response_diffi_jp = await client.get(
                diffi_cndb_link, timeout=100, follow_redirects=True
            )
        except httpx.ConnectTimeout:
            await sheet_query.finish("连接超时，请稍后再试。")

    async with httpx.AsyncClient() as client:
        try:
            response_zh = await client.get(
                zh_db_link, timeout=100, follow_redirects=True
            )
            response_ja = await client.get(
                ja_db_link, timeout=100, follow_redirects=True
            )
        except httpx.ConnectTimeout:
            await sheet_query.finish("连接超时，请稍后再试。")

    if (
        response_zh.status_code == 200
        and response_ja.status_code == 200
        and response_diffi_cn.status_code == 200
        and response_diffi_jp.status_code == 200
    ):
        data_zh = response_zh.json()
        data_ja = response_ja.json()
        data_diffi_zh = response_diffi_cn.json()
        data_diffi_jp = response_diffi_jp.json()

        reversed_zh = reverse_dict(data_zh)
        reversed_ja = reverse_dict(data_ja)

        merged = {}
        for d in [reversed_zh, reversed_ja]:
            for name, ids in d.items():
                merged[name] = ids[0]

        best_match_item = max(
            merged.items(), key=lambda item: fuzz.ratio(title.result, item[0])
        )

        best_match_name, best_match_id = best_match_item
        # print(merged)
        highest_score = fuzz.ratio(title.result, best_match_name)

        def check_music_exists(json_data, target_music_id, target_difficulty):
            for item in json_data:
                if (
                    item.get("musicId") == target_music_id
                    and item.get("musicDifficulty") == target_difficulty
                ):
                    return True
            return False

        if not check_music_exists(data_diffi_zh, int(best_match_id), diffi.result) and check_music_exists(data_diffi_jp, int(best_match_id), diffi.result):
            await sheet_query.finish(
                f"*检测输入名称：{title.result}\n歌曲名称：{best_match_name}\n难度：{diffi.result}\n匹配度：{highest_score}/100\n\
\n该歌曲在该难度下不存在，请检查拼写或选择其他难度。"
            )

        try:
            await sheet_query.finish(
                Message(
                    [
                        MessageSegment.text(
                            f"*检测输入名称：{title.result}\n歌曲名称：{best_match_name}\n难度：{diffi.result}\n匹配度：{highest_score}/100\n"
                        ),
                        MessageSegment.image(
                            f"https://storage.sekai.best/sekai-music-charts/jp/{int(best_match_id):04d}/{diffi.result}.png"
                        ),
                    ]
                )
            )
        except ActionFailed as E:
            logger.error(
                f"https://storage.sekai.best/sekai-music-charts/jp/{int(best_match_id):04d}/{diffi.result}.png"
            )
            logger.error(E)
            await sheet_query.finish(
                Message(
                    [
                        MessageSegment.text(
                            f"铺面获取失败，错误：{str(E)}\n请稍后再试。"
                        ),
                    ]
                )
            )
    else:
        print(
            f"请求失败，状态码：{response_zh.status_code} & {response_ja.status_code}"
        )
        await sheet_query.finish("获取数据失败，请稍后再试。")
