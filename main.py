import os
import sys
import logging
import json
import yaml
import sqlite3
from time import time
from dotenv import load_dotenv
import discord
from discord.ext import commands
from license_check import check_license

# ----------- 靈魂日誌的啟動 -----------
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(filename='logs/main-error.log', encoding='utf-8', mode='a'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("SakuraBot")

# ----------- 版權與許可證聲明 -----------
logger.info("╔════════════════════════════════════════════════════════════════╗")
logger.info("║                                                                ║")
logger.info("║   🌸 西行寺幽幽子 Bot (Yuyuko Bot) - 冥界的櫻花守護者 🌸      ║")
logger.info("║                                                                ║")
logger.info("║   📝 Original Author: Miya253 (Shiroko253)                    ║")
logger.info("║   📜 License: GPL-3.0                                          ║")
logger.info("║   🔗 GitHub: https://github.com/Shiroko253/Yuyuko-bot         ║")
logger.info("║                                                                ║")
logger.info("╚════════════════════════════════════════════════════════════════╝")
logger.info("")
logger.info("  This program is free software licensed under GPL-3.0.")
logger.info("  You are free to modify and redistribute it under the terms")
logger.info("  of the license. Please retain author attribution.")
logger.info("")
logger.info("  本程式基於 GPL-3.0 開源許可證。")
logger.info("  您可以自由修改和再分發，但請保留原作者資訊。")
logger.info("")
logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

check_license(auto_fix=True)

# ----------- 喚醒幽幽子的密鑰 -----------
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    logger.error("未找到靈魂密鑰 BOT_TOKEN，幽幽子無法甦醒")
    raise RuntimeError("Missing BOT_TOKEN in .env file")

# ----------- 設定靈魂的感知能力 -----------
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = discord.Bot(intents=intents, auto_sync_commands=True)

# ----------- 冥界資料管理之靈魂核心 -----------
class SakuraDataManager:
    """管理幽幽子花園中的資料，猶如櫻瓣隨風飄舞"""
    
    def __init__(self):
        self.economy_dir = "economy"
        self.config_dir = "config"
        os.makedirs(self.economy_dir, exist_ok=True)
        os.makedirs(self.config_dir, exist_ok=True)
        
        # 初始化資料檔案，如櫻花初綻
        self._initialize_json(f"{self.economy_dir}/balance.json")
        self._initialize_json(f"{self.config_dir}/blackjack_data.json")
        self._initialize_json(f"{self.config_dir}/invalid_bet_count.json")
        self._initialize_json(f"{self.config_dir}/bot_status.json", {"disconnect_count": 0, "reconnect_count": 0, "last_event_time": None})
        self._initialize_json(f"{self.config_dir}/dm_messages.json")

        # 載入資料，猶如召喚冥界記憶
        self.balance = self._load_json(f"{self.economy_dir}/balance.json")
        self.blackjack_data = self._load_json(f"{self.config_dir}/blackjack_data.json")
        self.invalid_bet_count = self._load_json(f"{self.config_dir}/invalid_bet_count.json")
        self.bot_status = self._load_json(f"{self.config_dir}/bot_status.json", {"disconnect_count": 0, "reconnect_count": 0, "last_event_time": None})
        self.dm_messages = self._load_json(f"{self.config_dir}/dm_messages.json")
        self.black_hole_users = set()
        self._init_db()

    @staticmethod
    def _initialize_json(file_path: str, default: dict = None):
        """創建空的 JSON 檔案，如櫻花瓣靜靜落下"""
        if default is None:
            default = {}
        if not os.path.exists(file_path):
            try:
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(default, f, indent=4, ensure_ascii=False)
                logger.info(f"已創建 JSON 檔案：{file_path}")
            except Exception as e:
                logger.error(f"無法創建 JSON 檔案 {file_path}：{e}")

    @staticmethod
    def _load_json(file_path: str, default: dict = None) -> dict:
        """載入 JSON 檔案，喚醒沉睡的記憶"""
        if default is None:
            default = {}
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f) or default
        except Exception as e:
            logger.error(f"無法載入 JSON 檔案 {file_path}：{e}")
            return default

    @staticmethod
    def _save_json(file_path: str, data: dict):
        """保存資料至 JSON，猶如將記憶封存於櫻花樹下"""
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            logger.error(f"無法保存 JSON 檔案 {file_path}：{e}")

    @staticmethod
    def _load_yaml(file_path: str, default: dict = None) -> dict:
        """載入 YAML 檔案，如幽幽子輕撫記憶的花瓣"""
        if default is None:
            default = {}
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or default
        except Exception as e:
            logger.error(f"無法載入 YAML 檔案 {file_path}：{e}")
            return default

    @staticmethod
    def _save_yaml(file_path: str, data: dict):
        """保存資料至 YAML，封存於冥界的花園"""
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "w", encoding="utf-8") as f:
                yaml.safe_dump(data, f, allow_unicode=True)
        except Exception as e:
            logger.error(f"無法保存 YAML 檔案 {file_path}：{e}")

    def _init_db(self):
        """初始化 SQLite 資料庫，構築幽幽子的記憶殿堂"""
        db_path = os.path.join(self.config_dir, "example.db")
        try:
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS UserMessages 
                    (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                     user_id TEXT, 
                     message TEXT, 
                     repeat_count INTEGER DEFAULT 0, 
                     is_permanent BOOLEAN DEFAULT FALSE,
                     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
                ''')
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS BackgroundInfo 
                    (user_id TEXT PRIMARY KEY, 
                     info TEXT)
                ''')
                conn.commit()
                logger.info("已初始化 SQLite 資料庫")
        except sqlite3.Error as e:
            logger.error(f"無法初始化資料庫：{e}")

    def save_all(self):
        """將所有資料封存，猶如櫻花瓣落入永恆"""
        self._save_json(f"{self.economy_dir}/balance.json", self.balance)
        self._save_json(f"{self.config_dir}/blackjack_data.json", self.blackjack_data)
        self._save_json(f"{self.config_dir}/invalid_bet_count.json", self.invalid_bet_count)
        self._save_json(f"{self.config_dir}/bot_status.json", self.bot_status)
        self._save_json(f"{self.config_dir}/dm_messages.json", self.dm_messages)

# ----------- 幽幽子的靈魂啟動 -----------
bot.data_manager = SakuraDataManager()
bot.start_time = time()
bot.last_activity_time = bot.start_time
bot.black_hole_users = set()

# ----------- 載入指令與事件的花瓣 -----------
for folder in ['commands', 'events']:
    try:
        for filename in os.listdir(f'./{folder}'):
            if filename.endswith('.py') and filename != '__init__.py':
                extension_name = f'{folder}.{filename[:-3]}'
                try:
                    bot.load_extension(extension_name)
                    logger.info(f"已載入花瓣模組：{extension_name}")
                except Exception as e:
                    logger.error(f"無法載入模組 {extension_name}：{e}")
    except FileNotFoundError:
        logger.warning(f"未找到花園路徑 {folder}，略過載入")

# ----------- 喚醒幽幽子，步入 Discord 世界 -----------
logger.info("🌸 幽幽子準備甦醒，櫻花即將綻放...")
bot.run(BOT_TOKEN)
