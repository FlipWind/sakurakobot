from ....utils import *
from PIL import ImageFont

font_path = f"{ASSETS_PATH}/fonts/YurukaFangTang.ttf"
def st_font(size: int):
    return ImageFont.truetype(font_path, size)