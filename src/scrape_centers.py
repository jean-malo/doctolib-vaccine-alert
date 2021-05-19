import json
import re
from urllib.parse import urlparse, parse_qs

import requests
from bs4 import BeautifulSoup

from src import settings
from src.utils import check_if_table_exists, get_centers_filename


def launch_centers_scraper():
    page = 1
    check_if_table_exists()
    headers = {
        "User-Agent": settings.USER_AGENT,
        "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7,la;q=0.6",
    }
    url = urlparse(settings.DOCTOLIB_SEARCH_URL)
    params = parse_qs(url.query)
    centers = []
    for i in range(20):
        print(i)
        try:
            results = paginate_search_results(headers, page, params)
        except SearchEnded:
            break
        centers.extend(results)
        page += 1
    save_results(centers)
    return centers

class SearchEnded(Exception):
    pass

def paginate_search_results(headers, page, params):
    results = []
    page += 1
    params["page"] = [str(page)]
    r = requests.get(settings.DOCTOLIB_SEARCH_URL, headers=headers, params=params)
    r.raise_for_status()
    json_data = BeautifulSoup(r.text, features="lxml").find(
        "script", text=re.compile("PostalAddress")
    )
    if not json_data:
        print(f'No more centers for page {page}')
        raise SearchEnded()
    parsed_profiles = json.loads(json_data.contents[0])
    for profile in parsed_profiles:
        print(profile['address']['name'])
        if not (
            any(
                [
                    profile["address"]["postalCode"].startswith(i)
                    for i in settings.ALLOWED_ZIPCODES
                ]
            )
            or not settings.ALLOWED_ZIPCODES
        ):
            print(f"{profile['address']['postalCode']} blacklisted")
            continue
        center_details = fetch_center_details(profile["url"], headers)
        if center_details:
            results.append(center_details)
    return results

def fetch_center_details(url, headers):
    profile_id = urlparse(url).path.split("/")[-1]
    print(f"Fetching center {profile_id}")
    r = requests.get(
        f"https://www.doctolib.fr/booking/{profile_id}.json", headers=headers
    )
    r.raise_for_status()
    booking_data = r.json()["data"]
    booking_data["places"] = [
        p
        for p in booking_data["places"]
        if p["zipcode"]
        if any([p["zipcode"].startswith(i) for i in settings.ALLOWED_ZIPCODES])
        or not settings.ALLOWED_ZIPCODES
    ]
    if not booking_data["places"]:
        return None
    motives = [
        visit_motive
        for visit_motive in booking_data["visit_motives"]
        if "1re injection" in visit_motive["name"]
        and "AstraZeneca" not in visit_motive["name"]
    ]
    if not motives:
        return None
    for place in booking_data["places"]:
        visit_motive_ids = motives[0]["id"]
        practice_ids = place["practice_ids"][0]
        agendas = [
            agenda
            for agenda in booking_data["agendas"]
            if agenda["practice_id"] == practice_ids
            and not agenda["booking_disabled"]
            and visit_motive_ids in agenda["visit_motive_ids"]
        ]
        agenda_ids = "-".join([str(agenda["id"]) for agenda in agendas])
        if not agenda_ids:
            continue
        return {
            "id": profile_id,
            "name": booking_data["profile"]["name_with_title_and_determiner"],
            "address": place["full_address"],
            "full_url": f"https://www.doctolib.fr{url}?highlight[speciality_ids][]={motives[0].get('speciality_id', '5494')}",
            "motive_ids": visit_motive_ids,
            "practice_ids": practice_ids,
            "agenda_ids": agenda_ids,
            "place": place,
        }


def save_results(results):
    with open(get_centers_filename(), "w") as f:
        json.dump(results, f)
