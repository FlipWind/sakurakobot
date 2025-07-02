from ..utils import *

from .sticker.draw.help_content import gen_helpcontent, gen_char_helpcontent
from .sticker.draw.sticker_main import simple_sticker

sticker = on_alconna(
    Alconna(
        "#pjsk",
        Args["name?", str],
        Args["id?", int],
        Args["words?", MultiVar(str)],
    ),
)

# 创建字典
pj_count = {
    "airi": 15,
    "akito": 13,
    "an": 13,
    "emu": 13,
    "ena": 16,
    "haruka": 13,
    "honami": 15,
    "ichika": 15,
    "kaito": 13,
    "kanade": 14,
    "kohane": 14,
    "len": 14,
    "luka": 13,
    "mafuyu": 14,
    "meiko": 13,
    "miku": 13,
    "minori": 14,
    "mizuki": 14,
    "nene": 13,
    "rin": 13,
    "rui": 16,
    "saki": 15,
    "shiho": 15,
    "shizuku": 13,
    "touya": 15,
    "tsukasa": 15,
}


@sticker.handle()
async def _(
    event: GroupMessageEvent | MessageEvent,
    bot: Bot,
    name: Match[str] = AlconnaMatch("name"),
    id: Match[int] = AlconnaMatch("id"),
    words: Match[str] = AlconnaMatch("words"),
):
    # logger.error(f"Current working directory:{os.getcwd()}")
    # one type of possible command: #pjsk <name> <id> <words>
    #                               0       1     2      3

    if COMMAND_OUTPUT:
        await sticker.send(
            f"Handle [#pjsk] with char [{name.result}], id [{id.result}], words [{words.result}]"
        )

    if not name.available:
        help_im = gen_helpcontent()
        image_data = io.BytesIO()
        help_im.save(image_data, format="PNG")
        image_data_bytes = image_data.getvalue()

        encoded_image = base64.b64encode(image_data_bytes).decode("utf-8")
        await sticker.finish(
            Message(
                [
                    MessageSegment.text(
                        "用来创建角色贴纸~\n\n可选择的角色如下~\n使用 #pjsk <name> <id> <words> 来制作贴纸喵~\n你可以继续使用 #pjsk <name> 查看该角色的所有贴纸~"
                    ),
                    MessageSegment.image(f"base64://{encoded_image}"),
                ]
            )
        )

    elif name.available and not id.available:
        if name.result not in pj_count:
            await sticker.finish("名字好像错了，请检查一下喵~")

        help_im = gen_char_helpcontent(name.result)
        image_data = io.BytesIO()
        help_im.save(image_data, format="PNG")
        image_data_bytes = image_data.getvalue()

        encoded_image = base64.b64encode(image_data_bytes).decode("utf-8")
        await sticker.finish(
            Message(
                [
                    MessageSegment.text(
                        "选择角色的贴纸表如下喵！\n使用 #pjsk <name> <id> <words> 来制作贴纸喵~"
                    ),
                    MessageSegment.image(f"base64://{encoded_image}"),
                ]
            )
        )

    elif name.available and id.available and words.available:
        name.result = name.result.lower()

        if name.result not in pj_count:
            await sticker.finish("名字好像错了，请检查一下喵~")
        if not 1 <= int(id.result) <= pj_count[name.result]:
            await sticker.finish("我的图片库里好像没有这张 ID 的图，主人再试试喵？")

        wordcontent = " ".join(list(words.result))

        logger.error(f"Wordcontent final: {wordcontent}")

        sticker_im = simple_sticker(name.result, id.result, wordcontent)
        image_data = io.BytesIO()
        sticker_im.save(image_data, format="PNG")
        image_data_bytes = image_data.getvalue()

        encoded_image = base64.b64encode(image_data_bytes).decode("utf-8")

        await sticker.send(MessageSegment.image(f"base64://{encoded_image}"))
        # todo: image process
        pass

    else:
        await sticker.finish(
            "参数错误，请以 #pjsk <name> <id> <words..> 的格式发送喵~(多行文本暂不支持以\\n分割)"
        )
