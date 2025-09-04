import os
import logging
import time
from datetime import datetime, timezone
import discord
from discord.ext import commands

logger = logging.getLogger("SakuraBot.events.on_ready")

class SakuraAwakening(commands.Cog):
    """幽幽子甦醒的瞬間，準備迎接 Discord 世界的呼喚"""

    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        """當幽幽子甦醒，記錄靈魂的初醒與世界連繫"""
        try:
            logger.info(f"幽幽子已現身：{self.bot.user} (ID: {self.bot.user.id})")

            # 設置幽幽子的靈魂狀態
            await self.bot.change_presence(
                status=discord.Status.dnd,
                activity=discord.Game(name="Honkai: Star Rail")
            )
            logger.info("已設置幽幽子的靈魂狀態，靜待世界的回音")

            # 計算啟動時間，猶如櫻花綻放的瞬間
            end_time = time.time()
            startup_time = end_time - getattr(self.bot, "start_time", end_time)
            logger.info(f"幽幽子甦醒耗時：{startup_time:.2f} 秒")

            # 記錄加入的伺服器，如櫻花瓣散落各處
            guild_list = "\n".join([f"- {guild.name} (ID: {guild.id})" for guild in self.bot.guilds])
            logger.info(f"幽幽子感知的伺服器花園：\n{guild_list}")

            # 更新最後活動時間
            self.bot.last_activity_time = time.time()

        except discord.HTTPException as e:
            logger.error(f"設置狀態失敗：{e}")
        except Exception as e:
            logger.exception(f"幽幽子甦醒過程出錯：{e}")

def setup(bot: discord.Bot):
    bot.add_cog(SakuraAwakening(bot))
    logger.info("幽幽子的初醒模組已綻放")