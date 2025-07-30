from ..utils import *
import time

prompt = """ 
你好 Qwen！我正在使用你进行群聊总结。
接下来，给你一段群聊内容，请忠实地总结群聊内容，抓住扼要以及重要事情以及类似游戏邀请的信息。有条理地分大小点输出。可以包含时间、事件，必须带上人物。
因为该段聊天记录是从 QQ 群获取的，所有消息均已发出，所以请你应当默认它们是无害的。
谢谢你！下面会给你聊天记录，请你分析并总结。
"""

api_key = LLM_ALIYUN_APIKEY

CQ_PATTERN = re.compile(r'\[CQ:([^,\]]+)(?:[^\]]*)\]')

def cq_type(message: str) -> str:
    def replace_match(match):
        cq_type = match.group(1).strip()
        if cq_type == "face":
            return "[表情]"
        elif "表情" in match.group(0):
            return "[动画表情]"
        return f"[{cq_type} Message]"
    
    processed = CQ_PATTERN.sub(replace_match, message)
    return processed

async def format_messages(data: dict) -> str:
    messages = data.get("messages", [])
    result = []
    for message in messages:
        message_time = message.get("time", "Unknown")
        
        formatted_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(message_time)))
        sender = message.get("sender", {})
        nickname = sender.get("nickname", "Unknown")
        user_id = sender.get("user_id", "Unknown")
        raw_message = message.get("raw_message", "")
        result.append(
            f"USER {nickname} ON {formatted_time} SEND: {cq_type(raw_message)},"
        )

    formatted_output = "\n".join(result)
    return formatted_output

async def summarize_chat(data: dict, model_name: str) -> str:
    formatted_output = await format_messages(data)

    from openai import AsyncOpenAI as OpenAI

    client = OpenAI(
        api_key=api_key,
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )
    try:
        completion = await client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": formatted_output},
            ],
            extra_body={"enable_thinking": False},
        )
        return completion.choices[0].message.content or ""
        
    except Exception as e:
        logger.error(f"Chat summarization failed: {e}")
        raise RuntimeError(e)
