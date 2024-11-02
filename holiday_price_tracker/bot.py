import asyncio
import os
import signal

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from dotenv import load_dotenv
from playwright.async_api import async_playwright

from holiday_price_tracker.database import Database
from holiday_price_tracker.logger import setup_logger
from holiday_price_tracker.models import Tour

load_dotenv()

logger = setup_logger()

API_TOKEN = os.getenv("TELEGRAM_API_TOKEN")
bot = Bot(token=API_TOKEN)
dp = Dispatcher()
db = Database()


async def get_tour_details(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False
        )  # TODO: change to True, fix the behaviour
        page = await browser.new_page()
        await page.set_extra_http_headers(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
                    AppleWebKit/537.36 (KHTML, like Gecko) \
                        Chrome/122.0.0.0 Safari/537.36",
                "Accept-Language": "en-US,en;q=0.9",
            }
        )
        await page.goto(url, wait_until="networkidle", timeout=60000)

        await page.wait_for_selector(".ProgressbarNavigation__perPerson")

        currency = await page.query_selector(".ProgressbarNavigation__currency")
        part1 = await page.query_selector(".ProgressbarNavigation__ppPart1")
        part2 = await page.query_selector(".ProgressbarNavigation__ppPart2")

        price = f"{await currency.inner_text()} \
            {await part1.inner_text()}.{await part2.inner_text()}"
        hotel_name_element = await page.query_selector(
            ".Header__headerTitle.Header__skiSignature span"
        )
        hotel_name = (
            await hotel_name_element.get_attribute("text")
            if hotel_name_element
            else "Unknown"
        )
        location_element = await page.query_selector(
            ".Header__locationBreadCrumb.Header__skiAccomLocation span"
        )
        location = (
            await location_element.get_attribute("text")
            if location_element
            else "Unknown"
        )
        await browser.close()
        return price, hotel_name, location


@dp.message(Command("start"))
async def start(message: types.Message):
    logger.info(f"User {message.from_user.id} started the bot")
    await message.reply("Hello! Send me a link to the tour to track its price.")


@dp.message(lambda message: message.text.startswith("http"))
async def add_tour_handler(message: types.Message):
    url = message.text.strip()
    chat_id = message.chat.id
    price, hotel_name, location = await get_tour_details(url)
    if price is not None:
        tour = Tour(url, chat_id, price, hotel_name, location)
        db = Database()
        db.add_tour(tour)
        logger.info(f"Tour added: {hotel_name} in {location} with price {price}")
        await message.reply(
            f"Tour added: {hotel_name} in {location} with price {price}"
        )
    else:
        logger.error(f"Failed to get tour data for {url}")
        await message.reply("Failed to get tour data.")


@dp.message(Command("stop"))
async def stop_tracking(message: types.Message):
    url = message.get_args()
    db.remove_tour(url)
    logger.info(f"Tour removed: {url}")
    await message.reply(f"Stopped tracking tour: {url}")


@dp.message(Command("list"))
async def list_tours(message: types.Message):
    tours = db.get_all_tours()
    if not tours:
        logger.info("No tracked tours.")
        await message.reply("No tracked tours.")
        return

    response = "Tracked tours:\n"
    for tour in tours:
        response += f"- {tour.url} (Price: {tour.price})\n"
    await message.reply(response)


async def check_prices():
    while True:
        tours = db.get_all_tours()
        for tour in tours:
            new_price = get_tour_details(tour.url)
            if new_price and new_price != tour.price:
                db.update_price(tour.url, new_price)
                logger.info(f"Tour price has been updated: {new_price} for {tour.url}")
                await bot.send_message(
                    tour.chat_id,
                    f"Tour price has been updated: {new_price}\nLink: {tour.url}",
                )
        await asyncio.sleep(3600)


if __name__ == "__main__":

    async def main():
        stop_event = asyncio.Event()

        def signal_handler():
            stop_event.set()

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        async def check_prices_with_stop():
            while not stop_event.is_set():
                tours = db.get_all_tours()
                for tour in tours:
                    if stop_event.is_set():
                        break
                    new_price = await get_tour_details(tour.url)
                    if new_price and new_price != tour.price:
                        db.update_price(tour.url, new_price)
                        logger.info(
                            f"Tour price has been updated: {new_price} for {tour.url}"
                        )
                        await bot.send_message(
                            tour.chat_id,
                            f"Tour price has been updated: \
                                {new_price}\nLink: {tour.url}",
                        )
                if not stop_event.is_set():
                    await asyncio.sleep(3600)

        try:
            await asyncio.gather(
                check_prices_with_stop(), dp.start_polling(bot), return_exceptions=True
            )
        finally:
            await bot.session.close()
            logger.info("Bot successfully stopped")

    asyncio.run(main())
