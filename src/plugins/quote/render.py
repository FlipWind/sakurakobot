from ..utils import *

class RankType(Enum):
    NORMAL = "normal", (65, 65, 65), (181, 182, 181)
    SPECIAL = "special", (66, 40, 90), (222, 121, 230)
    ADMIN = "admin", (4, 50, 47), (24, 172, 156)
    HEAD = "head", (52, 37, 6), (227, 140, 18)

class QuoteMessage:
    def __init__(self, nickname: str, rank: str, header: str, profile: str, message: Message, rank_type: RankType):
        self.nickname = nickname
        self.rank = rank
        self.header = header

        self.profile = profile
        self.message = message
        self.rank_bac = rank_type.value[1]
        self.rank_text = rank_type.value[2]
    
    def __str__(self):
        return f"QuoteMessage(nickname={self.nickname}, rank={self.rank}, header={self.header}, profile={self.profile}, message={self.message})"

async def rend_quote(quote_message: QuoteMessage) -> Image.Image:
    temp_img = Image.new("RGB", (1, 1))
    
    # Font
    def _font(name: str, size: int):
        return ImageFont.truetype(f"{ASSETS_PATH}/fonts/{name}.ttf", size)
    
    # Message
    async def _draw_texts(texts: str) -> tuple[Image.Image, bool]:
        font = _font("MiSans-Medium", 40)
        if texts == "":
            texts = " "
        
        lines = []
        cur_line = ""
        _length = 631
        
        with Pilmoji(temp_img) as cal_pilmoji:
            for chars in texts:
                if chars == "\n":
                    lines.append(cur_line)
                    cur_line = ""
                    continue
                test_line = cur_line + chars
                text_width = cal_pilmoji.getsize(test_line, font=font, emoji_scale_factor=0.9)[0]
                
                if text_width <= 631:
                    cur_line = test_line
                else:
                    lines.append(cur_line)
                    cur_line = "" + chars
            if cur_line:
                lines.append(cur_line)
            
            if len(lines) == 1:
                _length = cal_pilmoji.getsize(lines[0], font=font, emoji_scale_factor=0.9)[0]
        
        # Draw each line
        line_height = 48
        
        text_image = Image.new("RGBA", (_length, len(lines) * line_height + 8), (255, 255, 255, 0))
        for i, line in enumerate(lines):
            with Pilmoji(text_image) as pilmoji:
                pilmoji.text((0, i * line_height), line, fill=(255, 255, 255), font=font, emoji_scale_factor=0.9, emoji_position_offset=(0, 8))

        return text_image, True if len(lines) == 1 else False
    
    # Calculate image size
    title = f"{quote_message.rank} {quote_message.header}"
    text_image, is_single_line = await _draw_texts(quote_message.message.extract_plain_text())
    
    height, width = 0, 900
    if is_single_line:
        with Pilmoji(temp_img) as cal_pilmoji:
            title_width = cal_pilmoji.getsize(title, font=_font("MiSans-Semibold", 22), emoji_scale_factor=0.9)[0]
            name_width = cal_pilmoji.getsize(quote_message.nickname, font=_font("MiSans-Medium", 28), emoji_scale_factor=0.9)[0]
            title_edge = min(900, 158 + title_width + 16 + 12 + name_width + 36)
            
        with Pilmoji(temp_img) as cal_pilmoji:
            text_edge = 158 + text_image.width + 50 + 36

        width = min(900, max(title_edge, text_edge))
    
    height = 104 + text_image.height + 28 + 28 + 36
        
    image = Image.new("RGBA", (width, height), (16, 17, 19))
    
    # Draw Profile
    async with httpx.AsyncClient() as client:
        response = await client.get(quote_message.profile)
    profile_image = Image.open(BytesIO(response.content)).resize((100, 100))
    
    mask = Image.new("L", (100, 100), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, 100, 100), fill=255)
    
    profile_image.putalpha(mask)
    image.paste(profile_image, (40, 40), profile_image)
    
    # Draw rank and header
    draw = ImageDraw.Draw(image)
    font_size = 22
    
    temp_img = Image.new("RGB", (1, 1))
    with Pilmoji(temp_img) as temp_pilmoji:
        text_width = temp_pilmoji.getsize(title, font=_font("MiSans-Semibold", font_size), emoji_scale_factor=0.9)[0]
    
    rect_width, rect_height = int(text_width + 20), 36
    x, y = 157, 44
    
    draw.rounded_rectangle(
        [(x, y), (x + rect_width, y + rect_height)],
        radius=7,
        fill=quote_message.rank_bac
    )
    
    with Pilmoji(image) as pilmoji:
        pilmoji.text((x + 10, y + 4), title, fill=quote_message.rank_text, font=_font("MiSans-Semibold", font_size), emoji_scale_factor=0.9, emoji_position_offset=(0, 5))
    
    # Draw nickname
    nickname = quote_message.nickname
    font_size = 28
    with Pilmoji(image) as pilmoji:
        pilmoji.text((x + rect_width + 16, 44), nickname, fill=(255, 255, 255), font=_font("MiSans-Medium", font_size))
    
    # Draw message
    message_width = text_image.width
    print(f"Message width: {message_width}")
    message_height = text_image.height
    
    draw.rounded_rectangle(
        [(158, 104), (158 + message_width + 50, 104 + message_height + 56)],
        radius=26,
        fill=(37, 38, 40)
    )
    
    image.paste(text_image, (158 + 25, 104 + 28), text_image)
    
    return image