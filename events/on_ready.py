import logging
import time
import discord
from discord.ext import commands

# 使用統一日誌器（與 main.py 一致）
logger = logging.getLogger("SakuraBot")

# 嘗試匯入 send_sakura_alert，若失敗則提供 fallback
try:
    from utils.alerts import send_sakura_alert
except ImportError:
    logger.warning("未找到 utils.alerts.send_sakura_alert，將跳過甦醒通知")
    async def send_sakura_alert(message: str):
        logger.info(f"模擬通知：{message}")

class SakuraAwakening(commands.Cog):
    """幽幽子甦醒的瞬間，準備迎接 Discord 世界的呼喚"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._has_awakened = False  # 防止 on_ready 多次執行初始化

    @commands.Cog.listener()
    async def on_ready(self):
        """當幽幽子甦醒，記錄靈魂的初醒與世界連繫"""
        # 防止重複執行（Discord 可能多次觸發 on_ready）
        if self._has_awakened:
            logger.info("幽幽子已甦醒過，跳過重複初始化")
            return

        try:
            logger.info(f"幽幽子已現身：{self.bot.user} (ID: {self.bot.user.id})")

            # 設置幽幽子的靈魂狀態
            await self.bot.change_presence(
                status=discord.Status.dnd,
                activity=discord.Game(name="Honkai: Star Rail")
            )
            logger.info("已設置幽幽子的靈魂狀態，靜待世界的回音")

            # 計算啟動時間（防禦性檢查）
            start_time = getattr(self.bot, "start_time", time.time())
            startup_time = time.time() - start_time
            logger.info(f"幽幽子甦醒耗時：{startup_time:.2f} 秒")

            # 記錄伺服器資訊
            guild_count = len(self.bot.guilds)
            logger.info(f"幽幽子已降臨 {guild_count} 座伺服器花園")
            if guild_count <= 10:
                guild_list = "\n".join([f"- {guild.name} (ID: {guild.id})" for guild in self.bot.guilds])
                logger.info(f"花園清單：\n{guild_list}")

            # 更新最後活動時間
            self.bot.last_activity_time = time.time()

            # 標記已甦醒
            self._has_awakened = True

            # 🌸 發送甦醒通知（安全呼叫）
            try:
                await send_sakura_alert("🌸 幽幽子已重返現世，櫻花再度綻放。")
            except Exception as e:
                logger.error(f"發送甦醒通知失敗：{e}")

        except discord.HTTPException as e:
            logger.error(f"設置狀態失敗：{e}")
        except Exception as e:
            logger.exception(f"幽幽子甦醒過程出錯：{e}")

def setup(bot: commands.Bot):
    bot.add_cog(SakuraAwakening(bot))
    logger.info("幽幽子的初醒模組已綻放")
