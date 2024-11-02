# Holiday Price Tracker Bot

This is a Telegram bot application designed to track holiday prices, hotel names, and locations from a specified URL. The bot uses Playwright for web scraping and aiogram for Telegram bot interactions.

## Features

- **Track Holiday Prices**: Automatically fetches and updates holiday prices from specified URLs.
- **Hotel and Location Information**: Extracts and stores hotel names and locations.
- **Telegram Integration**: Interact with the bot via Telegram to add or remove tours.
- **Logging**: Logs all significant actions and errors for easy debugging and monitoring.

## Requirements

- Python 3.8+
- [Poetry](https://python-poetry.org/) for dependency management

## Installation

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
   poetry run playwright install
   ```

4. **Set up your Telegram bot**:

   - Create a new bot using [BotFather](https://core.telegram.org/bots#botfather) on Telegram.
   - Obtain your bot token.

5. **Configure the application**:

   - Update the bot token in your application code.

## Usage

1. **Run the bot**:

   ```bash
   poetry run python holiday_price_tracker/bot.py
   ```

2. **Interact with the bot**:

   - Use `/start` or `/help` to get started.
   - Send a URL to track a holiday tour.

## Logging

- Logs are stored in `holiday_price_tracker.log`.
- Logs include information about added or removed tours and command executions.

## Contributing

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Commit your changes (`cz commit`).
4. Push to the branch (`git push origin feature-branch`).
5. Create a new Pull Request.
