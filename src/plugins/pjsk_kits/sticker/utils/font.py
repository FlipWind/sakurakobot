from PIL import ImageFont
from .values import st_font

def cal_fontsize(words: str, max_width: int, max_height: int):
    font_size = 1
    while True:
        font = st_font(font_size)
        text_bbox = font.getbbox(max(words.split("\n"), key=len))
        text_width, text_height = (
            text_bbox[2] - text_bbox[0],
            text_bbox[3] - text_bbox[1],
        )

        if text_width > max_width or text_height > max_height:
            return font_size - 1
        font_size += 1


def cal_textsize(words: str, font_size: int) -> tuple[int, int]:
    font = st_font(font_size)
    text_bbox = font.getbbox(words)
    text_width, text_height = (
        text_bbox[2] - text_bbox[0],
        text_bbox[3] - text_bbox[1],
    )
    
    return int(text_width), int(text_height)
