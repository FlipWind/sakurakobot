from ..utils import *
import uuid
import httpx

random_remark = on_alconna(
    Alconna(
        "#随机语录",
    ),
    aliases=("#典", "#语录", "#爆典", "#随机怪话", "#怪话")
)

@random_remark.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    group_data_path = DATA_PATH / "random_record" / str(event.group_id)
    if not group_data_path.exists():
        logger.success(f"PATH {group_data_path} not exist. Creating...")
        group_data_path.mkdir(parents=True, exist_ok=True)
    
    files = list(group_data_path.glob("*.*"))
    logger.success(f"Found {len(files)} files in {group_data_path}")
    for file in files:
        logger.success(f"File: {file.name}")
    
    if len(files) == 0:
        await random_remark.finish("本群还没有收录任何语录喵。")
    random_file = random.choice(files)
    await random_remark.finish(MessageSegment.image(random_file))
        
collect_remark = on_alconna(
    Alconna(
        "#收录",
        Args["image?", Image],
        meta=CommandMeta(compact=True)
    ),
    aliases=("#爆","#加入怪话", "#收集")
)

@collect_remark.handle()
async def _(bot: Bot, event: GroupMessageEvent, target: Match[Image] = AlconnaMatch("image")):
    group_data_path = DATA_PATH / "random_record" / str(event.group_id)
    if not group_data_path.exists():
        logger.success(f"PATH {group_data_path} not exist. Creating...")
        group_data_path.mkdir(parents=True, exist_ok=True)
    
    if not target.available and not event.reply:
        await collect_remark.finish("在消息内发送图片或引用一条图片谢谢喵。")
    
    if event.reply:
        message = event.reply.message
        for message in message:
            if message.type == "image":
                url = message.data["url"]
                logger.success(f"Downloading image from {url}")
                async with httpx.AsyncClient() as client:
                    response = await client.get(url)
                    if response.status_code == 200:
                        filename = f"{uuid.uuid4()}.png"
                        file_path = group_data_path / filename
                        with open(file_path, "wb") as f:
                            f.write(response.content)
                        await collect_remark.finish("已收录喵。")
                    else:
                        await collect_remark.finish("无法下载图片喵。")
    else:
        try:
            target.result.save(group_data_path)
            await collect_remark.finish("已收录喵。")
        except:
            await collect_remark.finish("无法下载图片喵。")
    
