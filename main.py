import os
import sys
import logging
import json
import yaml
import sqlite3
from dotenv import load_dotenv
import discord
from discord.ext import commands

from license_check import check_license  # <-- 加入這行

# ----------- 日誌設定 -----------
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(filename='logs/main-error.log', encoding='utf-8', mode='a'),
        logging.StreamHandler()
    ]
)

# ----------- LICENSE 檢查（最前面執行）-----------
check_license(auto_fix=True)   # <-- 這裡執行

# ----------- 載入 .env -----------
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    logging.error("BOT_TOKEN not found in .env file")
    raise RuntimeError("Missing BOT_TOKEN in .env file")

# ----------- 設定 Intents -----------
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = discord.Bot(intents=intents, auto_sync_commands=True)

# ----------- DataManager 資料管理 -----------
class DataManager:
    def __init__(self):
        self.economy_dir = "economy"
        self.config_dir = "config"
        os.makedirs(self.economy_dir, exist_ok=True)
        os.makedirs(self.config_dir, exist_ok=True)
        self.initialize_json(f"{self.economy_dir}/balance.json")
        self.initialize_json(f"{self.config_dir}/blackjack_data.json")
        self.initialize_json(f"{self.config_dir}/invalid_bet_count.json")
        self.initialize_json(f"{self.config_dir}/bot_status.json", {"disconnect_count": 0, "reconnect_count": 0, "last_event_time": None})
        self.initialize_json(f"{self.config_dir}/dm_messages.json")

        self.balance = self.load_json(f"{self.economy_dir}/balance.json")
        self.blackjack_data = self.load_json(f"{self.config_dir}/blackjack_data.json")
        self.invalid_bet_count = self.load_json(f"{self.config_dir}/invalid_bet_count.json")
        self.bot_status = self.load_json(f"{self.config_dir}/bot_status.json", {"disconnect_count": 0, "reconnect_count": 0, "last_event_time": None})
        self.dm_messages = self.load_json(f"{self.config_dir}/dm_messages.json")
        self.black_hole_users = set()
        self.init_db()

    @staticmethod
    def initialize_json(file, default=None):
        if default is None:
            default = {}
        if not os.path.exists(file):
            try:
                os.makedirs(os.path.dirname(file), exist_ok=True)
                with open(file, "w", encoding="utf-8") as f:
                    json.dump(default, f, indent=4, ensure_ascii=False)
                logging.info(f"Created empty JSON file: {file}")
            except Exception as e:
                logging.error(f"Failed to create JSON file {file}: {e}")

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

    @staticmethod
    def save_yaml(file, data):
        try:
            os.makedirs(os.path.dirname(file), exist_ok=True)
            with open(file, "w", encoding="utf-8") as f:
                yaml.safe_dump(data, f, allow_unicode=True)
        except Exception as e:
            logging.error(f"Failed to save YAML file {file}: {e}")

    def init_db(self):
        db_path = os.path.join(self.config_dir, "example.db")
        try:
            with sqlite3.connect(db_path) as conn:
                c = conn.cursor()
                c.execute('''CREATE TABLE IF NOT EXISTS UserMessages 
                             (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                              user_id TEXT, 
                              message TEXT, 
                              repeat_count INTEGER DEFAULT 0, 
                              is_permanent BOOLEAN DEFAULT FALSE,
                              created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
                c.execute('''CREATE TABLE IF NOT EXISTS BackgroundInfo 
                             (user_id TEXT PRIMARY KEY, 
                              info TEXT)''')
                conn.commit()
                logging.info("Initialized SQLite database")
        except sqlite3.Error as e:
            logging.error(f"Failed to initialize database: {e}")

    def save_all(self):
        self.save_json(f"{self.economy_dir}/balance.json", self.balance)
        self.save_json(f"{self.config_dir}/blackjack_data.json", self.blackjack_data)
        self.save_json(f"{self.config_dir}/invalid_bet_count.json", self.invalid_bet_count)
        self.save_json(f"{self.config_dir}/bot_status.json", self.bot_status)
        self.save_json(f"{self.config_dir}/dm_messages.json", self.dm_messages)

# ----------- 資源初始化 -----------
bot.data_manager = DataManager()
bot.start_time = __import__('time').time()
bot.last_activity_time = bot.start_time
bot.black_hole_users = set()

# ----------- 自動載入指令與事件 -----------
for folder in ['commands', 'events']:
    try:
        for filename in os.listdir(f'./{folder}'):
            if filename.endswith('.py') and filename != '__init__.py':
                ext_name = f'{folder}.{filename[:-3]}'
                try:
                    bot.load_extension(ext_name)
                    logging.info(f"Loaded {ext_name}")
                except Exception as e:
                    logging.error(f"Failed to load {ext_name}: {e}")
    except FileNotFoundError:
        logging.warning(f"Folder not found: {folder}, skip loading.")

# ----------- 啟動 Bot -----------
bot.run(TOKEN)
