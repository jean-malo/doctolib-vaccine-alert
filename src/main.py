import asyncio

from src import settings
from src.get_availabilities import check_centers_availability
from src.scrape_centers import launch_centers_scraper
from src.utils import check_if_table_exists, get_centers, get_centers_filename


async def main():
    check_if_table_exists()
    try:
        centers = get_centers()
        if len(centers) < 2:
            print(
                f"Not enough centers in {get_centers_filename()}. Will fetch them before running again"
            )
            launch_centers_scraper()
    except Exception as e:
        print(e)
        print("Centers file does not exist. Will fetch them again before running again")
        launch_centers_scraper()
    centers = get_centers()
    while True:
        await check_centers_availability(centers)
        print(f"Waiting for {settings.RATE_LIMIT} seconds")
        await asyncio.sleep(settings.RATE_LIMIT)


if __name__ == "__main__":
    asyncio.run(main())
