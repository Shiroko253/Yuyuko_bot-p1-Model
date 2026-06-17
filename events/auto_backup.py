import discord
from discord.ext import commands, tasks
import logging
import json
import sqlite3
import asyncio
import os
from datetime import datetime, time, timezone, timedelta

logger = logging.getLogger("SakuraBot.events.auto_backup")

AUTHOR_ID = int(os.getenv("AUTHOR_ID", 0))
LOCAL_TIMEZONE = timezone(timedelta(hours=8))


class AutoBackup(commands.Cog):
    """
    ✿ 幽幽子的在線熱備份守衛 ✿
    定時將花園的記憶封存於 SQLite 殿堂，且不影響幽幽子與大家的互動♪
    """

    def __init__(self, bot: discord.Bot):
        self.bot = bot
        
        # 策略：每天凌晨 4:00 觸發在線備份 (不關機)
        self.backup_task.start()
        logger.info("在線備份守衛已部署，幽幽子會按時整理記憶，且不會打擾大家～")

    def cog_unload(self):
        self.backup_task.cancel()
        logger.info("在線備份守衛已撤收")

    @tasks.loop(time=time(4, 0, tzinfo=LOCAL_TIMEZONE))
    async def backup_task(self):
        """每天凌晨 4:00 觸發在線備份"""
        logger.info("🌸 觸發每日在線備份任務...")
        await self._execute_online_backup()

    async def _execute_online_backup(self):
        """執行在線備份 (不關機)"""
        if not hasattr(self.bot, 'data_manager'):
            return

        dm = self.bot.data_manager
        
        try:
            # 1. 開啟備份標記，攔截修改類指令
            dm.is_backing_up = True
            logger.info("🔒 數據庫已進入備份保護模式，修改類指令已暫停。")

            # 2. 確保記憶體中的最新數據寫入 JSON (雙重保險)
            await dm.save_all_async()
            
            # 3. 將數據快照寫入 SQLite
            await asyncio.to_thread(self._save_snapshot_to_sqlite)
            
            logger.info("✅ 在線備份成功完成！數據已安全封存於 SQLite。")
            
            # 4. 發送私訊通知給主人 (可選)
            if AUTHOR_ID:
                try:
                    owner = self.bot.get_user(AUTHOR_ID) or await self.bot.fetch_user(AUTHOR_ID)
                    if owner:
                        await owner.send("🌸 **每日在線備份完成**\n幽幽子已將所有記憶安全封存於 SQLite 殿堂，系統運行一切正常！✨")
                except Exception as e:
                    logger.warning(f"無法發送備份通知: {e}")

        except Exception as e:
            logger.error(f"❌ 在線備份過程發生錯誤: {e}", exc_info=True)
        finally:
            # 5. [關鍵] 無論成功或失敗，都必須關閉備份標記，恢復指令功能
            dm.is_backing_up = False
            logger.info("🔓 數據庫備份保護模式已解除，指令恢復正常。")

    def _save_snapshot_to_sqlite(self):
        """同步方法：將所有數據打包並寫入 SQLite"""
        dm = self.bot.data_manager
        db_path = dm.db_path

        snapshot = {
            "backup_time": datetime.now(LOCAL_TIMEZONE).isoformat(),
            "balance": dm.balance,
            "blackjack_data": dm.blackjack_data,
            "invalid_bet_count": dm.invalid_bet_count,
            "bot_status": dm.bot_status,
            "dm_messages": dm.dm_messages,
            "fishingbackpack": dm.fishingbackpack,
            "user_config": dm.user_config
        }

        json_payload = json.dumps(snapshot, ensure_ascii=False, indent=None)

        try:
            with sqlite3.connect(db_path, check_same_thread=False) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS SystemBackups (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        snapshot_data TEXT NOT NULL
                    )
                ''')
                cursor.execute('INSERT INTO SystemBackups (snapshot_data) VALUES (?)', (json_payload,))
                
                # 清理舊備份，只保留最近 7 份
                cursor.execute('''
                    DELETE FROM SystemBackups 
                    WHERE id NOT IN (SELECT id FROM SystemBackups ORDER BY created_at DESC LIMIT 7)
                ''')
                conn.commit()
                logger.info(f"SQLite 備份成功。目前保留了 {cursor.execute('SELECT COUNT(*) FROM SystemBackups').fetchone()[0]} 份快照。")
        except sqlite3.Error as e:
            logger.error(f"SQLite 寫入失敗: {e}")
            raise


def setup(bot: discord.Bot):
    bot.add_cog(AutoBackup(bot))
    logger.info("在線備份模組已綻放")
    
