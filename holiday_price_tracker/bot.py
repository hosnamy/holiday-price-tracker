import asyncio
import os

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from dotenv import load_dotenv
from playwright.async_api import async_playwright

from holiday_price_tracker.logger import setup_logger

load_dotenv()

logger = setup_logger()

API_TOKEN = os.getenv("TELEGRAM_API_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
bot = Bot(token=API_TOKEN)
dp = Dispatcher()


async def get_tour_details(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.set_extra_http_headers(
            {
                "sec-ch-ua-platform": '"Windows"',
                "accept-language": "en-US,en;q=0.5",
                "sec-ch-ua": '"Not?A_Brand";v="99", "Chromium";v="130"',
                "sec-ch-ua-mobile": "?0",
                "accept-encoding": "gzip, deflate, br",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
                    AppleWebKit/537.36 (KHTML, like Gecko) \
                        Chrome/122.0.0.0 Safari/537.36",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,\
                    image/webp,*/*;q=0.8",
            }
        )
        try:
            await page.goto(url, wait_until="networkidle", timeout=60000)
        except Exception as e:
            logger.error(f"Error navigating to {url}: {e}")
            await browser.close()
            return None, None, None
        try:
            await page.wait_for_selector(".ProgressbarNavigation__perPerson")
        except Exception as e:
            logger.error(f"Error waiting for selector: {e}")
            await browser.close()
            return None, None, None

        try:
            currency = await page.query_selector(".ProgressbarNavigation__currency")
            part1 = await page.query_selector(".ProgressbarNavigation__ppPart1")
            part2 = await page.query_selector(".ProgressbarNavigation__ppPart2")

            price = f"{await currency.inner_text()} \
                {await part1.inner_text()}.{await part2.inner_text()}"
        except Exception as e:
            logger.error(f"Error getting price: {e}")
            await browser.close()
            return None, None, None

        try:
            hotel_name_element = await page.query_selector(
                ".Header__headerTitle.Header__skiSignature span"
            )
            hotel_name = (
                await hotel_name_element.get_attribute("text")
                if hotel_name_element
                else "Unknown"
            )
        except Exception as e:
            logger.error(f"Error getting hotel name: {e}")
            await browser.close()
            return None, None, None

        try:
            location_element = await page.query_selector(
                ".Header__locationBreadCrumb.Header__skiAccomLocation span"
            )
            location = (
                await location_element.get_attribute("text")
                if location_element
                else "Unknown"
            )
        except Exception as e:
            logger.error(f"Error getting location: {e}")
            await browser.close()
            return None, None, None

        await browser.close()
        return price, hotel_name, location


async def get_tours_from_env():
    tours_str = os.getenv("TOURS_LIST", "")
    tours_list = tours_str.split(",")

    results = []
    for url in tours_list:
        price, hotel_name, location = await get_tour_details(url)
        results.append(
            {"url": url, "price": price, "hotel_name": hotel_name, "location": location}
        )
    return results


async def send_results_to_telegram(results):
    for result in results:
        message = (
            f"*URL:* {result['url']}\n"
            f"*Hotel:* {result['hotel_name']}\n"
            f"*Location:* {result['location']}\n"
            f"*Price:* {result['price']}"
        )
        try:
            await bot.send_message(CHAT_ID, message, parse_mode=ParseMode.MARKDOWN)
            await bot.session.close()
        except Exception as e:
            logger.error(f"Error sending message: {e}")


if __name__ == "__main__":

    async def main():
        results = await get_tours_from_env()
        await send_results_to_telegram(results)

    asyncio.run(main())
