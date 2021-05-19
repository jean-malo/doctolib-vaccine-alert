import asyncio
import json
import os
from playwright.async_api import Response
from playwright.async_api import async_playwright
import sqlite3
from . import settings
from .alert import send_alert
import logging

logger = logging.getLogger(__name__)


async def scroll(page):
    logger.info("Scrolling")
    cur_dist = 0
    height = await page.evaluate("() => document.body.scrollHeight")
    while True:
        if cur_dist < height:
            await asyncio.sleep(0.4)
            await page.evaluate("window.scrollBy(0, 500);")
            cur_dist += 500
        else:
            break
    await page.wait_for_load_state(state="networkidle")
    await asyncio.sleep(settings.RATE_LIMIT)
    await page.evaluate("window.scrollTo(0, 0);")
    await page.reload()


def check_if_table_exists():
    conn = sqlite3.connect(settings.SQL_LITE_DB_PATH)
    try:
        cursor = conn.cursor()
        # get the count of tables with the name
        tablename = "SENT"
        cursor.execute(
            "SELECT count(name) FROM sqlite_master WHERE type='table' AND name=? ",
            (tablename,),
        )
        if cursor.fetchone()[0] == 1:
            logger.info("Table to track messages sent exists.")
            pass
        else:
            logger.info("Table to track messages sent does not exist. Creating it.")
            cursor.execute(
                """create table SENT (
                    profile_id INT not null, 
                    sent_at CHAR(140));"""
            )
            cursor.execute(
                """
                    create index idx_profile_sent on SENT (profile_id, sent_at);"""
            )
        conn.commit()
    finally:
        conn.close()


async def main():
    check_if_table_exists()
    parsed_results = []
    raw_results = []
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.set_viewport_size({"width": 800, "height": 650})
        await page.set_extra_http_headers(
            {
                "User-Agent": settings.USER_AGENT,
                "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7,la;q=0.6",
            }
        )
        await page.goto(
            url=settings.DOCTOLIB_SEARCH_URL,
        )
        page.on(
            "response",
            lambda x: asyncio.ensure_future(
                parse_response(x, parsed_results, raw_results)
            ),
        )
        while True:
            await scroll(page)


def export_parsed_results(results):
    with open("parsed_results.json", "a+") as f:
        json.dump(results, f)
        f.write(os.linesep)


def export_raw_results(results):
    with open("raw_results.json", "a+") as f:
        json.dump(results, f)
        f.write(os.linesep)


async def parse_response(response: Response, parsed_results, raw_results):
    if "https://www.doctolib.fr/search_results" in response.url:
        data = await response.json()
        center_name = data.get("search_result", {}).get("last_name")
        if data.get("total", 0) > 0:
            export_raw_results(data)
            if data.get("availabilities", []):
                availabilities = data.get("availabilities", [])
                availabilities = [i for i in availabilities if i["slots"]]
                if availabilities:
                    if (
                        any(
                            [
                                data["search_result"]["zipcode"].startswith(i)
                                for i in settings.ALLOWED_ZIPCODES
                            ]
                        )
                        or not settings.ALLOWED_ZIPCODES
                    ):
                        logger.info(
                            f"🚨 Appointment(s) found for center {center_name}"
                            f'link to book: https://www.doctolib.fr/{data["search_result"]["url"]}'
                        )
                        send_alert(
                            [
                                {
                                    "name": center_name,
                                    "url": f'https://www.doctolib.fr{data["search_result"]["url"]}',
                                    "starts": availabilities,
                                    "profile_id": data["search_result"]["profile_id"],
                                    "address": f'{data["search_result"]["address"]}, {data["search_result"]["zipcode"]}, {data["search_result"]["city"]}',
                                }
                            ]
                        )
                    else:
                        logger.info(
                            f'Zipcode {data["search_result"]["zipcode"]} not allowed!'
                        )
        else:
            logger.info(f"No availabilities for {center_name}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s :: %(levelname)s :: %(message)s')
    asyncio.run(main())
