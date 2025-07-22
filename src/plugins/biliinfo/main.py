from ..utils import *
from . import render as render

async def get_bvid(message: Message):
    jumpUrl = None
    bvid = None
    for msg in message:
        if msg.type == "json":
            data = msg.data
            try:
                tdata = json.loads(json.dumps(data))["data"]
                tdata = json.loads(tdata)
                jumpUrl = tdata["meta"]["news"]["jumpUrl"]
            except:
                try:
                    tdata = json.loads(json.dumps(data))["data"]
                    tdata = json.loads(tdata)
                    jumpUrl = tdata["meta"]["detail_1"]["qqdocurl"]
                except:
                    pass
    
    if jumpUrl and jumpUrl.startswith("https://b23.tv/"):
        logger.success(f"yes = {jumpUrl}")

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
            "Referer": "https://www.bilibili.com/",
        }

        # https://b23.tv/mkHk2iI
        async with httpx.AsyncClient(timeout=1000.0) as client:
            response = await client.get(jumpUrl, follow_redirects=True, headers=headers)
            # print(response)
            if response.status_code != 200:
                await biliinfo.finish("获取数据失败，请稍后再试。")
        # data = response.json()
        link = response.url
        path = urlparse(str(link)).path
        logger.success(f"link = {path}")
        
        bvid = path.split("/")[2]
    
    if bvid == None:
        text_content = message.extract_plain_text()
        bvid_match = re.search(r'BV1[A-Za-z0-9]{9}', text_content)
        bvid = bvid_match.group() if bvid_match else None
    
    return bvid

biliinfo = on_message(block=False)

@biliinfo.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    bvid = await get_bvid(event.get_message())
    
    if bvid:
        logger.success(f"Founded {bvid}")
        
        video_info = await render.get_video_info(bvid)
        
        help_im = await render.rend_image(video_info)
        image_data = io.BytesIO()
        help_im.save(image_data, format="PNG")
        image_data_bytes = image_data.getvalue()

        encoded_image = base64.b64encode(image_data_bytes).decode("utf-8")
        
        message_reply = Message(
            [
                MessageSegment.text("👀 成功获取视频信息：\n"),
                MessageSegment.text(f"✨ 标题：{video_info.title}\n"),
                MessageSegment.text(f"🤔 UP主：{video_info.owner.name}\n"),
                MessageSegment.text(f"🔗 链接：https://www.bilibili.com/video/{bvid}\n"),
                MessageSegment.image(f"base64://{encoded_image}"),
            ]
        )
        
        await biliinfo.finish(message_reply)

biliinfo_intro = on_alconna(
    Alconna("#简介")
)

@biliinfo_intro.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    if not event.reply:
        await biliinfo_intro.finish("未找到引用的消息喵。请试着引用一条 Bilibili 视频消息喵！")
    
    rep_message = event.reply.message
    bvid = await get_bvid(rep_message)
    if not bvid:
        await biliinfo_intro.finish("呜，咱好像处理不了这条消息……试试其他的吧？")
    
    video_info = await render.get_video_info(bvid)
    if not video_info:
        await biliinfo_intro.finish("暂时无法获取视频信息，等等再试惹。")
    
    await biliinfo_intro.finish(Message(
        [
            MessageSegment.reply(event.reply.message_id),
            MessageSegment.text(f"✨ 成功获取视频简介喵。\n\n{video_info.desc}")
        ]
    ))