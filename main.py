import discord
from discord.ext import commands
import json
import yaml
import logging
import os
import sys
import aiohttp
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

# 載入 .env
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    logging.critical("BOT_TOKEN not found in .env file")
    sys.exit(1)

# 設定 Intents
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)


class DataManager:
    def __init__(self):
        self.balance = self.load_json("economy/balance.json", {})
        self.blackjack_data = self.load_json("config/blackjack_data.json", {})
        self.invalid_bet_count = self.load_json("config/invalid_bet_count.json", {})
        self.bot_status = self.load_json(
            "config/bot_status.json",
            {"disconnect_count": 0, "reconnect_count": 0, "last_event_time": None}
        )

    @staticmethod
    def load_json(file, default=None):
        if default is None:
            default = {}
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
    def load_yaml(file, default=None):
        if default is None:
            default = {}
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


async def setup_bot():
    bot.data_manager = DataManager()
    bot.session = aiohttp.ClientSession()
    logging.info("Initialized DataManager and ClientSession")


@bot.event
async def on_close():
    """確保關閉 bot 時清理資源"""
    if hasattr(bot, "session"):
        await bot.session.close()


# 強制檢查 LICENSE
def check_license():
    license_file = os.path.join(os.path.dirname(__file__), "LICENSE")
    if not os.path.exists(license_file):
        logging.error("LICENSE file missing! The bot cannot start without a valid LICENSE.")
        exit(1)

    with open(license_file, "r", encoding="utf-8") as f:
        content = f.read()
        if "GNU GENERAL PUBLIC LICENSE" not in content:
            logging.error("Invalid LICENSE content! Please include the original GPL-3.0 license.")
            exit(1)

# 載入 commands/ 與 events/
def load_extensions():
    for folder, prefix in [("./commands", "commands"), ("./events", "events")]:
        if not os.path.exists(folder):
            continue
        for filename in os.listdir(folder):
            if filename.endswith(".py") and not filename.startswith("__"):
                try:
                    bot.load_extension(f"{prefix}.{filename[:-3]}")
                    logging.info(f"Loaded module: {prefix}.{filename[:-3]}")
                except Exception as e:
                    logging.error(f"Failed to load module {prefix}.{filename[:-3]}: {e}")


if __name__ == "__main__":
    check_license()
    bot.loop.run_until_complete(setup_bot())  # 取代 asyncio.run()
    load_extensions()
    try:
        bot.run(TOKEN)
    except KeyboardInterrupt:
        logging.info("Bot stopped manually.")
