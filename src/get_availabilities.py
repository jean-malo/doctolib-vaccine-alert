import asyncio
import datetime
import urllib
from urllib.parse import urlparse

from aiohttp import ClientSession, ClientConnectorError, ContentTypeError

from src.alert import send_alert


async def parse_center_availability(
    url: str, session: ClientSession, center, center_name
) -> tuple:
    try:
        resp = await session.request(method="GET", url=url)
        data = await resp.json()
        if data["total"] > 1:
            if data.get("availabilities", []):
                availabilities = data.get("availabilities", [])
                availabilities = [i for i in availabilities if i["slots"]]
                if availabilities:
                    print(
                        f"🚨 {datetime.datetime.now().isoformat()}: Appointment(s) found for center {center_name}"
                        f"link to book: {center['full_url']}"
                    )
                    send_alert(
                        [
                            {
                                "name": center_name,
                                "url": center["full_url"],
                                "starts": availabilities,
                                "profile_id": center["practice_ids"],
                                "address": center["address"],
                            }
                        ]
                    )
        else:
            print(f"No availabilities for {center_name}")
    except (ClientConnectorError, ContentTypeError) as e:
        print(e)
        return url, 404
    return url, resp.status


async def check_centers_availability(centers) -> None:
    start_date = datetime.datetime.now().isoformat()
    async with ClientSession() as session:
        tasks = []
        for center in centers:
            center_name = center["name"]
            params = {
                "start_date": start_date,
                "visit_motive_ids": center["motive_ids"],
                "agenda_ids": center["agenda_ids"],
                "practice_ids": center["practice_ids"],
                "insurance_sector": "public",
                "destroy_temporary": "true",
                "limit": 2,
            }
            url = (
                "https://www.doctolib.fr/availabilities.json?"
                + urllib.parse.urlencode(params)
            )
            tasks.append(
                parse_center_availability(
                    url=url, session=session, center=center, center_name=center_name
                )
            )
        await asyncio.gather(*tasks)
