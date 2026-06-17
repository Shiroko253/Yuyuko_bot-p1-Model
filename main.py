import os
import sys
import logging
import json
import yaml
import sqlite3
import copy  # [新增] 用於 save_all_async 的 deepcopy 保護
from time import time
from dotenv import load_dotenv
import discord
from discord.ext import commands
import asyncio
import argparse
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

# ----------- 解析啟動參數 -----------
parser = argparse.ArgumentParser(description='啟動幽幽子機器人')
parser.add_argument('mode', nargs='?', default='main', choices=['main', 'test'], 
                    help='選擇運行模式: main (正式環境) 或 test (測試環境), 預設為 main')
args = parser.parse_args()

# ----------- 喚醒幽幽子的密鑰 -----------
load_dotenv()

# 根據模式選擇對應的 token
if args.mode == 'main':
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    token_name = "BOT_TOKEN"
    logger.info("🌸 幽幽子將以【正式模式】甦醒")
else:
    BOT_TOKEN = os.getenv("TEST_BOT_TOKEN")
    token_name = "TEST_BOT_TOKEN"
    logger.info("🌸 幽幽子將以【測試模式】甦醒")

if not BOT_TOKEN:
    logger.error(f"未找到靈魂密鑰 {token_name},幽幽子無法甦醒")
    raise RuntimeError(f"Missing {token_name} in .env file")

# ----------- 設定靈魂的感知能力 -----------
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = discord.Bot(intents=intents, auto_sync_commands=True)

# ----------- 冥界資料管理之靈魂核心 (企業級重構版) -----------
class SakuraDataManager:
    """管理幽幽子花園中的資料，猶如櫻瓣隨風飄舞 (企業級記憶體快取與雙重鎖保護)"""
    
    def __init__(self):
        # 明確區分目錄結構
        self.config_dir = "config"
        self.data_dir = "data"
        self.economy_dir = "economy"
        
        self.game_state_dir = os.path.join(self.data_dir, "game_state")
        self.bot_state_dir = os.path.join(self.data_dir, "bot_state")
        self.player_data_dir = os.path.join(self.data_dir, "player_data")

        for directory in [self.config_dir, self.data_dir, self.economy_dir, 
                          self.game_state_dir, self.bot_state_dir, self.player_data_dir]:
            os.makedirs(directory, exist_ok=True)

        # Locks 先設為 None，在 Event Loop 啟動後初始化 (相容 Python 3.10+)
        self.balance_lock = None
        self.save_lock = None
        
        # 在線備份狀態標記
        self.is_backing_up = False

        # 1. Economy (經濟系統)
        self._initialize_json(f"{self.economy_dir}/balance.json")
        self.balance = self._load_json(f"{self.economy_dir}/balance.json")

        self._initialize_json(f"{self.economy_dir}/server_vault.json")
        self.server_vault = self._load_json(f"{self.economy_dir}/server_vault.json")
        
        self._initialize_json(f"{self.economy_dir}/personal_bank.json")
        self.personal_bank = self._load_json(f"{self.economy_dir}/personal_bank.json")

        self._initialize_json(f"{self.economy_dir}/credit.json")
        self.credit = self._load_json(f"{self.economy_dir}/credit.json")

        # 2. Game State (遊戲狀態)
        self._initialize_json(f"{self.game_state_dir}/blackjack.json")
        self.blackjack_data = self._load_json(f"{self.game_state_dir}/blackjack.json")
        
        self._initialize_json(f"{self.game_state_dir}/invalid_bets.json")
        self.invalid_bet_count = self._load_json(f"{self.game_state_dir}/invalid_bets.json")

        # 3. Bot State (Bot 狀態)
        BOT_STATUS_DEFAULT = {"disconnect_count": 0, "reconnect_count": 0, "last_event_time": None}
        self._initialize_json(f"{self.bot_state_dir}/bot_status.json", BOT_STATUS_DEFAULT)
        self.bot_status = self._load_json(f"{self.bot_state_dir}/bot_status.json", BOT_STATUS_DEFAULT)

        self._initialize_json(f"{self.config_dir}/dm_messages.json")
        self.dm_messages = self._load_json(f"{self.config_dir}/dm_messages.json")

        # 4. Player Data (玩家數據)
        self._initialize_json(f"{self.player_data_dir}/fishingbackpack.json")
        self.fishingbackpack = self._load_json(f"{self.player_data_dir}/fishingbackpack.json")
        
        self._initialize_yaml(f"{self.player_data_dir}/user_config.yml")
        self.user_config = self._load_yaml(f"{self.player_data_dir}/user_config.yml")

        self.black_hole_users = set()
        self._init_db()

    def setup_locks(self):
        """在事件循環啟動後建立 Lock (必須在 async 環境中呼叫)"""
        if self.balance_lock is None:
            self.balance_lock = asyncio.Lock()
        if self.save_lock is None:
            self.save_lock = asyncio.Lock()
        logger.info("🔒 asyncio.Lock 已在事件循環中初始化完畢")

    async def check_backup_status(self, ctx_or_interaction, command_name: str) -> bool:
        """檢查是否正在備份。如果是，則攔截指令並回覆用戶。"""
        if self.is_backing_up:
            msg = f"⚠️ 幽幽子正在進行數據備份，`/{command_name}` 暫時無法使用，請稍候再試哦～🌸"
            try:
                # 相容 ApplicationContext (ctx) 與 Interaction
                if hasattr(ctx_or_interaction, 'respond'): 
                    await ctx_or_interaction.respond(msg, ephemeral=True)
                elif hasattr(ctx_or_interaction, 'response'): 
                    if ctx_or_interaction.response.is_done():
                        await ctx_or_interaction.followup.send(msg, ephemeral=True)
                    else:
                        await ctx_or_interaction.response.send_message(msg, ephemeral=True)
            except Exception:
                pass
            return False
        return True

    @staticmethod
    def _initialize_json(file_path: str, default: dict = None):
        if default is None: default = {}
        if not os.path.exists(file_path):
            try:
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(default, f, indent=4, ensure_ascii=False)
                logger.info(f"已創建 JSON 檔案: {file_path}")
            except Exception as e:
                logger.error(f"無法創建 JSON 檔案 {file_path}: {e}")

    @staticmethod
    def _initialize_yaml(file_path: str, default: dict = None):
        if default is None: default = {}
        if not os.path.exists(file_path):
            try:
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                with open(file_path, "w", encoding="utf-8") as f:
                    yaml.safe_dump(default, f, allow_unicode=True)
                logger.info(f"已創建 YAML 檔案: {file_path}")
            except Exception as e:
                logger.error(f"無法創建 YAML 檔案 {file_path}: {e}")

    @staticmethod
    def _load_json(file_path: str, default: dict = None) -> dict:
        if default is None: default = {}
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f) or default
        except Exception as e:
            logger.error(f"無法載入 JSON 檔案 {file_path}: {e}")
            return default

    @staticmethod
    def _save_json(file_path: str, data: dict):
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            logger.error(f"無法保存 JSON 檔案 {file_path}: {e}")

    @staticmethod
    def _load_yaml(file_path: str, default: dict = None) -> dict:
        if default is None: default = {}
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or default
        except Exception as e:
            logger.error(f"無法載入 YAML 檔案 {file_path}: {e}")
            return default

    @staticmethod
    def _save_yaml(file_path: str, data: dict):
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "w", encoding="utf-8") as f:
                yaml.safe_dump(data, f, allow_unicode=True)
        except Exception as e:
            logger.error(f"無法保存 YAML 檔案 {file_path}: {e}")

    def _init_db(self):
        self.db_path = os.path.join(self.config_dir, "sakura_bot.db")
        try:
            with sqlite3.connect(self.db_path, check_same_thread=False) as conn:
                cursor = conn.cursor()
                cursor.execute('''CREATE TABLE IF NOT EXISTS UserMessages (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, message TEXT, repeat_count INTEGER DEFAULT 0, is_permanent BOOLEAN DEFAULT FALSE, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
                cursor.execute('''CREATE TABLE IF NOT EXISTS BackgroundInfo (user_id TEXT PRIMARY KEY, info TEXT)''')
                conn.commit()
                logger.info("已初始化 SQLite 資料庫")
        except sqlite3.Error as e:
            logger.error(f"無法初始化資料庫: {e}")

    def _save_snapshot(self, snapshot: dict):
        """將快照資料寫入檔案 (純同步，供 save_all_async 使用)"""
        self._save_json(f"{self.economy_dir}/balance.json",               snapshot["balance"])
        self._save_json(f"{self.economy_dir}/server_vault.json",          snapshot["server_vault"])
        self._save_json(f"{self.economy_dir}/personal_bank.json",         snapshot["personal_bank"])
        self._save_json(f"{self.economy_dir}/credit.json",                snapshot["credit"])
        self._save_json(f"{self.game_state_dir}/blackjack.json",          snapshot["blackjack_data"])
        self._save_json(f"{self.game_state_dir}/invalid_bets.json",       snapshot["invalid_bet_count"])
        self._save_json(f"{self.bot_state_dir}/bot_status.json",          snapshot["bot_status"])
        self._save_json(f"{self.config_dir}/dm_messages.json",            snapshot["dm_messages"])
        self._save_json(f"{self.player_data_dir}/fishingbackpack.json",   snapshot["fishingbackpack"])
        self._save_yaml(f"{self.player_data_dir}/user_config.yml",        snapshot["user_config"])

    def save_all(self):
        """將所有資料封存 (同步版本)"""
        self._save_snapshot({
            "balance":           self.balance,
            "server_vault":      self.server_vault,
            "personal_bank":     self.personal_bank,
            "credit":            self.credit,
            "blackjack_data":    self.blackjack_data,
            "invalid_bet_count": self.invalid_bet_count,
            "bot_status":        self.bot_status,
            "dm_messages":       self.dm_messages,
            "fishingbackpack":   self.fishingbackpack,
            "user_config":       self.user_config
        })

    async def save_all_async(self):
        """異步保存，先對所有 dict 做 deepcopy 再寫入，確保絕對安全"""
        if self.save_lock is None:
            logger.warning("⚠️ save_lock 尚未初始化，直接同步保存")
            self.save_all()
            return

        async with self.save_lock:
            snapshot = {
                "balance":           copy.deepcopy(self.balance),
                "server_vault":      copy.deepcopy(self.server_vault),
                "personal_bank":     copy.deepcopy(self.personal_bank),
                "credit":            copy.deepcopy(self.credit),
                "blackjack_data":    copy.deepcopy(self.blackjack_data),
                "invalid_bet_count": copy.deepcopy(self.invalid_bet_count),
                "bot_status":        copy.deepcopy(self.bot_status),
                "dm_messages":       copy.deepcopy(self.dm_messages),
                "fishingbackpack":   copy.deepcopy(self.fishingbackpack),
                "user_config":       copy.deepcopy(self.user_config)
            }
        await asyncio.to_thread(self._save_snapshot, snapshot)
        logger.info("💾 數據已安全保存 (Deepcopy 保護)")


# ----------- 幽幽子的靈魂啟動 -----------
bot.data_manager = SakuraDataManager()
bot.start_time = time()
bot.last_activity_time = bot.start_time
bot.run_mode = args.mode

# ----------- 幽幽子甦醒時的第一聲問候 (初始化 Locks) -----------
@bot.event
async def on_ready():
    # 確保 Locks 在 Event Loop 運行後才初始化 (解決 Python 3.10+ 的 RuntimeError)
    bot.data_manager.setup_locks()
    logger.info(f"🌸 幽幽子已甦醒！目前服侍 {len(bot.guilds)} 個伺服器，擁有 {len(bot.users)} 位靈魂。")

# ----------- 載入指令與事件的花瓣 -----------
for folder in ['commands', 'events']:
    try:
        for filename in os.listdir(f'./{folder}'):
            if filename.endswith('.py') and filename != '__init__.py':
                extension_name = f'{folder}.{filename[:-3]}'
                try:
                    bot.load_extension(extension_name)
                    logger.info(f"已載入花瓣模組: {extension_name}")
                except Exception as e:
                    logger.error(f"無法載入模組 {extension_name}: {e}")
    except FileNotFoundError:
        logger.warning(f"未找到花園路徑 {folder}, 略過載入")

# ----------- 喚醒幽幽子,步入 Discord 世界 -----------
try:
    bot.run(BOT_TOKEN)
except KeyboardInterrupt:
    logger.info("幽幽子正在優雅地離去...")
    bot.data_manager.save_all()
    logger.info("所有記憶已封存於櫻花樹下")
except Exception as e:
    logger.critical(f"幽幽子遭遇致命錯誤: {e}", exc_info=True)
    bot.data_manager.save_all()
finally:
    logger.info("靈魂已歸於寂靜")
