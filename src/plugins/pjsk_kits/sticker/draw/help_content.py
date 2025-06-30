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

from PIL import Image, ImageDraw, ImageFont
from .sticker_main import simple_sticker, multi_sticker

def gen_helpcontent():
    sticker_list = []
    
    counter = 0
    for name in pj_count.keys():
        counter += 1
        # for id in range(1, pj_count[name] + 1):
        #     sticker_list.append(simple_sticker(name, id, f"{name} {id}"))
        sticker_list.append(simple_sticker(name, 1, f"{name}"))
    
    return multi_sticker(sticker_list)

def gen_char_helpcontent(name: str):
    sticker_list = []
    
    for id in range(1, pj_count[name] + 1):
        sticker_list.append(simple_sticker(name, id, f"{id}"))
    
    return multi_sticker(sticker_list)