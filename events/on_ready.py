import discord
from discord.ext import commands
import logging
import time
from dotenv import load_dotenv
import os
from datetime import datetime, timezone

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(BASE_DIR, ".env")
load_dotenv(dotenv_path=env_path)

class OnReady(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def send_webhook_message(self, message: str, color: discord.Color):
        """透過 Webhook 發送幽幽子的呢喃"""
        WEBHOOK_URL = os.getenv("WEBHOOK_URL")
        if not WEBHOOK_URL:
            logging.error("WEBHOOK_URL not set in .env")
            return
        try:
            # 確保 bot 有 session
            session = getattr(self.bot, "session", None)
            if not session:
                logging.error("Bot.session not initialized")
                return
            async with session.post(
                WEBHOOK_URL,
                json={
                    "embeds": [{
                        "description": message,
                        "color": color.value,
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }]
                }
            ) as response:
                if response.status != 204:
                    logging.error(f"Webhook failed with status {response.status}")
        except Exception as e:
            logging.error(f"Webhook send failed: {e}")

    @commands.Cog.listener()
    async def on_ready(self):
        """當機器人成功上線時執行"""
        try:
            logging.info(f"已登入為 {self.bot.user} (ID: {self.bot.user.id})")
            logging.info("------")

            await self.send_webhook_message("✅ **幽幽子已飄然現身！**", discord.Color.green())

            await self.bot.change_presence(
                status=discord.Status.dnd,
                activity=discord.Activity(type=discord.ActivityType.playing, name='Honkai: Star Rail')
            )
            logging.info("已設置機器人的狀態")

            end_time = time.time()
            startup_time = end_time - getattr(self.bot, "start_time", end_time)
            logging.info(f"Bot startup time: {startup_time:.2f} seconds")

            logging.info("加入的伺服器列表：")
            for guild in self.bot.guilds:
                logging.info(f"- {guild.name} (ID: {guild.id})")

            self.bot.last_activity_time = time.time()

        except discord.errors.HTTPException as e:
            logging.error(f"設置機器人狀態或發送 Webhook 訊息失敗：{e}")
        except Exception as e:
            logging.error(f"on_ready 事件處理失敗：{e}")

def setup(bot):
    bot.add_cog(OnReady(bot))
