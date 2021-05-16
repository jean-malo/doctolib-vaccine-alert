import asyncio
import json
import os

from playwright.async_api import Response
from playwright.async_api import async_playwright

from . import settings
from .alert import send_alert


async def scroll(page):
    print("Scrolling")
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
    await asyncio.sleep(2)
    await page.evaluate("window.scrollTo(0, 0);")
    await page.reload()


async def main():
    with open("parsed_results.json", "w"):
        pass
    with open("raw_results.json", "w"):
        pass
    parsed_results = []
    raw_results = []
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.set_viewport_size({"width": 800, "height": 650})
        await page.set_extra_http_headers(
            {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
                "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7,la;q=0.6",
            }
        )
        await page.goto(
            url="https://www.doctolib.fr/vaccination-covid-19/paris-75001?page=1&ref_visit_motive_ids[]=6970&ref_visit_motive_ids[]=7005&force_max_limit=2",
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
                                for i in settings.ZIPCODE_WHITE_LIST
                            ]
                        )
                        or not settings.ZIPCODE_WHITE_LIST
                    ):
                        print(
                            f"🚨 Appointment(s) found for center {center_name}"
                            f'link to book: https://www.doctolib.fr/{data["search_result"]["url"]}'
                        )
                        send_alert(
                            [
                                {
                                    "name": center_name,
                                    "url": f'https://www.doctolib.fr/{data["search_result"]["url"]}',
                                    "starts": availabilities,
                                    "profile_id": data["search_result"]["profile_id"],
                                    "address": f'{data["search_result"]["address"]}, {data["search_result"]["zipcode"]}, {data["search_result"]["city"]}',
                                }
                            ]
                        )
                    else:
                        print(
                            f'Zipcode {data["search_result"]["zipcode"]} not allowed!'
                        )
        else:
            print(f"No availabilities for {center_name}")


asyncio.run(main())
