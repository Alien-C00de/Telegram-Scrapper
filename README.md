# Telegram Scraper - Using Python

The Telegram Scraper is a robust tool designed to extract detailed information from Telegram users, channels, and groups, and compile it into a convenient CSV format. This utility is perfect for data analysts and researchers looking to gather insights from Telegram's vast user network.

## Features

- Retrieve personal Telegram user information.
- Collect data from channels/groups including all participant details.
- Display basic details of groups and individual users on the screen.
- Save chat and participant data into CSV files for easy analysis.

## Installation

### Prerequisites

You must have a Telegram API ID and API HASH to run this program. Create your own using the following link and insert them into the `config.ini` file:

https://telegram-spam-master.com/en/telegram-api-id-and-hash.html

- Telegram API ID and HASH

### Required Libraries

Install the following libraries to ensure the scraper runs smoothly:

```bash
pip install Telethon
pip install configparser
pip install beautifulsoup4
pip install requests
```
## Usage

Execute the tool with the following commands based on your data retrieval needs:

- To scrape data from groups you are associated with:
   ```bash
   python telegram_scrapper.py -m self
   ```
![image](https://github.com/Alien-C00de/Telegram-Scrapper/assets/138598543/17a9ef03-d0e9-43aa-a3d5-d2ad4271a891)
- To display basic details of a group on the screen:
   ```bash
   python telegram_scrapper.py -b durov
   ```
![image](https://github.com/Alien-C00de/Telegram-Scrapper/assets/138598543/ab37ca16-e4d1-4e80-8ef5-dc424556cb56)
- To collect group chat and participant data:
   ```bash
   python telegram_scrapper.py -i vikasjhahelloworld001
   ```
![image](https://github.com/Alien-C00de/Telegram-Scrapper/assets/138598543/a6ba4a1a-be1b-4908-9c08-2033ea40602d)
- To display user details on the screen:
   ```bash
   python telegram_scrapper.py -u @bishkumar
   ```
![image](https://github.com/Alien-C00de/Telegram-Scrapper/assets/138598543/4b48b934-cdf0-499b-9c9c-4c80cd35cc54)

## Output

The scraper generates CSV files containing the extracted data, which can be found in the designated output directory.

📨 Happy Telegram scraping! 🚀
