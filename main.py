import discord
from discord.ext import commands
import json
import yaml
import logging
import os
import aiohttp
import asyncio
from dotenv import load_dotenv

# 設定日誌
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(filename='logs/main-error.log', encoding='utf-8', mode='a'),
        logging.StreamHandler()
    ]
)

# 載入 .env 檔案
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    logging.error("BOT_TOKEN not found in .env file")
    exit(1)

# 設定必要的 Intents
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

class DataManager:
    def __init__(self):
        self.balance = self.load_json("economy/balance.json")
        self.blackjack_data = self.load_json("config/blackjack_data.json")
        self.invalid_bet_count = self.load_json("config/invalid_bet_count.json")
        self.bot_status = self.load_json("config/bot_status.json", {"disconnect_count": 0, "reconnect_count": 0, "last_event_time": None})

    @staticmethod
    def load_json(file, default={}):
        try:
            with open(file, "r", encoding="utf-8") as f:
                return json.load(f) or default
        except Exception as e:
            logging.error(f"Failed to load JSON file {file}: {e}")
            return default

    @staticmethod
    def save_json(file, data):
        try:
            os.makedirs(os.path.dirname(file), exist_ok=True)
            with open(file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            logging.error(f"Failed to save JSON file {file}: {e}")

    @staticmethod
    def load_yaml(file, default={}):
        try:
            with open(file, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or default
        except Exception as e:
            logging.error(f"Failed to load YAML file {file}: {e}")
            return default

    def save_all(self):
        self.save_json("economy/balance.json", self.balance)
        self.save_json("config/blackjack_data.json", self.blackjack_data)
        self.save_json("config/invalid_bet_count.json", self.invalid_bet_count)
        self.save_json("config/bot_status.json", self.bot_status)

# 將 DataManager 和 aiohttp.ClientSession 附加到 bot
async def setup_bot():
    bot.data_manager = DataManager()
    bot.session = aiohttp.ClientSession()
    logging.info("Initialized DataManager and ClientSession")

# 載入 commands/
for filename in os.listdir('./commands'):
    if filename.endswith('.py') and filename != '__init__.py':
        try:
            bot.load_extension(f'commands.{filename[:-3]}')
            logging.info(f"Loaded command module: commands.{filename[:-3]}")
        except Exception as e:
            logging.error(f"Failed to load command module commands.{filename[:-3]}: {e}")

# 載入 events/
for filename in os.listdir('./events'):
    if filename.endswith('.py') and filename != '__init__.py':
        try:
            bot.load_extension(f'events.{filename[:-3]}')
            logging.info(f"Loaded event module: events.{filename[:-3]}")
        except Exception as e:
            logging.error(f"Failed to load event module events.{filename[:-3]}: {e}")

# 啟動 bot
if __name__ == "__main__":
    asyncio.run(setup_bot())
    bot.run(TOKEN)