from ..utils import *
from telethon import TelegramClient, events

TEMP_PATH = pathlib.Path(__file__).parent.parent.parent.parent / "temp"

class Repeater:
    def __init__(self):
        self.api_id = TELEGRAM_APPID
        self.api_hash = TELEGRAM_APIHASH
        self.phone = TELEGRAM_ACC_PHONE
        self.password = TELEGRAM_ACC_PASSWORD

        self.proxy = {
            "proxy_type": TELEGRAM_PROXY_TYPE,
            "addr": TELEGRAM_PROXY_ADDR,
            "port": TELEGRAM_PROXY_PORT,
        }
        
        self.repeat_groups = TELEGRAM_REPEATER_GROUPS
        self.forward_groups = TELEGRAM_FORWARD_GROUPS

    async def start(self):
        self.client = TelegramClient(
            "anon",
            self.api_id,
            self.api_hash,
            proxy=self.proxy,
            retry_delay=5,
            connection_retries=720,
            timeout=10,
            auto_reconnect=True,
        )

        try:
            await self.client.start(phone=self.phone, password=self.password) # type: ignore
            self.client.add_event_handler(
                self._message_handle,
                events.NewMessage(chats=self.repeat_groups)
            )
            logger.info("Telethon 客户端连接成功，正在监听消息...")
        except Exception as e:
            logger.error(f"Telethon 客户端连接失败: {e}")
            return

        await self.client.run_until_disconnected() # type: ignore
    
    async def stop(self):
        self._running = False
        if self.client and self.client.is_connected():
            self.client.disconnect()
            logger.info("Telethon 客户端已断开连接")
    
    async def _message_handle(self, event):
        try:
            chat_id = event.chat_id
            logger.success(f"接收到来自频道 {event.chat.title} 的消息 (chat_id: {chat_id})")
            
            message = [
                MessageSegment.text(f"转自频道「{event.chat.title}」:\n")
            ]
            
            if event.message.message:
                message.append(MessageSegment.text(event.message.message))
                checker = event.message.message.lower()
                
                if any(word in checker for word in ["中出", "r18", "nsfw", "18", "后入", "足交"]):
                    logger.error(f"消息疑似包含 NSFW 内容，跳过转发 (chat_id: {chat_id})")
                    return
            if event.message.media:
                file_path = f"{TEMP_PATH}/{chat_id}_{event.message.id}.png"
                await self.client.download_media(event.message.media, file=file_path)
                
                message.append(MessageSegment.image(f"file://{file_path}"))
            
            await self.forward_message(message)
                
            
            
        except Exception as e:
            logger.error(f"处理频道消息时出错 (chat_id: {chat_id}): {e}")
    
    async def forward_message(self, message):
        bot = nonebot.get_bot()
        if not bot:
            logger.error("没有可用的 Bot 实例。")
            return
        for group in self.forward_groups:
            try:
                await bot.send_group_msg(group_id=group, message=message)
            except Exception as e:
                logger.error(f"转发消息到群组 {group} 失败: {e}")
            


telegram_monitor = Repeater()
driver = get_driver()

@driver.on_startup
async def start_telegram_monitor():
    if not TELEGRAM_REPEATER_ENABLE:
        logger.info("Telegram 监控未启用，跳过启动")
        return
    try:
        asyncio.create_task(telegram_monitor.start())
        logger.info("Telegram 监控任务已创建")
    except Exception as e:
        logger.error(f"启动 Telegram 监控失败: {e}")

@driver.on_shutdown
async def stop_telegram_monitor():
    if not TELEGRAM_REPEATER_ENABLE:
        return
    
    await telegram_monitor.stop()