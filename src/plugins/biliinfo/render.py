from ..utils import *

class OwnerInfo:
    mid: int
    name: str
    face_url: str
    
    def __init__(self, mid: int, name: str, face_url: str):
        self.mid = mid
        self.name = name
        self.face_url = face_url

class VideoInfo:
    bvid: str
    
    title: str
    owner: OwnerInfo
    cover_url: str
    duration: int # 视频长度
    
    publictime: int
    view: int
    danmaku: int
    reply: int
    
    like: int
    coin: int
    favorite: int
    share: int
    
    desc: str
    
    def __init__(self, bvid: str, title: str, owner: OwnerInfo, cover_url: str, duration: int, publictime: int, view: int, danmaku: int, reply: int, like: int, coin: int, favorite: int, share: int, desc: str):
        self.bvid = bvid
        self.title = title
        self.owner = owner
        self.cover_url = cover_url
        self.duration = duration
        
        self.publictime = publictime
        self.view = view
        self.danmaku = danmaku
        self.reply = reply
        
        self.like = like
        self.coin = coin
        self.favorite = favorite
        self.share = share
        
        self.desc = desc
        
    def __str__(self):
        return f"视频BV号: {self.bvid}\n" \
               f"视频标题: {self.title}\n" \
               f"视频UP主: {self.owner.name}\n" \
               f"视频封面: {self.cover_url}\n" \
               f"视频时长: {self.duration}秒\n" \
               f"发布时间: {self.publictime}\n" \
               f"观看人数: {self.view}\n" \
               f"弹幕数量: {self.danmaku}\n" \
               f"评论数量: {self.reply}\n" \
               f"点赞数量: {self.like}\n" \
               f"投币数量: {self.coin}\n" \
               f"收藏数量: {self.favorite}\n" \
               f"分享数量: {self.share}\n" \
               f"视频简介: {self.desc}\n" 
    

# get video infomation
async def get_video_info(bvid: str) -> VideoInfo:
    url = f"https://api.bilibili.com/x/web-interface/view?bvid={bvid}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
        "Referer": "https://www.bilibili.com/",
    }

    async with httpx.AsyncClient(timeout=1000.0) as client:
        response = await client.get(url, follow_redirects=True, headers=headers)
        # print(response)
        if response.status_code != 200:
            raise Exception("获取数据失败，请稍后再试。")
    
    response.encoding = 'utf-8'
    res_json = json.loads(response.text)["data"]
    # print(res_json)
    
    try:
        return VideoInfo(
            res_json["bvid"],
            res_json["title"],
            OwnerInfo(
                res_json["owner"]["mid"],
                res_json["owner"]["name"],
                res_json["owner"]["face"]
            ),
            res_json["pic"],
            res_json["duration"],
            res_json["pubdate"],
            res_json["stat"]["view"],
            res_json["stat"]["danmaku"],
            res_json["stat"]["reply"],
            res_json["stat"]["like"],
            res_json["stat"]["coin"],
            res_json["stat"]["favorite"],
            res_json["stat"]["share"],
            res_json["desc"]
        )
    except:
        raise Exception("转码失败，请稍后再试。")

def call_font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(f"{ASSETS_PATH}/fonts/MiSans-Bold.ttf", size)

def format_number(num):
    if num >= 1_000_000_000:
        return f"{num / 1_000_000_000:.1f}B"
    elif num >= 1_000_000:
        return f"{num / 1_000_000:.1f}M"
    elif num >= 1_000:
        return f"{num / 1_000:.1f}k"
    else:
        return f"{num:.1f}".rstrip('0').rstrip('.')

async def rend_image(video_info: VideoInfo) -> Image.Image:
    # pass
    image = Image.open(f"./assets/bilinote/bili.png")
    WHITE = (255, 255, 255, 255)
    GRAY = (212, 212, 212, 255)
    
    draw = ImageDraw.Draw(image)
    font72 = call_font(72)
    font58 = call_font(58)
    font50 = call_font(50)
    font36 = call_font(36)
    font18 = call_font(18)
    
    max_width = 1841
    title = video_info.title
    while font72.getlength(title) > max_width:
        title = title[:-1]
    if font72.getlength(video_info.title) > max_width:
        title = title[:-3] + "..."
    draw.text((153, 83), title, font=font72, fill=WHITE)
    draw.text((289,213), video_info.owner.name, font=font58, fill=GRAY)
    
    duration_minutes, duration_seconds = divmod(video_info.duration, 60)
    duration_hours, duration_minutes = divmod(duration_minutes, 60)
    if duration_hours > 0:
        duration_text = f"{duration_hours} 小时 {duration_minutes} 分钟 {duration_seconds} 秒"
    elif duration_minutes > 0:
        duration_text = f"{duration_minutes} 分钟 {duration_seconds} 秒"
    else:
        duration_text = f"{duration_seconds} 秒"
    
    draw.text((1350, 355), duration_text, font=font50, fill=WHITE)
    
    readable_time = datetime.datetime.fromtimestamp(video_info.publictime).strftime("%Y-%m-%d %H:%M:%S")
    draw.text((1350, 449), readable_time, font=font50, fill=WHITE)
    
    
    
    draw.text((1350, 548), format_number(video_info.view), font=font50, fill=WHITE)
    draw.text((1350, 648), format_number(video_info.danmaku), font=font50, fill=WHITE)
    draw.text((1350, 740), format_number(video_info.reply), font=font50, fill=WHITE)
    
    draw.text((1319, 834), format_number(video_info.like), font=font36, fill=WHITE)
    draw.text((1521, 834), format_number(video_info.coin), font=font36, fill=WHITE)
    draw.text((1721, 834), format_number(video_info.favorite), font=font36, fill=WHITE)
    draw.text((1921, 834), format_number(video_info.share), font=font36, fill=WHITE)
    
    draw.text((91, 1017), video_info.bvid, font=font36, fill=WHITE)
    
    video_info.desc = "简介：\n" + video_info.desc
    desc_lines = []
    for paragraph in video_info.desc.split("\n"):
        desc_lines.extend(textwrap.wrap(paragraph, width=44))
    y_offset = 904
    max_lines = 7
    for i, line in enumerate(desc_lines):
        if i >= max_lines:
            draw.text((1249, y_offset), "...", font=font18, fill=WHITE)
            break
        draw.text((1249, y_offset), line, font=font18, fill=WHITE)
        y_offset += 30
    
    async with httpx.AsyncClient() as client:
        response = await client.get(video_info.cover_url)
        if response.status_code == 200:
            cover_image = Image.open(BytesIO(response.content))
            ori_width, ori_height = cover_image.size
            tar_width, tar_height = 1123, 642
            
            scale_x = tar_width / ori_width
            scale_y = tar_height / ori_height
            scale = max(scale_x, scale_y)
            
            new_width = int(ori_width * scale)
            new_height = int(ori_height * scale)
            
            cover_image = cover_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            width, height = cover_image.size
            left = (width - 1123) // 2
            top = (height - 642) // 2
            right = left + 1123
            bottom = top + 642
            cover_image = cover_image.crop((left, top, right, bottom))
            
            mask = Image.new("L", cover_image.size, 0)
            draw_mask = ImageDraw.Draw(mask)
            draw_mask.rounded_rectangle((0, 0, 1123, 642), radius=64, fill=255)
            cover_image.putalpha(mask)
            
            image.paste(cover_image, (91, 355), cover_image)
    
    async with httpx.AsyncClient() as client:
        response = await client.get(video_info.owner.face_url)
        if response.status_code == 200:
            owner_face = Image.open(BytesIO(response.content))
            owner_face = owner_face.resize((104, 104), Image.Resampling.LANCZOS)
            
            mask = Image.new("L", owner_face.size, 0)
            draw_mask = ImageDraw.Draw(mask)
            draw_mask.ellipse((0, 0, 104, 104), fill=255)

            owner_face.putalpha(mask)

            image.paste(owner_face, (153, 200), owner_face)
    
    # image.show()
    
    return image