import discord
from discord.ext import commands
import logging
import os
import sys
import asyncio
from datetime import datetime, timezone

AUTHOR_ID = int(os.getenv("AUTHOR_ID", 0))
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

class Restart(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    async def send_webhook_message(self, message: str, color: discord.Color):
        """透過 Webhook 發送幽幽子的呢喃"""
        if not WEBHOOK_URL:
            logging.error("WEBHOOK_URL not set in .env")
            return
        try:
            from discord import Webhook, Embed
            webhook = Webhook.from_url(WEBHOOK_URL, session=self.bot.session)
            embed = Embed(
                description=message,
                color=color,
                timestamp=datetime.now(timezone.utc)
            )
            embed.set_footer(
                text="冥界呼喚幽幽子甦醒",
                icon_url=str(self.bot.user.avatar.url if self.bot.user.avatar else self.bot.user.default_avatar.url)
            )
            await webhook.send(embed=embed)
        except Exception as e:
            logging.exception(f"Webhook send failed: {e}")

    @commands.slash_command(name="restart", description="喚醒幽幽子重新起舞")
    async def restart(self, ctx: discord.ApplicationContext):
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

            await self.send_webhook_message(
                "🔄 **幽幽子輕輕轉身，即將再度現身...**",
                discord.Color.orange()
            )
            await asyncio.sleep(3)
            logging.info("Bot restart initiated by authorized user")

            # 關閉 bot 與 session，main.py 會自動重建 session
            await self.bot.close()
            logging.info("Bot closed for restart")

            os.execv(sys.executable, [sys.executable] + sys.argv)
        except Exception as e:
            logging.exception(f"Restart command failed: {e}")
            await ctx.followup.send(
                f"哎呀，幽幽子好像絆倒了…重啟失敗，錯誤：{e}",
                ephemeral=True
            )

def setup(bot: discord.Bot):
    bot.add_cog(Restart(bot))