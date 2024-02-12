from httpx import Client
from asyncio import Semaphore

# replace with new cookies or keep commented if works without it

HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
    #"Cookie": "",
    "Referer": "https://shopping.google.com/",
    "Sec-Ch-Ua": 'Not A(Brand";v="99", "Google Chrome";v="121"',
}

async def request_page(url:str, client: Client, semaphore:Semaphore) -> str: 
    async with semaphore:
        response = await client.get(url, headers=HEADERS)
        return response.text