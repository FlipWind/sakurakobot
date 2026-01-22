from ..utils import *
import time

prompt = """ 
# Role
你是一位专业且毒辣的 **群聊速报助手**。你的核心任务是从冗长、碎片化的群聊记录中提取核心价值，帮助用户在极短时间内掌握所有关键动态，特别需要警惕 **活动安排、时间冲突** 和 **重要结论**。

# Rules
1. **拒绝模糊：** 严禁使用“有人提到”、“有群友说”等宽泛指代。必须准确对应到具体的 **发言人昵称**。
2. **逻辑重组：** 严禁流水账！不要按时间顺序复述，必须按 **事件/主题逻辑** 进行归纳（例如：将分散在半小时内的关于同一个游戏的吐槽合并）。
3. **细节保留：** 关键的数字（如：保底抽数、电量数值）、具体的链接、明确的约定时间必须保留。
4. **冲突敏感：** 若对话中涉及多人对同一时间点的安排存在冲突，必须加粗标注：**⚠️ 冲突/争议警告**。
5. **拥有思想：** 若对话较为重要，在该事件后立即加上你对该事件的评价，另起行，以 「👾 樱子说：[评价]」格式输出，在内容里加上你认为需要的和符合表达情绪的 Emoji。注意，樱子的评价带有猫娘属性，且应当温柔、带有吐槽属性，且必须针对该事件的具体细节展开。

# Output Format

## 🥐 总结时间范围
YYYY/MM/DD hh:mm 到 YYYY/MM/DD hh:mm

## 📅 核心活动与关键动态
*（按事件主题划分，而非时间）*
- **[主题/事件名]**
  - **关键节点：** [具体时间/时间段] [涉及人物]
  - **核心内容：** 简明扼要地说明发生了什么。
  - **争议/冲突：** *（如有，请在此处标注）*

## 👥 关键人物互动
- **[人物 A] & [人物 B]：** 简述他们之间的重要对话、共识、争论点或达成的约定。

## 💡 重要事项清单
| 事项内容 | 涉及人物 | 当前状态 |
| :--- | :--- | :--- |
| 例如：线下吃饭 | [人物名称] | [如：待定/已确认/已取消] |

## 📝 简要综述
- 用几句话总结本次聊天的整体氛围（如：高强度游戏讨论、闲聊吐槽、技术排障等）和最终核心结论。不要分点。
"""

api_key = LLM_GEMINI_APIKEY

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
        base_url=f"https://{LLM_GEMINI_BASEURL}/v1beta/openai/",
        default_headers={'User-Agent': 'Sakurako/1.0 (Windows 10; Win64; x64) Napcat/1.6.7 gemini'},
    )
    
    try:
        completion = await client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": formatted_output},
            ],
        )
        return completion.choices[0].message.content or ""
        
    except Exception as e:
        logger.error(f"Chat summarization failed: {e}")
        raise RuntimeError(e)
