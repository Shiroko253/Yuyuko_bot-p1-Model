import discord
from discord.ext import commands
import logging
import os
import asyncio
from datetime import datetime, timezone

AUTHOR_ID = int(os.getenv("AUTHOR_ID", 0))

async def send_webhook_message(bot, content: str, color: discord.Color):
    webhook_url = os.getenv("WEBHOOK_URL")
    if not webhook_url:
        logging.error("Webhook URL 未配置。")
        raise ValueError("Webhook URL 未配置。")
    icon_url = bot.user.avatar.url if bot.user.avatar else bot.user.default_avatar.url
    embed = discord.Embed(
        title="🌸 幽幽子的飄渺呢喃",
        description=content,
        color=color,
        timestamp=datetime.now(timezone.utc)
    )
    embed.set_footer(text="來自冥界的微風與魂魄之語～", icon_url=icon_url)
    webhook = discord.Webhook.from_url(webhook_url, session=bot.session)
    await webhook.send(embed=embed)

class ShutdownCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(name="shutdown", description="讓幽幽子安靜地沉眠")
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
            await send_webhook_message(self.bot, "🔴 **幽幽子飄然離去，魂魄歸於冥界...**", discord.Color.red())
            await asyncio.sleep(2)
            logging.info("Bot shutdown initiated by authorized user.")

            # 不要自己關 bot.session，讓 pycord 處理
            await self.bot.close()
            logging.info("Bot 已關閉。")
        except Exception as e:
            logging.error(f"Shutdown command failed: {e}")
            await ctx.respond(
                f"哎呀，幽幽子好像被什麼纏住了，無法沉眠…錯誤：{e}",
                ephemeral=True
            )

def setup(bot):
    bot.add_cog(ShutdownCog(bot))
