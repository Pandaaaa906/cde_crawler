import asyncio
import re

from install_playwright import install
from loguru import logger
from parsel import Selector
from playwright.async_api import async_playwright, expect
from playwright_stealth import stealth_async, StealthConfig
from sqlalchemy.ext.asyncio import async_sessionmaker

from cde_crawler import settings
from cde_crawler.models import engine

logger.add(str(settings.ROOT / 'logs/cde_crawler.log'))

url = 'https://www.cde.org.cn/main/xxgk/listpage/b40868b5e21c038a6aa8b4319d21b07d'
Session = async_sessionmaker(engine)

EXIT_FLAG = False
stealth_config = StealthConfig()
stealth_config.navigator_languages = False
stealth_config.navigator_user_agent = False
stealth_config.navigator_vendor = False


async def detail_page_worker(context, tasks: asyncio.Queue, *, start_page: int = None, timeout=5*60*1000):
    async with (await context.new_page()) as page:
        await stealth_async(page, config=stealth_config)
        await page.goto(url)
        while not EXIT_FLAG or not tasks.empty():
            code = tasks.get()
            await page.goto(f"https://www.cde.org.cn/main/xxgk/postmarketpage?acceptidCODE={code}")
            html = Selector(await page.content())
            d ={
                ""
            }
            pass
            tasks.task_done()


async def list_page_worker(context, tasks: asyncio.Queue, *, start_page: int = None, timeout=5*60*1000):
    async with (await context.new_page()) as page:
        await stealth_async(page, config=stealth_config)
        await page.goto(url)

        loading = page.locator('xpath=//div[text()="拼命加载中..."]').first
        input_page = page.locator('xpath=//span[@class="layui-laypage-skip"]/input').first

        await page.locator('xpath=//select[@lay-ignore]').first.select_option("50")

        try:
            await expect(loading).not_to_be_visible(timeout=timeout)
        except Exception as e:
            logger.warning(f"loading not disappearing: {e}")

        if start_page:
            await input_page.fill(str(start_page))
            await page.locator('xpath=//span[@class="layui-laypage-skip"]/button').click()

        while True:
            try:
                await expect(loading).not_to_be_visible(timeout=5 * 60 * 1000)
            except Exception as e:
                logger.warning(f"loading not disappearing: {e}")
            cur_page = await input_page.get_attribute("value")

            html = Selector(await page.content())
            attr_rows = html.xpath('//tbody[@id="listDrugInfoTbody"]/tr/@ondblclick').getall()
            for attr in attr_rows:
                code = (m := re.search(r'openListDrugInfoDetail\(([^)]+)\)', attr)) and m.group()
                if not code:
                    continue
                await tasks.put(code)
            logger.info(f"waiting for page {cur_page} finish")
            await tasks.join()
            logger.info(f"crawled page {cur_page}")
            next_page = page.locator('xpath=//a[text()="下一页"]').first
            try:
                await next_page.click(timeout=2000)
            except:
                break


async def main(start_page: int = None, max_workers: int = 1, headless=True, timeout=5 * 60 * 1000):
    tasks = asyncio.Queue()
    async with async_playwright() as p:
        install(p.chromium)
        context = await p.chromium.launch_persistent_context(
            settings.usr_dir,
            headless=headless,
            timeout=timeout,
            user_agent=settings.user_agent,
        )
        page = await context.new_page()
        await stealth_async(page, config=stealth_config)

        await asyncio.gather(
            list_page_worker(context, tasks, start_page=start_page, timeout=timeout),
            # *(detail_page_worker(context, tasks, timeout=timeout) for _ in range(max_workers))
        )


if __name__ == '__main__':
    asyncio.run(main(headless=False))
