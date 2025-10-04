import os
import sys
import logging
import json
import yaml
import sqlite3
from time import time
from dotenv import load_dotenv
import discord # pycord
from discord.ext import commands
import signal
import atexit
from typing import Dict, Any
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

check_license(auto_fix=True)

# ----------- 喚醒幽幽子的密鑰 -----------
load_dotenv()
BOT_TOKEN = os.getenv("TEST_BOT_TOKEN")
if not BOT_TOKEN:
    logger.error("未找到靈魂密鍵 BOT_TOKEN，幽幽子無法甦醒")
    sys.exit(1)  # [修復1級問題] 使用 sys.exit 而不是 raise

AUTHOR_ID = int(os.getenv("AUTHOR_ID", 0))

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
        self.db_path = os.path.join(self.config_dir, "data.db")  # [修復2級問題] 使用更明確的資料庫名稱
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
                raise  # [修復1級問題] 重新拋出異常

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
    def _save_json(file_path: str, data: Dict[str, Any]):
        """保存資料至 JSON，猶如將記憶封存於櫻花樹下"""
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            logger.error(f"無法保存 JSON 檔案 {file_path}：{e}")
            raise  # [修復2級問題] 保存失敗時拋出異常

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
    def _save_yaml(file_path: str, data: Dict[str, Any]):
        """保存資料至 YAML，封存於冥界的花園"""
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "w", encoding="utf-8") as f:
                yaml.safe_dump(data, f, allow_unicode=True)
        except Exception as e:
            logger.error(f"無法保存 YAML 檔案 {file_path}：{e}")

    def _init_db(self):
        """初始化 SQLite 資料庫，構築幽幽子的記憶殿堂"""
        try:
            with sqlite3.connect(self.db_path) as conn:  # [修復2級問題] 使用實例變量
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
                # 新增 BlockedUsers 表
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS BlockedUsers (
                        user_id TEXT PRIMARY KEY
                    )
                ''')
                conn.commit()
                logger.info("已初始化 SQLite 資料庫")
        except sqlite3.Error as e:
            logger.error(f"無法初始化資料庫：{e}")
            raise  # [修復1級問題] 資料庫初始化失敗時拋出異常

    # --- 黑名單相關 SQLite 操作 ---
    def _get_db_connection(self):
        """獲取資料庫連線，包含錯誤處理"""
        try:
            return sqlite3.connect(self.db_path)
        except sqlite3.Error as e:
            logger.error(f"無法建立資料庫連線：{e}")
            raise  # [修復1級問題] 連線失敗時拋出異常

    def get_blocked_users(self):
        """從 SQLite 讀取所有被封鎖的 user_id（回傳 set）"""
        try:
            with self._get_db_connection() as conn:  # [修復1級問題] 使用安全的連線方法
                c = conn.cursor()
                c.execute("CREATE TABLE IF NOT EXISTS BlockedUsers (user_id TEXT PRIMARY KEY)")
                c.execute("SELECT user_id FROM BlockedUsers")
                rows = c.fetchall()
                return set(row[0] for row in rows)
        except sqlite3.Error as e:
            logger.error(f"讀取封鎖用戶失敗：{e}")
            return set()  # [修復1級問題] 返回安全的默認值

    def add_blocked_user(self, user_id):
        """將 user_id 加入封鎖（字串型態）"""
        try:
            with self._get_db_connection() as conn:  # [修復1級問題] 使用安全的連線方法
                c = conn.cursor()
                c.execute("CREATE TABLE IF NOT EXISTS BlockedUsers (user_id TEXT PRIMARY KEY)")
                try:
                    c.execute("INSERT INTO BlockedUsers (user_id) VALUES (?)", (str(user_id),))
                    conn.commit()
                except sqlite3.IntegrityError:
                    pass  # 已存在
        except sqlite3.Error as e:
            logger.error(f"新增封鎖用戶失敗：{e}")
            raise  # [修復2級問題] 保存失敗時拋出異常

    def remove_blocked_user(self, user_id):
        """將 user_id 從封鎖表移除"""
        try:
            with self._get_db_connection() as conn:  # [修復1級問題] 使用安全的連線方法
                c = conn.cursor()
                c.execute("CREATE TABLE IF NOT EXISTS BlockedUsers (user_id TEXT PRIMARY KEY)")
                c.execute("DELETE FROM BlockedUsers WHERE user_id = ?", (str(user_id),))
                conn.commit()
        except sqlite3.Error as e:
            logger.error(f"移除封鎖用戶失敗：{e}")
            raise  # [修復2級問題] 保存失敗時拋出異常

    def is_user_blocked(self, user_id):
        """檢查 user_id 是否在封鎖表"""
        try:
            with self._get_db_connection() as conn:  # [修復1級問題] 使用安全的連線方法
                c = conn.cursor()
                c.execute("CREATE TABLE IF NOT EXISTS BlockedUsers (user_id TEXT PRIMARY KEY)")
                c.execute("SELECT 1 FROM BlockedUsers WHERE user_id = ?", (str(user_id),))
                return c.fetchone() is not None
        except sqlite3.Error as e:
            logger.error(f"檢查封鎖用戶失敗：{e}")
            return False  # [修復1級問題] 返回安全的默認值

    def save_all(self):
        """將所有資料封存，猶如櫻花瓣落入永恆"""
        try:
            self._save_json(f"{self.economy_dir}/balance.json", self.balance)
            self._save_json(f"{self.config_dir}/blackjack_data.json", self.blackjack_data)
            self._save_json(f"{self.config_dir}/invalid_bet_count.json", self.invalid_bet_count)
            self._save_json(f"{self.config_dir}/bot_status.json", self.bot_status)
            self._save_json(f"{self.config_dir}/dm_messages.json", self.dm_messages)
        except Exception as e:
            logger.error(f"保存所有資料失敗：{e}")
            raise  # [修復2級問題] 保存失敗時拋出異常

# ----------- 幽幽子的靈魂啟動 -----------
try:
    bot.data_manager = SakuraDataManager()
    bot.start_time = time()
    bot.last_activity_time = bot.start_time
except Exception as e:
    logger.error(f"資料管理器初始化失敗：{e}")
    sys.exit(1)  # [修復1級問題] 初始化失敗時退出

# [修復2級問題] 添加異常處理和資源清理
def cleanup_resources():
    """清理資源"""
    try:
        if hasattr(bot, 'data_manager'):
            bot.data_manager.save_all()
            logger.info("已保存所有資料")
    except Exception as e:
        logger.error(f"清理資源時出錯：{e}")

# 註冊清理函數
atexit.register(cleanup_resources)

def signal_handler(signum, frame):
    """處理信號"""
    logger.info(f"收到信號 {signum}，正在關閉...")
    cleanup_resources()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# [修復2級問題] 改進指令載入邏輯
def load_extensions():
    """載入擴展模組"""
    loaded_extensions = []
    failed_extensions = []
    
    for folder in ['commands', 'events']:
        try:
            for filename in os.listdir(f'./{folder}'):
                if filename.endswith('.py') and filename != '__init__.py':
                    extension_name = f'{folder}.{filename[:-3]}'
                    try:
                        bot.load_extension(extension_name)
                        loaded_extensions.append(extension_name)
                        logger.info(f"已載入花瓣模組：{extension_name}")
                    except Exception as e:
                        failed_extensions.append((extension_name, str(e)))
                        logger.error(f"無法載入模組 {extension_name}：{e}")
        except FileNotFoundError:
            logger.warning(f"未找到花園路徑 {folder}，略過載入")
    
    logger.info(f"成功載入 {len(loaded_extensions)} 個模組")
    if failed_extensions:
        logger.warning(f"載入失敗的模組：{len(failed_extensions)} 個")
        for ext_name, error in failed_extensions:
            logger.error(f"  - {ext_name}: {error}")
    
    return loaded_extensions, failed_extensions

# ----------- 載入指令與事件的花瓣 -----------
try:
    loaded_exts, failed_exts = load_extensions()
    if failed_exts:
        logger.warning("部分模組載入失敗，但程式繼續運行")
except Exception as e:
    logger.error(f"載入模組時發生嚴重錯誤：{e}")
    sys.exit(1)

# ----------- 喚醒幽幽子，步入 Discord 世界 -----------
try:
    bot.run(BOT_TOKEN)
except KeyboardInterrupt:
    logger.info("收到中斷信號，正在關閉...")
    cleanup_resources()
except Exception as e:
    logger.error(f"機器人運行時發生錯誤：{e}")
    cleanup_resources()
    sys.exit(1)
