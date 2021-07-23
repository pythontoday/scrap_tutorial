import asyncio
import json
import logging
import sys
from typing import List, Dict, Optional, Any
from urllib.parse import urljoin

from bs4 import BeautifulSoup
import aiohttp

OFFSET_URL = ('https://www.skiddle.com/festivals/search/?ajaxing=1&sort=0&fest_name=&'
              'from_date=24%20Jan%202021&to_date=&where%5B%5D=2&where%5B%5D=3&'
              'where%5B%5D=4&where%5B%5D=6&where%5B%5D=7&where%5B%5D=8&where%5B%5D=9&'
              'where%5B%5D=10&maxprice=500&o={offset}&bannertitle=May')
HEADERS = {
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36'
}
MAX_OFFSET = 192
DELAY = 0.1  # delay between requests in seconds

logger = logging.getLogger(__name__)
logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def parse_fest_urls(html: str) -> List[str]:
    """Parse html and return a list of festival urls."""
    soup = BeautifulSoup(html, 'lxml')
    return [
        urljoin('https://www.skiddle.com', elem['href'])
        for elem in soup.find_all('a', class_='card-details-link')
    ]


async def get_fests_urls_from_url(
        session: aiohttp.ClientSession, url: str
) -> List[str]:
    """Return a list of festivals urls from the page with specified url."""
    logging.info('Fetching urls from %s', url)
    async with session.get(url) as response:
        html = (await response.json(content_type=None))['html']
    return parse_fest_urls(html)


async def get_fests_urls(session: aiohttp.ClientSession) -> List[str]:
    """Return a list of festival urls."""
    tasks = []
    for offset in range(0, MAX_OFFSET, 24):
        url = OFFSET_URL.format(offset=offset)
        tasks.append(asyncio.create_task(get_fests_urls_from_url(session, url)))
        await asyncio.sleep(DELAY)

    await asyncio.gather(*tasks)
    fests_urls = [url for task in tasks for url in task.result()]
    return fests_urls


def parse_fest_info(html: str) -> Dict[str, Optional[str]]:
    """Parse html and return a dict with festival information."""
    soup = BeautifulSoup(html, 'lxml')
    fest_info_block = soup.find('div', class_='top-info-cont')
    try:
        fest_name = fest_info_block.find('h1').text.strip()
    except Exception:
        fest_name = None
    try:
        fest_date = fest_info_block.find('h3').text.strip()
    except Exception:
        fest_date = None
    try:
        fest_location_url = urljoin(
            'https://www.skiddle.com',
            fest_info_block.find('a', class_='tc-white')['href']
        )
    except Exception:
        fest_location_url = None
    return {
        'fest_name': fest_name,
        'fest_date': fest_date,
        'fest_location_url': fest_location_url
    }


def parse_fest_contact_info(html: str) -> Dict[str, str]:
    """Parse html and return a dict with festival contact information."""
    soup = BeautifulSoup(html, 'lxml')
    contact_details = soup.find('h2', string='Venue contact details and info').find_next()
    items = [item.text for item in contact_details.find_all('p')]
    return {
        key.strip().lower().replace(' ', '_'): value.strip()
        for key, value
        in map(lambda s: s.split(':', 1), items)
    }


async def get_fest_info(session: aiohttp.ClientSession, url: str) -> Dict[str, Any]:
    """Return festival information from specified url."""
    logging.info('Fetching festival info from %s', url)
    async with session.get(url) as response:
        festival_html = await response.text()
    fest_info = parse_fest_info(festival_html)  # type: Dict[str, Any]
    async with session.get(fest_info.pop('fest_location_url')) as response:
        place_html = await response.text()
    fest_info['contact_info'] = parse_fest_contact_info(place_html)
    return fest_info


async def get_fests_info(
        session: aiohttp.ClientSession, urls: List[str]
) -> List[Dict[str, Any]]:
    """Return a list of dicts with information about festivals."""
    tasks = []
    for url in urls:
        tasks.append(asyncio.create_task(get_fest_info(session, url)))
        await asyncio.sleep(DELAY)

    await asyncio.gather(*tasks)
    return [task.result() for task in tasks]


async def main() -> None:
    async with aiohttp.ClientSession(headers=HEADERS) as session:
        logger.info('Starting fetching urls...')
        fests_urls = await get_fests_urls(session)
        logger.info('Finished fetching urls')

        logger.info('Starting downloading information about festivals...')
        fests_info = await get_fests_info(session, fests_urls)
        logger.info('Finished downloading information about festivals')

        logger.info('Saving parsed information to file...')
        with open('fest_list_result_async.json', 'w', encoding='utf-8') as f:
            json.dump(fests_info, f, indent=4, ensure_ascii=False)
        logger.info('Done')


if __name__ == '__main__':
    asyncio.run(main())
