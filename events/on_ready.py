import discord
from discord.ext import commands
import logging
import time
import os
import aiohttp
from datetime import datetime, timezone

WEBHOOK_URL = os.getenv("WEBHOOK_URL")

async def send_webhook(bot: discord.Bot, message: str, color: discord.Color):
    """透過 Webhook 發送 Embed 訊息"""
    if not WEBHOOK_URL:
        logging.error("WEBHOOK_URL not set in .env")
        return
    try:
        from discord import Webhook, Embed
        async with aiohttp.ClientSession() as session:
            webhook = Webhook.from_url(WEBHOOK_URL, session=session)
            embed = Embed(description=message, color=color, timestamp=datetime.now(timezone.utc))
            await webhook.send(embed=embed)
    except Exception as e:
        logging.exception(f"Webhook send failed: {e}")

class OnReady(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        try:
            logging.info(f"已登入為 {self.bot.user} (ID: {self.bot.user.id})")
            await send_webhook(self.bot, "✅ **幽幽子已飄然現身！**", discord.Color.green())

            # 設定狀態
            await self.bot.change_presence(
                status=discord.Status.dnd,
                activity=discord.Game(name='Honkai: Star Rail')
            )
            logging.info("已設置機器人的狀態")

            # 啟動時間統計
            end_time = time.time()
            startup_time = end_time - getattr(self.bot, "start_time", end_time)
            logging.info(f"Bot startup time: {startup_time:.2f} seconds")

            # 伺服器列表
            guild_list = "\n".join([f"- {guild.name} (ID: {guild.id})" for guild in self.bot.guilds])
            logging.info("加入的伺服器列表：\n" + guild_list)

            self.bot.last_activity_time = time.time()

        except discord.HTTPException as e:
            logging.error(f"設置狀態或發送 Webhook 失敗：{e}")
        except Exception as e:
            logging.exception(f"on_ready 事件處理失敗：{e}")

def setup(bot: discord.Bot):
    bot.add_cog(OnReady(bot))
