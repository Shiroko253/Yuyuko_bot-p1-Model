import discord
from discord.ext import commands
import logging
import asyncio
from datetime import datetime, timezone
import os
import aiohttp

WEBHOOK_URL = os.getenv("WEBHOOK_URL")

async def send_webhook(message: str):
    if not WEBHOOK_URL:
        logging.error("WEBHOOK_URL not set in .env")
        return
    try:
        async with aiohttp.ClientSession() as session:
            webhook = discord.Webhook.from_url(WEBHOOK_URL, adapter=discord.AsyncWebhookAdapter(session))
            embed = discord.Embed(
                title="🚨 【冥界警報】幽幽子的低語 🚨",
                description=f"📢 {message}",
                color=0xFFA500,
                timestamp=datetime.now(timezone.utc)
            ).set_footer(text="⚠️ 來自冥界的警示～")
            await webhook.send(embed=embed)
    except Exception as e:
        logging.error(f"Webhook send failed: {e}")

class Disconnect(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.disconnect_count = 0
        self.last_disconnect_time = None
        self.MAX_DISCONNECTS = 3
        self.MAX_DOWN_TIME = 20
        self.CHECK_INTERVAL = 3
        asyncio.create_task(self.check_long_disconnect())

    async def check_long_disconnect(self):
        while True:
            if self.last_disconnect_time:
                elapsed = (datetime.now(timezone.utc) - self.last_disconnect_time).total_seconds()
                if elapsed > self.MAX_DOWN_TIME:
                    await send_webhook(f"⚠️ 幽幽子已迷失超過 {self.MAX_DOWN_TIME} 秒！")
                    self.last_disconnect_time = None
            await asyncio.sleep(self.CHECK_INTERVAL)

    @commands.Cog.listener()
    async def on_disconnect(self):
        self.disconnect_count += 1
        self.last_disconnect_time = datetime.now(timezone.utc)
        logging.info(f"Bot disconnected at {self.last_disconnect_time} (Count: {self.disconnect_count})")

        if self.disconnect_count >= self.MAX_DISCONNECTS:
            await send_webhook(f"⚠️ 幽幽子短時間內已迷失 {self.disconnect_count} 次！")

    @commands.Cog.listener()
    async def on_resumed(self):
        logging.info(f"🌸 幽幽子於 {datetime.now(timezone.utc)} 重返現世")
        self.disconnect_count = 0
        self.last_disconnect_time = None

def setup(bot):
    bot.add_cog(Disconnect(bot))
