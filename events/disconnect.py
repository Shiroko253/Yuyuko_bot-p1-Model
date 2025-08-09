import discord
from discord.ext import commands
import logging
import asyncio
from datetime import datetime, timezone
import aiohttp
from dotenv import load_dotenv
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(BASE_DIR, "..", ".env")  # 建議用主目錄 .env
load_dotenv(dotenv_path=env_path)
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

class Disconnect(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.disconnect_count = 0
        self.last_disconnect_time = None
        self.MAX_DISCONNECTS = 3
        self.MAX_DOWN_TIME = 20
        self.MAX_RETRIES = 5
        self.RETRY_DELAY = 10
        self.CHECK_INTERVAL = 3
        # 在 __init__ 啟動 background task
        self.task = self.bot.loop.create_task(self.check_long_disconnect())

    async def send_alert_async(self, message: str):
        """以幽幽子的靈魂之音發送警報至現世，安全判斷 loop 狀態"""
        if not WEBHOOK_URL:
            logging.error("WEBHOOK_URL not set in main .env")
            return

        embed = {
            "title": "🚨 【冥界警報】幽幽子的低語 🚨",
            "description": f"📢 {message}",
            "color": 0xFFA500,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "footer": {"text": "⚠️ 來自冥界的警示～"}
        }

        session = getattr(self.bot, "session", None)
        loop = getattr(self.bot, "loop", None)
        if not session or not loop or loop.is_closed():
            logging.error("Webhook not sent: session or loop is closed")
            return

        for attempt in range(1, self.MAX_RETRIES + 1):
            # 每次重試前都檢查 loop 狀態
            if loop.is_closed():
                logging.error("Event loop is closed, cannot send webhook")
                return
            try:
                async with session.post(
                    WEBHOOK_URL, json={"embeds": [embed]}, timeout=5
                ) as response:
                    if 200 <= response.status < 300:
                        logging.info("Webhook alert sent successfully")
                        return
                    else:
                        logging.warning(f"Webhook failed with status {response.status}")
            except asyncio.TimeoutError:
                logging.warning(f"Retry {attempt}/{self.MAX_RETRIES}: Webhook timed out")
            except aiohttp.ClientConnectionError:
                logging.warning(f"Retry {attempt}/{self.MAX_RETRIES}: Webhook connection failed")
            except Exception as e:
                logging.error(f"Webhook send failed: {e}")
                break
            await asyncio.sleep(self.RETRY_DELAY)
        logging.error("Failed to send webhook after max retries")

    async def check_long_disconnect(self):
        """監控幽幽子是否長時間迷失於冥界之外（安全判斷 loop 狀態）"""
        while True:
            # 每輪循環都判斷 loop 狀態
            loop = getattr(self.bot, "loop", None)
            if loop is None or loop.is_closed():
                logging.info("Event loop is closed, disconnect monitor task ending.")
                break
            if self.last_disconnect_time:
                elapsed = (datetime.now(timezone.utc) - self.last_disconnect_time).total_seconds()
                if elapsed > self.MAX_DOWN_TIME:
                    await self.send_alert_async(
                        f"⚠️ 【警告】幽幽子已迷失於現世之外超過 {self.MAX_DOWN_TIME} 秒，冥界之風是否斷絕？"
                    )
                    self.last_disconnect_time = None
            await asyncio.sleep(self.CHECK_INTERVAL)

    @commands.Cog.listener()
    async def on_disconnect(self):
        """當幽幽子與現世失去聯繫時"""
        self.disconnect_count += 1
        self.last_disconnect_time = datetime.now(timezone.utc)

        data_manager = getattr(self.bot, "data_manager", None)
        if data_manager:
            try:
                data_manager.bot_status["disconnect_count"] = self.disconnect_count
                data_manager.bot_status["last_event_time"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
                data_manager.save_all()
            except Exception as e:
                logging.warning(f"DataManager save failed during on_disconnect: {e}")
        else:
            logging.warning("DataManager not initialized during on_disconnect")

        logging.info(f"Bot disconnected at {self.last_disconnect_time.strftime('%Y-%m-%d %H:%M:%S')} (Count: {self.disconnect_count})")

        if self.disconnect_count >= self.MAX_DISCONNECTS:
            await self.send_alert_async(
                f"⚠️ 【警告】幽幽子短時間內已迷失 {self.disconnect_count} 次，冥界之風是否消散？"
            )

    @commands.Cog.listener()
    async def on_resumed(self):
        """當幽幽子重新飄回現世時"""
        data_manager = getattr(self.bot, "data_manager", None)
        if data_manager:
            try:
                data_manager.bot_status["reconnect_count"] = data_manager.bot_status.get("reconnect_count", 0) + 1
                data_manager.bot_status["last_event_time"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
                data_manager.save_all()
            except Exception as e:
                logging.warning(f"DataManager save failed during on_resumed: {e}")
        else:
            logging.warning("DataManager not initialized during on_resumed")

        logging.info(f"🌸 【訊息】幽幽子於 {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} 重返現世，冥界之風再次吹起～")
        self.disconnect_count = 0
        self.last_disconnect_time = None

def setup(bot):
    bot.add_cog(Disconnect(bot))
