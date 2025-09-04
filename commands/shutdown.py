import discord
from discord.ext import commands
import logging
import os
import asyncio
from datetime import datetime, timezone
import aiohttp

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
    # 用 aiohttp session 正確發送
    async with aiohttp.ClientSession() as session:
        webhook = discord.Webhook.from_url(webhook_url, session=session)
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
                title="🌸 幽幽子即將沉眠 🌸",
                description=(
                    "夜櫻下，幽幽子輕輕閉上雙眼，靈魂歸於冥界安眠…\n"
                    "感謝大家的陪伴，夢裡見吧～"
                ),
                color=discord.Color.from_rgb(205, 133, 232),
                timestamp=datetime.now(timezone.utc)
            )
            embed.set_footer(text="來自冥界的微風與魂魄之語～", icon_url=icon_url)
            await ctx.respond(embed=embed, ephemeral=True)
            await send_webhook_message(
                self.bot,
                "🔴 **幽幽子飄然離去，魂魄歸於冥界…**\n\n「夜櫻下的安眠，是幽幽子的幸福時刻～」",
                discord.Color.from_rgb(205, 133, 232)
            )
            await asyncio.sleep(2)
            logging.info("Bot shutdown initiated by authorized user.")

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