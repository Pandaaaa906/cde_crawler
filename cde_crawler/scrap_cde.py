import asyncio
from math import inf

from loguru import logger
from pyppeteer import launch, errors
from peewee_async import Manager
from peewee import IntegrityError
from pyppeteer_stealth import stealth
from more_itertools import first

from models import database, CDE
from psycopg2.errors import UniqueViolation

from utils import strip


logger.add('logs/cde_crawler.log')

base_url = "http://www.cde.org.cn/news.do?method=changePage&pageName=service&frameStr=20"
loop = asyncio.get_event_loop()
objects = Manager(database=database, loop=loop)

# objects.database.allow_sync = False

args = ['--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-infobars',
        '--window-position=0,0',
        '--ignore-certifcate-errors',
        '--disable-gpu',
        '--ignore-certifcate-errors-spki-list',
        '--disable-gpu-shader-disk-cache',
        '--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3312.0 Safari/537.36'
        ]


async def get_text_by_xpath(page, xpath: str):
    (await (first(await page.xpath(xpath)).getProperty('textContent'))).jsonValue()


async def process_item(item):
    try:
        await objects.create(
            CDE,
            **item
        )
    except UniqueViolation:
        logger.trace(f"Unique Violation Occurred:{item!r}")
    except IntegrityError:
        logger.trace(f"Unique Violation Occurred:{item!r}")


async def parse_list(page):
    x_query = '//form[@name="transparentForm"]//table[thead]/tbody/tr'
    await page.waitForXPath(x_query)
    rows = await page.xpath(x_query)
    for row in rows:
        d = {
            "code": strip(await (await (first(await row.xpath('./td[1]')).getProperty('textContent'))).jsonValue()),
            "name": strip(await (await (first(await row.xpath('./td[2]')).getProperty('textContent'))).jsonValue()),
            "drug_type": strip(
                await (await (first(await row.xpath('./td[3]')).getProperty('textContent'))).jsonValue()),
            "apply_type": strip(
                await (await (first(await row.xpath('./td[4]')).getProperty('textContent'))).jsonValue()),
            "reg_type": strip(await (await (first(await row.xpath('./td[5]')).getProperty('textContent'))).jsonValue()),
            "pharm_name": strip(
                await (await (first(await row.xpath('./td[6]')).getProperty('textContent'))).jsonValue()),
            "accept_date": strip(
                await (await (first(await row.xpath('./td[7]')).getProperty('textContent'))).jsonValue()) or None,
        }
        await process_item(d)


async def get_catalog(page, start_page: int = 1, stop_page: int = None):
    global snapshot1
    logger.info("Start crawling")
    await (await page.waitForXPath('//td[@id="menuE_02"]', visible=True)).click()
    await (await page.waitForXPath('//td[@id="menuE_021"]//a[contains(text(), "受理目录浏览")]')).click()

    chl_f, *_ = page.mainFrame.childFrames
    await chl_f.waitForSelector('select[name="year"]')
    await chl_f.select('select[name="year"]', '全部')
    await (await chl_f.waitForXPath('//span[@class="menu"]')).click()

    # select more record in one page
    await chl_f.select('#pageMaxNum', '80')
    # jump to page
    if start_page != 1:
        elem = await chl_f.waitForSelector('input[name="pagenum"]')
        await chl_f.evaluate(f'''
        document.querySelector('input[name="pagenum"]').value = "{start_page}";
        ''')
        await elem.click()
        await page.keyboard.press("Enter")
        await chl_f.waitForXPath(f'//td[@id="pageNumber"]/font[position()=1 and text()="{start_page}"]')

    cur_page = start_page or 1
    stop_page = stop_page or inf
    while stop_page > cur_page:
        # parse record
        await parse_list(chl_f)

        # Next Page
        cur_page = int(await(
            await (first(await chl_f.xpath('//td[@id="pageNumber"]/font[1]')).getProperty('textContent'))).jsonValue())
        logger.info(f"Page {cur_page} is finished")
        next_page = await chl_f.waitForXPath('//img[contains(@src,"nextPage")]/parent::a')
        await next_page.click()
        try:
            await chl_f.waitForXPath(f'//td[@id="pageNumber"]/font[position()=1 and text()={str(cur_page+1)!r}]')
        except errors.TimeoutError:
            logger.info("Cannot find next page, exiting")
            break
        pass


async def main(start_page: int = None, stop_page: int = None):
    # Initial
    CDE.create_table(fail_silently=True)
    logger.info("starting browser")
    browser = await launch(ignoreHTTPSErrors=True,
                           headless=True,
                           userDataDir='./tmp',
                           args=args
                           )
    page = await browser.newPage()
    await stealth(page)
    await page.setViewport({'width': 800, 'height': 600})
    await page.goto(base_url)

    # Entering target page
    await get_catalog(page, start_page, stop_page)

    await browser.close()


if __name__ == "__main__":
    loop.run_until_complete(main(start_page=1))
