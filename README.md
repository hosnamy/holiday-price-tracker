# Holiday Price Tracker Bot

This is a Telegram bot application designed to track holiday prices, hotel names, and locations from a specified URL. The bot uses Playwright for web scraping and aiogram for Telegram bot interactions.

## Features

- **Track Holiday Prices**: Automatically fetches and updates holiday prices from specified URLs.
- **Hotel and Location Information**: Extracts and stores hotel names and locations.
- **Telegram Integration**: Send messages to a Telegram chat when prices change.
- **Logging**: Logs all significant actions and errors for easy debugging and monitoring.

## Requirements

- Python 3.8+
- [Poetry](https://python-poetry.org/) for dependency management
- [Docker](https://www.docker.com/) for containerization

## Logging

- Logs are stored in `holiday_price_tracker.log`.
- Logs include information about added or removed tours and command executions.

## Contributing

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Commit your changes (`cz commit`).
4. Push to the branch (`git push origin feature-branch`).
5. Create a new Pull Request.

## Setup

1. **Clone the repository**:

   ```bash
   git clone https://github.com/hosnamy/holiday-price-tracker.git
   cd holiday-price-tracker
   ```

2. **Install dependencies**:

   ```bash
   poetry install
   ```

3. **Install Playwright browsers**:

   ```bash
   poetry run playwright install chromium
   ```

4. **Set up Telegram bot**:

   - Create a new bot using [BotFather](https://core.telegram.org/bots#botfather) on Telegram
   - Get your bot token
   - To get your CHAT_ID:
     1. Send any message to your bot
     2. Go to `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates`
     3. Find the `"chat":{"id":` value in the returned JSON - this is your CHAT_ID

5. **Configure the application**:

   - Create a `.env` file in the root directory with:
     ```
     TELEGRAM_API_TOKEN="your_bot_token"
     TELEGRAM_CHAT_ID="your_chat_id"
     ```
   - Create a `urls.yml` file with the URLs you want to track:
     ```yaml
     urls:
       - https://www.example.com/tour1
       - https://www.example.com/tour2
     ```
