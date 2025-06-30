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

pj_color = {
    "airi": (203, 134, 140, 255),
    "akito": (190, 126, 84, 255),
    "an": (65, 86, 157, 255),
    "emu": (194, 143, 169, 255),
    "ena": (87, 73, 82, 255),
    "haruka": (30, 92, 156, 255),
    "honami": (161, 126, 126, 255),
    "ichika": (51, 65, 91, 255),
    "kaito": (42, 61, 156, 255),
    "kanade": (172, 182, 191, 255),
    "kohane": (178, 170, 150, 255),
    "len": (204, 190, 108, 255),
    "luka": (203, 176, 191, 255),
    "mafuyu": (78, 54, 117, 255),
    "meiko": (129, 102, 64, 255),
    "miku": (101, 155, 152, 255),
    "minori": (169, 113, 97, 255),
    "mizuki": (202, 190, 186, 255),
    "nene": (154, 160, 150, 255),
    "rin": (203, 190, 105, 255),
    "rui": (166, 120, 193, 255),
    "saki": (204, 196, 164, 255),
    "shiho": (154, 152, 150, 255),
    "shizuku": (138, 165, 173, 255),
    "touya": (108, 123, 153, 255),
    "tsukasa": (203, 190, 147, 255),
}

from PIL import Image, ImageDraw, ImageFont

from ..utils.font import cal_fontsize, cal_textsize
from ..utils.values import st_font

def simple_sticker(name: str, id: int, words: str) -> Image.Image:
    image = Image.open(f"./assets/pjsk_sticker/{name}/{name}_{id}.png")
    stroke_width = 4
    # stroke_color = pj_color[name]
    # text_color = (255, 255, 255, 255)
    
    stroke_color = (255, 255, 255, 255)
    text_color = pj_color[name]
    rotate_angle = 10
    
    fontsize = cal_fontsize(words, image.width-20, image.height//4)
    text_size = cal_textsize(words, fontsize)
    font = st_font(fontsize)
    
    # text_pos = (image.width - text_size[0]) // 2,  (image.height - text_size[1]) // 2 - image.height // 3
    text_pos = 10, 0
    
    # text handle
    text_image = Image.new("RGBA", image.size, (255, 255, 255, 0))
    text_draw = ImageDraw.Draw(text_image)
    
    for dx in range(-stroke_width, stroke_width + 1):
        for dy in range(-stroke_width, stroke_width + 1):
            text_draw.text((5 + dx, 5 + dy), words, font=font, fill=stroke_color)
    
    text_draw.text((5, 5), words, font=font, fill=text_color)
    rotated_text = text_image.rotate(
        rotate_angle, expand=True, resample=Image.Resampling.BILINEAR
    )
    
    # text paste
    image.paste(rotated_text, (int(text_pos[0]), int(text_pos[1])), rotated_text)
    
    # debug
    # image.show()
    
    return image

def multi_sticker(stickers: list[Image.Image]) -> Image.Image:
    stickers_num = len(stickers)
    height = stickers_num // 5 + (stickers_num % 5 > 0)

    image = Image.new("RGBA", (850, height * 160), (255, 255, 255, 0))
    
    # test_image = Image.open(f"test.png")
    # test_image = test_image.resize((150, int(test_image.height * (150 / test_image.width))))
    
    for i in range(stickers_num):
        temp_image = stickers[i]
        temp_image = temp_image.resize((150, int(temp_image.height * (150 / temp_image.width))))
        image.paste(temp_image, ((i%5) * 150 + 50, (i//5) * 150), temp_image)
    # image.paste(test_image, (0, 0), test_image)

    # image.show()
    
    return image