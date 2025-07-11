from ..utils import *


class QuoteMessage:
    class RankType(Enum):
        # Name, Background Color, Text Color
        NORMAL = "成员", (227, 227, 227), (186, 186, 186)
        ADMIN = "管理员", (0, 50, 50), (20, 190, 160)
        OWNER = "群主", (50, 40, 10), (230, 140, 20)
        SPECIAL = "SPECIAL", (70, 40, 90), (210, 140, 230)

    user_id: int
    group_id: int
    nick_name: str

    rank_type: RankType
    rank: int
    header: str

    message: Message

    def __init__(
        self,
        user_id: int,
        nick_name: str,
        rank: int,
        header: str,
        message: Message,
        rank_type: RankType,
        group_id: int,
    ):
        self.user_id = user_id
        self.nick_name = nick_name
        self.rank = rank
        self.header = header
        self.message = message
        self.rank_type = rank_type
        self.group_id = group_id

    def get_message_seg(self) -> List[MessageSegment]:
        list = []
        for segment in self.message:
            list.append(MessageSegment(segment.type, segment.data))
        return list


async def rend_quote_message(quote_message: QuoteMessage, bot: Bot) -> Image.Image:
    """Only rend a single quote message.
    To rend multiple quote messages, use `rend_multiple_quote_messages()`.
    Args:
        quote_message (QuoteMessage): The quote message to rend.
    Returns:
        Image.Image: The rendered image of the quote message.
    """
    image_background = (16, 17, 18)
    image_width = 940

    async def _font(name: str, size: int) -> ImageFont.FreeTypeFont:
        return ImageFont.truetype(f"{ASSETS_PATH}/fonts/{name}.ttf", size)

    # Rend the message
    async def rend_image(urls: List[str], sub_type: int = 0) -> Image.Image:
        """Rend the image from online resource.
        The max width is the width of message.
        Under this ratio, it is defined as 690px.
        Args:
            url (List[str]): a list of URLs.
                What you should know is that when url is a list, it will only return the first image.
                Would like to rend multiple images? use `rend_images()` instead.
        Returns:
            Image.Image: The rendered image.
        """
        image_width = 690

        async with httpx.AsyncClient() as client:
            tasks = [asyncio.create_task(client.get(u)) for u in urls]
            for task in asyncio.as_completed(tasks):
                try:
                    response = await task
                    if response.status_code == 200:
                        for t in tasks:
                            if not t.done():
                                t.cancel()

                        image_data = BytesIO(response.content)
                        image = Image.open(image_data)

                        new_height = int(image.height * image_width / image.width)

                        if image.width > image_width:
                            # resize the image to fit the width
                            image = image.resize(
                                (image_width, new_height), Image.Resampling.LANCZOS
                            )
                        
                        if sub_type == 1:
                            max_size = 310
                            if image.width > max_size or image.height > max_size:
                                scale_factor = min(max_size / image.width, max_size / image.height)
                                new_width = int(image.width * scale_factor)
                                new_height = int(image.height * scale_factor)
                                image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)

                        return image
                except Exception:
                    continue

        # a placeholder
        return Image.new("RGB", (690, 100), (50, 50, 50))

    # Rend the at message
    async def rend_text_message(
        text: str, font=await _font("MiSans-Medium", 46), color=(255, 255, 255)
    ) -> Image.Image:
        """Rend the text message.
        The default width is the width of message.
        Under this ratio, it is defined as 690px.
        Args:
            text (str): The text to rend.
        Returns:
            Image.Image: The rendered image.
        """
        image_width = 690
        line_height = 61

        # temp_img = Image.new("RGB", (1, 1))
        # with Pilmoji(temp_img) as pilmoji:
        #     font = _font("MiSans-Medium", font_size)
        #     text_image = pilmoji.text(text, font=font, fill=(255, 255, 255), width=image_width)

        if text.endswith("\n"):
            text = text[:-1]
        sentences = text.split("\n")
        lines = []
        current_line = ""

        # handle text into lines
        for sentence in sentences:
            if sentence.endswith(" "):
                sentence = sentence[:-1]
            words = sentence.split(" ")
            for word in words:
                pilmoji = Pilmoji(Image.new("RGB", (1, 1)))
                if current_line == "":
                    # the line is empty, so rend char by char
                    for char in word:
                        line_width = pilmoji.getsize(
                            current_line, font=font, emoji_scale_factor=0.9
                        )[0]
                        char_width = pilmoji.getsize(
                            char, font=font, emoji_scale_factor=0.9
                        )[0]
                        if line_width + char_width > image_width:
                            lines.append(current_line)
                            current_line = char
                        else:
                            current_line += char
                    line_width = pilmoji.getsize(
                        current_line + " ", font=font, emoji_scale_factor=0.9
                    )[0]
                    if line_width >= image_width:
                        lines.append(current_line)
                        current_line = ""
                    else:
                        current_line += " "
                else:
                    # the line not empty, try to add the word
                    line_width = pilmoji.getsize(
                        current_line + word, font=font, emoji_scale_factor=0.9
                    )[0]

                    if line_width > image_width:
                        # line too long, jump to the next line
                        lines.append(current_line)
                        current_line = ""
                        if (
                            pilmoji.getsize(word, font=font, emoji_scale_factor=0.9)[0]
                            >= image_width
                        ):
                            # the word is too big to go inside, rend char by char

                            ### same as above
                            for char in word:
                                line_width = pilmoji.getsize(
                                    current_line, font=font, emoji_scale_factor=0.9
                                )[0]
                                char_width = pilmoji.getsize(
                                    char, font=font, emoji_scale_factor=0.9
                                )[0]
                                if line_width + char_width > image_width:
                                    lines.append(current_line)
                                    current_line = char
                                else:
                                    current_line += char
                            line_width = pilmoji.getsize(
                                current_line + " ", font=font, emoji_scale_factor=0.9
                            )[0]
                            if line_width >= image_width:
                                lines.append(current_line)
                                current_line = ""
                            else:
                                current_line += " "
                            ### end

                        else:
                            current_line = word + " "
                    else:
                        current_line += word + " "
            if current_line:
                lines.append(current_line)
                current_line = ""
        if current_line != "":
            lines.append(current_line)

        image_width = 0
        for line in lines:
            with Pilmoji(Image.new("RGB", (1, 1))) as pilmoji:
                image_width = max(
                    image_width,
                    pilmoji.getsize(line, font=font, emoji_scale_factor=0.9)[0],
                )

        # rend the lines
        text_image_height = len(lines) * line_height
        text_image = Image.new(
            "RGBA", (image_width, text_image_height), (255, 255, 255, 0)
        )

        for i, line in enumerate(lines):
            with Pilmoji(text_image) as pilmoji:
                pilmoji.text(
                    (0, i * line_height),
                    line,
                    fill=color,
                    font=font,
                    emoji_scale_factor=0.9,
                    emoji_position_offset=(0, 8),
                )

        return text_image

    # Calculate the height of the image
    async def rend_content(quote_message: QuoteMessage):
        image_height = 0

        messages = quote_message.get_message_seg()
        message_images = []
        text_lists = ""
        for message in messages:
            if message.type == "image":
                if text_lists != "":
                    message_images.append(("text", await rend_text_message(text_lists)))
                    text_lists = ""
                image_message = await rend_image([message.data["url"]], int(message.data["sub_type"]))

                mask = Image.new("L", image_message.size, 0)
                ImageDraw.Draw(mask).rounded_rectangle(
                    [(0, 0), image_message.size], radius=12, fill=255
                )
                image_message.putalpha(mask)
                message_images.append(("image", image_message))

            if message.type == "text":
                text_lists += message.data["text"]
            if message.type == "at":
                profile = await bot.get_group_member_info(
                    group_id=quote_message.group_id,
                    user_id=message.data["qq"],
                )

                text_lists += f' @{profile["card"] if profile["card"] else profile["nickname"]}'  # front with a space

        if text_lists != "":
            message_images.append(("text", await rend_text_message(text_lists)))

        for message_image in message_images:
            image_height += message_image[1].height
        image_height += (len(message_images) - 1) * 8

        content_image_width = 690
        content_image_width = max(
            message_image[1].width for message_image in message_images
        )

        content_image = Image.new(
            "RGBA", (content_image_width, image_height), (255, 255, 255, 0)
        )

        _y = 0
        for message_image in message_images:
            content_image.paste(message_image[1], (0, _y))
            _y += message_image[1].height + 8

        return content_image

    content_image = await rend_content(quote_message)
    image_height = content_image.height + 94 + (24 + 37) + 25
    # 94: from top to message_box
    # 24 + 37: top padding + bottom padding
    # 25: message_box to the bottom

    quote_image = Image.new("RGB", (image_width, image_height), image_background)

    # profile
    profile_xy = (30, 22)
    profile_image = await rend_image(
        [
            f"http://q2.qlogo.cn/headimg_dl?dst_uin={quote_message.user_id}&spec=640",
            f"http://q1.qlogo.cn/g?b=qq&nk={quote_message.user_id}&s=640",
            f"http://q.qlogo.cn/headimg_dl?spec=640&dst_uin={quote_message.user_id}",
        ]
    )
    profile_image = profile_image.resize((110, 110), Image.Resampling.LANCZOS)

    mask = Image.new("L", (110, 110), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, 110, 110), fill=255)
    profile_image.putalpha(mask)

    quote_image.paste(profile_image, profile_xy, profile_image)

    # rank and header
    rank_text_xy = (172, 29)
    rank_header_xy = (160, 22)
    rank_text = f"LV{quote_message.rank} {quote_message.header}"
    # await rend_text_message(
    #     rank_text,
    #     font=await _font("MiSans-Semibold", 23),
    #     color=quote_message.rank_type.value[2],
    # )

    rank_text_width = 0
    with Pilmoji(Image.new("RGB", (1, 1))) as pilmoji:
        rank_text_width = pilmoji.getsize(
            rank_text, font=await _font("MiSans-Semibold", 23), emoji_scale_factor=0.9
        )[0]

    rank_header_xy_end = (160 + rank_text_width + 24, 22 + 46)

    ImageDraw.Draw(quote_image).rounded_rectangle(
        [rank_header_xy, rank_header_xy_end],
        radius=12,
        fill=quote_message.rank_type.value[1],
    )

    with Pilmoji(quote_image) as pilmoji:
        pilmoji.text(
            rank_text_xy,
            rank_text,
            fill=quote_message.rank_type.value[2],
            font=await _font("MiSans-Semibold", 23),
            emoji_scale_factor=0.9,
            emoji_position_offset=(0, 8),
        )

    # nickname
    nickname_xy = (rank_header_xy_end[0] + 12, rank_header_xy[1] + 4)

    with Pilmoji(quote_image) as pilmoji:
        pilmoji.text(
            nickname_xy,
            quote_message.nick_name,
            fill=(140, 140, 140),
            font=await _font("MiSans-Medium", 28),
            emoji_scale_factor=0.9,
            emoji_position_offset=(0, 8),
        )

    # message box
    message_box_xy = (160, 94)
    message_box_xy_end = (
        160 + content_image.width + 25 + 25,
        94 + content_image.height + 24 + 24,
    )

    ImageDraw.Draw(quote_image).rounded_rectangle(
        [message_box_xy, message_box_xy_end], radius=25, fill=(37, 38, 40)
    )

    if (
        len(quote_message.get_message_seg()) == 1
        and quote_message.get_message_seg()[0].type == "image"
    ):
        content_image = content_image.resize(
            (content_image.width + 25 + 25, content_image.height + 24 + 24),
            resample=Image.Resampling.LANCZOS,
        )
        quote_image.paste(content_image, (160, 94), content_image)
    else:
        quote_image.paste(content_image, (185, 118), content_image)

    return quote_image


async def rend_quote_messages(messages: List[QuoteMessage], bot: Bot):
    message_images = []
    for message in messages:
        message_image = await rend_quote_message(message, bot)
        message_images.append(message_image)

    _y = 0
    total_height = sum(image.height for image in message_images)
    result_image = Image.new("RGBA", (940, total_height), (16, 17, 18, 100))

    for message_image in message_images:
        result_image.paste(message_image, (0, _y))
        _y += message_image.height

    return result_image
