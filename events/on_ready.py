import logging
import time
from datetime import datetime, timezone
import discord
from discord.ext import commands

logger = logging.getLogger("SakuraBot.events.on_ready")


class SakuraAwakening(commands.Cog):
    """幽幽子甦醒的瞬間,準備迎接 Discord 世界的呼喚"""
    
    def __init__(self, bot: discord.Bot):
        self.bot = bot
        self.ready_fired = False  # 防止 on_ready 重複觸發

    @commands.Cog.listener()
    async def on_ready(self):
        """當幽幽子甦醒,記錄靈魂的初醒與世界連繫"""
        # 防止重複執行(Discord 斷線重連會再次觸發 on_ready)
        if self.ready_fired:
            logger.info("幽幽子重新連接,無需再次初始化")
            return
        
        self.ready_fired = True
        
        try:
            logger.info(f"幽幽子已現身:{self.bot.user} (ID: {self.bot.user.id})")
            
            # 設置幽幽子的靈魂狀態
            await self.bot.change_presence(
                status=discord.Status.dnd,
                activity=discord.Game(name="Honkai: Star Rail")
            )
            logger.info("已設置幽幽子的靈魂狀態,靜待世界的回音")
            
            # 計算啟動時間,猶如櫻花綻放的瞬間
            startup_time = time.time() - getattr(self.bot, "start_time", time.time())
            logger.info(f"幽幽子甦醒耗時:{startup_time:.2f} 秒")
            
            # 記錄加入的伺服器,如櫻花瓣散落各處
            guild_count = len(self.bot.guilds)
            user_count = sum(guild.member_count for guild in self.bot.guilds)
            logger.info(f"幽幽子守護著 {guild_count} 個伺服器花園,共 {user_count} 位靈魂")
            
            # 詳細列出伺服器(可選)
            if guild_count <= 10:  # 只在伺服器不多時列出
                guild_list = "\n".join([
                    f"  - {guild.name} (ID: {guild.id}, 成員: {guild.member_count})" 
                    for guild in self.bot.guilds
                ])
                logger.info(f"伺服器列表:\n{guild_list}")
            
            # 更新最後活動時間
            self.bot.last_activity_time = time.time()
            
            # 記錄當前時間
            now = datetime.now(timezone.utc)
            logger.info(f"甦醒時刻:{now.strftime('%Y-%m-%d %H:%M:%S UTC')}")
            
        except discord.HTTPException as e:
            logger.error(f"設置狀態失敗:{e}")
        except Exception as e:
            logger.exception(f"幽幽子甦醒過程出錯:{e}")

    @commands.Cog.listener()
    async def on_resumed(self):
        """當幽幽子重新連接時的處理"""
        logger.info("幽幽子重新連接至 Discord")
        self.bot.last_activity_time = time.time()


def setup(bot: discord.Bot):
    bot.add_cog(SakuraAwakening(bot))
    logger.info("幽幽子的初醒模組已綻放")
