from nonebot import logger
from ..utils import *
import requests
from bs4 import BeautifulSoup
import httpx

bgmtv_headers = {
    "User-Agent": "flipwind/sakurako (Windows 10; Linux) Napcat/1.6.7",
    "Accept": "*/*",
    "Connection": "close",
}


# Daily Calendar
class CalendarDayItem:
    def __init__(self, weekday, items):
        self.weekday = weekday
        self.items: list[CalendarItem] = items


class CalendarItem:
    def __init__(self, id, url, air_date, name, name_cn, image_url, score, rank):
        self.id = id
        self.url = url
        self.air_date = air_date

        self.name = name
        self.name_cn = name_cn
        self.image_url = image_url

        self.score = score
        self.rank = rank


async def get_calendar(weekday: int) -> CalendarDayItem:
    calendar_day_items = []

    today_weekday = datetime.datetime.now().weekday()
    if weekday == None or weekday < 0 or weekday > 6:
        weekday = today_weekday

    _url = "https://api.bgm.tv/calendar"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(_url, headers=bgmtv_headers)
        if response.status_code == 200:
            data = response.json()[weekday]

            for item in data.get("items", []):
                calendar_day_items.append(
                    CalendarItem(
                        id=item.get("id"),
                        url=item.get("url"),
                        air_date=item.get("air_date"),
                        name=item.get("name"),
                        name_cn=item.get("name_cn"),
                        image_url=item.get("images", {}).get("large"),
                        score=item.get("rating", {}).get("score"),
                        rank=item.get("rank"),
                    )
                )
        else:
            print(f"请求失败，状态码: {response.status_code}")
    except Exception as e:
        logger.error("function get_calendar() got an Unknown Expection", e)
        pass
    return CalendarDayItem(weekday=weekday, items=calendar_day_items)


# Search Bangumi
class SearchBangumiItem:
    def __init__(self, id, platform, date, name, name_cn, image_url, eps, tags, score, rank):
        self.id = id
        self.date = date
        self.platform = platform

        self.name = name
        self.name_cn = name_cn
        self.image_url = image_url

        self.eps = eps
        self.tags = tags
        self.score = score
        self.rank = rank


async def search_bangumi(keyword: str) -> list[SearchBangumiItem]:
    search_results = []

    _url = f"https://api.bgm.tv/v0/search/subjects"

    body = {"keyword": keyword, "sort": "rank", "filter": {"type": [2]}}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(_url, headers=bgmtv_headers, json=body)
        if response.status_code == 200:
            data = response.json()
            for item in data.get("data", []):
                search_results.append(
                    SearchBangumiItem(
                        id=item.get("id"),
                        platform=item.get("platform"),
                        date=item.get("date"),
                        name=item.get("name"),
                        name_cn=item.get("name_cn"),
                        image_url=item.get("image"),
                        eps=item.get("eps"),
                        tags=[tag.get("name") for tag in item.get("tags", [])],
                        score=item.get("rating", {}).get("score"),
                        rank=item.get("rating", {}).get("rank"),
                    )
                )
        else:
            print(f"请求失败，状态码: {response.status_code}")
    except Exception as e:
        logger.error("function search_bangumi() got an Unknown Expection", e)
        pass
    
    search_results.sort(key=lambda x: x.date or "", reverse=True)
    
    return search_results

# Search Character
class SearchCharacterItem:
    def __init__(self, id, name, gender, image_url, summary, related_subjects):
        self.id = id

        self.name = name
        self.gender = gender # maybe null
        self.image_url = image_url

        self.summary = summary
        self.related_subjects: list[RelatedSubjectItem] = related_subjects

class RelatedSubjectItem:
    def __init__(self, id, staff, name, name_cn):
        self.id = id
        self.staff = staff
        self.name = name
        self.name_cn = name_cn

async def search_character(keyword: str) -> list[SearchCharacterItem]:
    search_results = []

    _url = f"https://api.bgm.tv/v0/search/characters"

    body = {"keyword": keyword, "sort": "rank"}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(_url, headers=bgmtv_headers, json=body)
        if response.status_code == 200:
            data = response.json()
            for item in data.get("data", []):
                search_results.append(
                    SearchCharacterItem(
                        id=item.get("id"),
                        name=item.get("name"),
                        gender=item.get("gender"),
                        image_url=item.get("images", {}).get("large"),
                        summary=item.get("summary"),
                        related_subjects=await get_character_related_subjects(item.get("id")),
                    )
                )
        else:
            logger.error(f"请求失败，状态码: {response.status_code}")
    except Exception as e:
        logger.error(f"function search_character() got an Unknown Expection: {e}")
        pass
    
    return search_results

async def get_character_related_subjects(character_id: int) -> list[RelatedSubjectItem]:
    related_subjects = []

    _url = f"https://api.bgm.tv/v0/characters/{character_id}/subjects"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(_url, headers=bgmtv_headers)
        if response.status_code == 200:
            data = response.json()
            for item in data:
                related_subjects.append(
                    RelatedSubjectItem(
                        id=item.get("id"),
                        staff=item.get("staff"),
                        name=item.get("name"),
                        name_cn=item.get("name_cn"),
                    )
                )
        else:
            logger.error(f"请求失败，状态码: {response.status_code}")
    except Exception as e:
        logger.error(f"function get_character_related_subjects() got an Unknown Expection: {e}")
        pass
    
    return related_subjects