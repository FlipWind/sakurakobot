from nonebot import logger
import requests
from bs4 import BeautifulSoup

headers = {
        'User-Agent': 'Sakurako/1.0 (Windows 10; Win64; x64) Napcat/1.6.7 animegarden',
        'Accept': '*/*',
        'Host': 'api.animes.garden',
        'Connection': 'close'
    }

class BangumiItem:
    def __init__(self, id, title, type, size, magnet):
        self.id = id
        self.title = title
        self.type = type
        self.size = size
        self.magnet = magnet


async def get_bangumi(keys: str, nums: int):
    bangumi_items = []
    _url = f"https://api.animes.garden/resources?pageSize={nums}&magnetWithoutTracker=true&search=[\"{keys}\"]"
    logger.success(f"Result Url: {_url}")

    try:
        response = requests.request("GET", _url, headers=headers)
        # logger.success(response.headers)
        # logger.success(response.text)
        if response.status_code == 200:
            data = response.json().get('resources', [])
            # print(data)

            _id = [resource['providerId'] for resource in data]
            _title = [resource['title'] for resource in data] 
            _type = [resource['type'] for resource in data]
            _size = [resource['size'] for resource in data]
            _magnet = [resource['magnet'] for resource in data]
            # _magnet = [resource['magnet'] for resource in data]

            for i in range(nums):
                bangumi_items.append(BangumiItem(_id[i], _title[i], _type[i], _size[i], _magnet[i]))
            
        else:
            print(f"请求失败，状态码: {response.status_code}")
    except Exception as e:
        logger.error("function get_bangumi() got an Unknown Expection", e)
        pass
        # TODO: email notice & qq notice
    return bangumi_items