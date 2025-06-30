from PIL import ImageFont

font_path = "./assets/fonts/YurukaFangTang.ttf"
def st_font(size: int):
    return ImageFont.truetype(font_path, size)