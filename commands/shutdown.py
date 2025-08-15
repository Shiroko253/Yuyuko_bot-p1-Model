import discord
from discord.ext import commands
import logging
import asyncio
from datetime import datetime, timezone
import os

AUTHOR_ID = int(os.getenv("AUTHOR_ID", 0))
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

class Shutdown(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    async def send_webhook_message(self, message: str, color: discord.Color):
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
                text="冥界呼喚幽幽子沉眠",
                icon_url=str(self.bot.user.avatar.url if self.bot.user.avatar else self.bot.user.default_avatar.url)
            )
            await webhook.send(embed=embed)
        except Exception as e:
            logging.exception(f"Webhook send failed: {e}")

    @commands.slash_command(
        name="shutdown",
        description="讓幽幽子安靜地沉眠",
        default_member_permissions=discord.Permissions(administrator=True)
    )
    async def shutdown(self, ctx: discord.ApplicationContext):
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

            await self.send_webhook_message(
                "🔴 **幽幽子飄然離去，魂魄歸於冥界...**",
                discord.Color.red()
            )

            await asyncio.sleep(3)
            logging.info("Shutdown initiated by authorized user")

            await self.bot.close()
            logging.info("Bot has been shut down")
            # aiohttp session 將於 main.py finally 處理

        except Exception as e:
            logging.exception(f"Shutdown command failed: {e}")
            await ctx.followup.send(
                f"哎呀，幽幽子好像被什麼纏住了，無法沉眠…錯誤：{e}",
                ephemeral=True
            )

def setup(bot: discord.Bot):
    bot.add_cog(Shutdown(bot))