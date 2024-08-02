import asyncio

import typer

from spiders import scrap_cde, cde_approval

app = typer.Typer()


@app.command()
def run_scrap_cde(headless: bool = True, start_page: int = None, timeout: int = 5 * 60 * 1000):
    asyncio.run(scrap_cde.main(headless=headless, start_page=start_page, timeout=timeout))


@app.command()
def run_cde_approval(
        headless: bool = True, max_workers: int = 1, start_page: int = None, timeout: int = 5 * 60 * 1000
):
    asyncio.run(cde_approval.main(
        headless=headless, start_page=start_page, max_workers=max_workers, timeout=timeout
    ))


if __name__ == '__main__':
    app()
