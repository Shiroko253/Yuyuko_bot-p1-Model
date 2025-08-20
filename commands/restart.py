import discord
from discord.ext import commands
import logging
import os
import sys
import asyncio
import aiohttp
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

    # --- 修正：確保 session 可用 ---
    session = getattr(bot, "session", None)
    if session is None or session.closed:
        async with aiohttp.ClientSession() as temp_session:
            webhook = discord.Webhook.from_url(webhook_url, session=temp_session)
            await webhook.send(embed=embed)
    else:
        webhook = discord.Webhook.from_url(webhook_url, session=session)
        await webhook.send(embed=embed)

class RestartCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(name="restart", description="喚醒幽幽子重新起舞")
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
            await send_webhook_message(self.bot, "🔄 **幽幽子輕輕轉身，即將再度現身...**", discord.Color.orange())
            await asyncio.sleep(3)
            logging.info("Bot restart initiated by authorized user.")
            # --- 關閉 session ---
            session = getattr(self.bot, "session", None)
            if session and not session.closed:
                await session.close()
                logging.info("已關閉 aiohttp.ClientSession。")
            os.execv(sys.executable, [sys.executable] + sys.argv)
        except Exception as e:
            logging.error(f"Restart command failed: {e}")
            await ctx.respond(
                f"哎呀，幽幽子好像絆倒了…重啟失敗，錯誤：{e}",
                ephemeral=True
            )

def setup(bot):
    bot.add_cog(RestartCog(bot))
