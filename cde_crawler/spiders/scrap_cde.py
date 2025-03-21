import asyncio
from datetime import date

from install_playwright import install
from loguru import logger
from parsel import Selector
from playwright.async_api import async_playwright, expect
from playwright_stealth import stealth_async, StealthConfig
from sqlalchemy.ext.asyncio import async_sessionmaker

from .. import settings
from cde_crawler.models import engine, CDE
from cde_crawler.utils.db_operations import upsert_table

logger.add(str(settings.ROOT / 'logs/cde_crawler.log'))

url = 'https://www.cde.org.cn/main/xxgk/listpage/9f9c74c73e0f8f56a8bfbc646055026d'
Session = async_sessionmaker(engine)


async def main(start_page: int = None, headless=True, timeout=5 * 60 * 1000):
    async with (
        async_playwright() as p,
        Session() as db
    ):
        install(p.chromium)
        context = await p.chromium.launch_persistent_context(
            settings.usr_dir,
            headless=headless,
            timeout=timeout,
            user_agent=settings.user_agent,
        )
        page = await context.new_page()
        config = StealthConfig()
        config.navigator_languages = False
        config.navigator_user_agent = False
        config.navigator_vendor = False
        await stealth_async(page, config=config)

        await page.goto(url)
        loading = page.locator('xpath=//div[text()="拼命加载中..."]').first
        selector_year = page.locator('xpath=//select[@id="year"]/following-sibling::div').first
        await selector_year.click()
        await page.locator('xpath=//select[@id="year"]/following-sibling::div//dd[text()="全部"]').click()

        await page.locator('xpath=//select[@lay-ignore]').first.select_option("50")

        try:
            await expect(loading).not_to_be_visible(timeout=5 * 60 * 1000)
        except Exception as e:
            logger.warning(f"loading not disappearing: {e}")

        input_page = page.locator('xpath=//span[@class="layui-laypage-skip"]/input')

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

            rows = html.xpath('//tbody[@id="acceptVarietyInfoTbody"]/tr')
            for row in rows:
                accept_date = row.xpath('./td[8]/text()').get('').strip()
                accept_date = date.fromisoformat(accept_date) if accept_date else None
                d = {
                    "code": row.xpath('./td[2]/text()').get(),
                    "name": row.xpath('./td[3]/text()').get(),
                    "drug_type": row.xpath('./td[4]/text()').get(),
                    "apply_type": row.xpath('./td[5]/text()').get(),
                    "reg_type": row.xpath('./td[6]/text()').get(),
                    "pharm_name": row.xpath('./td[7]/text()').get(),
                    "accept_date": accept_date,
                }
                d = {k: v or None for k, v in d.items()}
                await upsert_table(db, CDE, d, index_elements=['code'], do_update=True)

            await db.commit()
            logger.info(f"crawled page {cur_page}")
            next_page = page.locator('xpath=//a[text()="下一页"]').first
            try:
                await next_page.click(timeout=2000)
            except Exception as e:
                logger.error(e)
                break


if __name__ == '__main__':
    asyncio.run(main(headless=False))
