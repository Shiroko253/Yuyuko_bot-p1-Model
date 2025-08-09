import discord
from discord.ext import commands
import logging
import os
import asyncio
from datetime import datetime, timezone
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(BASE_DIR, ".env")
load_dotenv(dotenv_path=env_path)
AUTHOR_ID = int(os.getenv("AUTHOR_ID", 0))
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

class Shutdown(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def send_webhook_message(self, message: str, color: discord.Color):
        """透過 Webhook 發送幽幽子的呢喃"""
        if not WEBHOOK_URL:
            logging.error("WEBHOOK_URL not set in commands/.env")
            return
        try:
            async with self.bot.session.post(
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

    @commands.slash_command(name="shutdown", description="讓幽幽子安靜地沉眠")
    async def shutdown(self, ctx: discord.ApplicationContext):
        """僅限指定作者使用的關閉指令"""
        if ctx.user.id != AUTHOR_ID:
            await ctx.respond(
                "嘻嘻，只有特別的人才能讓幽幽子安靜下來，你還不行哦～",
                ephemeral=True
            )
            return

        try:
            icon_url = self.bot.user.avatar.url if self.bot.user.avatar else self.bot.user.default_avatar.url
            embed = discord.Embed(
                title="幽幽子即將沉眠",
                description="幽幽子要睡囉，晚安哦～",
                color=discord.Color.red(),
                timestamp=datetime.now(timezone.utc)
            )
            embed.set_footer(text="來自冥界的微風與魂魄之語～", icon_url=icon_url)

            await ctx.respond(embed=embed, ephemeral=True)
            await self.send_webhook_message("🔴 **幽幽子飄然離去，魂魄歸於冥界...**", discord.Color.red())
            await asyncio.sleep(3)

            logging.info("Bot shutdown initiated by authorized user")

            if self.bot.session and not self.bot.session.closed:
                await self.bot.session.close()
                logging.info("Closed aiohttp.ClientSession")

            tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
            if tasks:
                logging.info(f"Cancelling {len(tasks)} pending tasks")
                for task in tasks:
                    task.cancel()
                results = await asyncio.gather(*tasks, return_exceptions=True)
                for i, result in enumerate(results):
                    if isinstance(result, Exception):
                        logging.warning(f"Task {i} cancellation raised: {result}")

            await self.bot.close()
            logging.info("Bot has been shut down")

        except Exception as e:
            logging.error(f"Shutdown command failed: {e}")
            await ctx.followup.send(
                f"哎呀，幽幽子好像被什麼纏住了，無法沉眠…錯誤：{e}",
                ephemeral=True
            )

def setup(bot):
    bot.add_cog(Shutdown(bot))
