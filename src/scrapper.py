# imports

import httpx
import asyncio

from datetime import date
from datetime import datetime

from tinydb import TinyDB
from tinydb import  Query

from selectolax.parser import HTMLParser

#local imports
from utils import request_page

# global variables
db = TinyDB(f'./data/scraping/{datetime.now().strftime("%m_%d_%Y_%H_%M_%S")}.json')
query = Query()
sempahore = asyncio.Semaphore(10)
client = httpx.AsyncClient()

async def searching_products_page(search_name:str, max_items:int, last_index:int=0, inserted_lines=[]) -> list: 
    """Scrapes data from Google Shopping search page.

    Args:
        search_name (str): Product name for which information is to be extracted.
        max_items (int): Maximum number of items to request; higher values result in more requests.
        last_index (int, optional): Auxiliary recursive parameter; does not require a value when calling the function.

    Returns:
        list: Number of rows inserted into TinyDB.
    """

    current_page_url = f"https://www.google.com/search?tbm=shop&q={search_name.replace(' ', '+')}&start={last_index}"
    print('Scraping... ', current_page_url)

    # Make an asynchronous request to get the HTML page and parse the HTML with selectolax 
    html_page = await request_page(current_page_url, semaphore=sempahore, client=client)
    html_parser = HTMLParser(html_page)
    parser_products = html_parser.css('div[class="xcR77"]')
    
    # Extract product information using CSS selectors
    scraping_data = [
        {
            'load_ts': datetime.now().strftime("%m/%d/%Y, %H:%M:%S"),
            'search_page':current_page_url,
            'title': product.css_first('div[class="rgHvZc"] a').text(),
            'link': product.css_first('div[class="rgHvZc"] a').attrs.get('href'),
            'best_price_store': product.css_first('div[class="dD8iuc"]').text(),
            'best_price': product.css_first('span[class="HRLxBb"]').text(),
            'compare_prices': product.css_first('a[class="DKkjqf"]').attrs.get('href') if product.css_first('a[class="DKkjqf"]') else None
         } for product in parser_products if product.css_first('div[class="rgHvZc"] a') ]
    
    inserts = db.insert_multiple(scraping_data)
    scraping_data_len = len(scraping_data)
    
    if (scraping_data_len+last_index < max_items) & (scraping_data_len > 0):
        # If not enough items have been scraped, recursively call the function with an updated last_index
        return await searching_products_page(
            search_name=search_name,
            max_items=max_items,
            last_index=scraping_data_len+last_index,
            inserted_lines=inserted_lines+inserts
            )
    
    return inserted_lines

asyncio.run(searching_products_page('iphone', 40))
