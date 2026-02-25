from ..utils import *
from ._request import *
from nonebot import on_regex
from nonebot.params import RegexGroup

# Calendar Today
bangumi_today = on_alconna(
    Alconna(
        "#今日放送",
        Args["day?", int, datetime.datetime.today().weekday() + 1],
        meta=CommandMeta(compact=True),
    ),
    aliases=("今天有啥番", "今日番剧", "#今日番剧", "#番剧日历"),
)


@bangumi_today.handle()
async def _(
    event: GroupMessageEvent,
    day: Match[int] = AlconnaMatch("day"),
):
    if COMMAND_OUTPUT:
        await bangumi_today.send(f"Handle [#今日放送] with day [{day.result}]")

    weekday = day.result - 1

    res = await get_calendar(weekday)
    append_list: List[Message] = [
        Message(
            f"已知 星期{'一二三四五六日'[weekday]}({'月火水木金土日'[day.result]}) 放送的番剧如下喵！"
        )
    ]

    for item in res.items:
        _item = Message(
            f"ID #{item.id}\n"
            f"{item.name}{'(' + item.name_cn + ')' if item.name_cn else ""}\n"
            + MessageSegment.image(item.image_url if item.image_url else "https://lain.bgm.tv/img/no_icon_subject.png")
            + "\n"
            f"⏰ 开播: {item.air_date}\n"
            f"⭐ 评分: {item.score}\n📈 排名: {item.rank}\n"
            f"\n🔗 {item.url}"
        )
        append_list.append(_item)

    await send_node_messages_list(event, append_list)


# Search Bangumi
bangumi_search = on_alconna(
    Alconna(
        "#搜索番剧",
        Args["keyword", str],
        meta=CommandMeta(compact=True),
    ),
    aliases=("#查番", "#番剧", "搜番"),
)

bangumi_search_alt = on_regex(r"^(?P<keyword>.+)是什么番$")


@bangumi_search_alt.handle()
async def _(
    event: GroupMessageEvent,
    keyword: tuple = RegexGroup(),
):
    await bangumi_search_internal(event, keyword=keyword[0] if keyword else "")


@bangumi_search.handle()
async def _(
    event: GroupMessageEvent,
    keyword: Match[str] = AlconnaMatch("keyword"),
):
    await bangumi_search_internal(event, keyword=keyword.result)


async def bangumi_search_internal(
    event: GroupMessageEvent,
    keyword: str,
):
    if COMMAND_OUTPUT:
        await bangumi_search.send(f"Handle [#搜索番剧] with keyword [{keyword}]")

    if len(keyword) == 0:
        await bangumi_search.finish("貌似你什么也没输入喵……")

    res = await search_bangumi(keyword)
    append_list: List[Message] = [
        Message(f"搜索 [{keyword}]，您要找的是哪个喵？(仅显示前6个结果)"),
    ]

    for item in res[:6]:
        _item = Message(
            f"ID #{item.id}\n"
            f"{item.name}{'(' + item.name_cn + ')' if item.name_cn else ""}\n"
            + MessageSegment.image(item.image_url if item.image_url else "https://lain.bgm.tv/img/no_icon_subject.png")
            + "\n"
            f"在 {item.date} 于 {item.platform} 首播，共 {item.eps} 集\n"
            f"⭐ 评分: {item.score}\n📈 排名: {item.rank}\n"
            f"📌 标签: {' '.join(item.tags[:5])}\n"
            + f"\n🔗 https://bgm.tv/subject/{item.id}"
        )
        append_list.append(_item)

    await send_node_messages_list(event, append_list)


# Search Character

character_search = on_alconna(
    Alconna(
        "#搜索角色",
        Args["keyword", str],
        meta=CommandMeta(compact=True),
    ),
    aliases=("#查角色", "#角色", "搜角色"),
)

character_search_alt = on_regex(r"^(?P<keyword>.+)是什么角色$")

@character_search.handle()
async def _(
    event: GroupMessageEvent,
    keyword: Match[str] = AlconnaMatch("keyword"),
):
    await character_search_internal(event, keyword=keyword.result)

@character_search_alt.handle()
async def _(
    event: GroupMessageEvent,
    keyword: tuple = RegexGroup(),
):
    await character_search_internal(event, keyword=keyword[0] if keyword else "")

async def character_search_internal(
    event: GroupMessageEvent,
    keyword: str,
):
    if COMMAND_OUTPUT:
        await character_search.send(f"Handle [#搜索角色] with keyword [{keyword}]")

    if len(keyword) == 0:
        await character_search.finish("貌似你什么也没输入喵……")

    res = await search_character(keyword)
    append_list: List[Message] = [
        Message(f"搜索 [{keyword}]，您要找的是哪个角色喵？(仅显示前6个结果)"),
    ]

    for item in res[:6]:
        _related_subjects = "\n".join(f"「{obj.staff}」担当于 ID#{obj.id} {obj.name}{'(' + obj.name_cn + ')' if obj.name_cn else ""}" for obj in item.related_subjects[:5])
        _item = Message(
            f"ID #{item.id}\n"
            f"{item.name}{'(' + item.gender + ')' if item.gender else ""}\n"
            + MessageSegment.image(item.image_url if item.image_url else "https://lain.bgm.tv/img/no_icon_subject.png")
            + MessageSegment.text(f"\n> 简介: \n{item.summary}\n\n" if item.summary else "\n\n")
            + f"🔮 相关作品: \n{_related_subjects}\n"
            f"\n🔗 https://bgm.tv/character/{item.id}"
        )
        append_list.append(_item)

    await send_node_messages_list(event, append_list)
