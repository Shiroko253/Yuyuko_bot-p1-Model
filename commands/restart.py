import discord
from discord.ext import commands
import logging
import os
import sys
import asyncio
from datetime import datetime, timezone
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(BASE_DIR, ".env")
load_dotenv(dotenv_path=env_path)
AUTHOR_ID = int(os.getenv("AUTHOR_ID", 0))
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

class Restart(commands.Cog):
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

    @commands.slash_command(name="restart", description="喚醒幽幽子重新起舞")
    async def restart(self, ctx: discord.ApplicationContext):
        """重啟 Discord 機器人，僅限授權用戶執行"""
        if ctx.user.id != AUTHOR_ID:
            await ctx.respond(
                "只有靈魂的主人才能喚醒幽幽子，你還不行呢～",
                ephemeral=True
            )
            return

        try:
            icon_url = self.bot.user.avatar.url if self.bot.user.avatar else self.bot.user.default_avatar.url
            embed = discord.Embed(
                title="幽幽子即將甦醒",
                description="幽幽子要重新翩翩起舞啦，稍等片刻哦～",
                color=discord.Color.orange(),
                timestamp=datetime.now(timezone.utc)
            )
            embed.set_footer(text="來自冥界的微風與魂魄之語～", icon_url=icon_url)

            await ctx.respond(embed=embed, ephemeral=True)
            await self.send_webhook_message("🔄 **幽幽子輕輕轉身，即將再度現身...**", discord.Color.orange())
            await asyncio.sleep(3)
            logging.info("Bot restart initiated by authorized user")

            if self.bot.session and not self.bot.session.closed:
                await self.bot.session.close()
                logging.info("Closed aiohttp.ClientSession")

            os.execv(sys.executable, [sys.executable] + sys.argv)
        except Exception as e:
            logging.error(f"Restart command failed: {e}")
            await ctx.followup.send(
                f"哎呀，幽幽子好像絆倒了…重啟失敗，錯誤：{e}",
                ephemeral=True
            )

def setup(bot):
    bot.add_cog(Restart(bot))
