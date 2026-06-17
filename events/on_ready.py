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
        self.ready_fired = False  # 防止 on_ready 重複觸發

    @commands.Cog.listener()
    async def on_ready(self):
        """當幽幽子甦醒，記錄靈魂的初醒與世界連繫"""

        # [Debug 修復 #2] 修正註解以符合程式碼邏輯
        # 原因：asyncio.Lock 是綁定到 Event Loop 的，只要 Bot 沒有重啟 (Event Loop 不變)，
        # Lock 就不需要重新建立。保留 is None 判斷可避免重複建立，效能更好。
        if self.bot.data_manager.save_lock is None:
            self.bot.data_manager.setup_locks()

        # [Debug 修復 #3] 將 change_presence 移到 ready_fired 判斷之前
        # 原因：如果 Bot 斷線重連，ready_fired 為 True 會跳過後續邏輯。
        # 將狀態設置放在前面，可確保每次重連後 Bot 的「正在玩」狀態不會遺失。
        try:
            await self.bot.change_presence(
                status=discord.Status.dnd,
                activity=discord.Game(name="Honkai: Star Rail")
            )
            logger.info("已設置/刷新幽幽子的靈魂狀態")
        except discord.HTTPException as e:
            logger.error(f"設置狀態失敗：{e}")

        # 防止重複執行初始化邏輯（Discord 斷線重連會再次觸發 on_ready）
        if self.ready_fired:
            logger.info("幽幽子重新連接，無需再次初始化核心資料")
            return
        
        self.ready_fired = True

        try:
            logger.info(f"幽幽子已現身：{self.bot.user} (ID: {self.bot.user.id})")

            # 計算啟動時間，猶如櫻花綻放的瞬間
            startup_time = time.time() - getattr(self.bot, "start_time", time.time())
            logger.info(f"幽幽子甦醒耗時：{startup_time:.2f} 秒")

            # 記錄加入的伺服器，如櫻花瓣散落各處
            guild_count = len(self.bot.guilds)
            
            # [Debug 修復 #1] 加上 `or 0` 防呆，避免 Discord API 回傳 None 導致 sum() 崩潰
            user_count = sum((guild.member_count or 0) for guild in self.bot.guilds)
            logger.info(f"幽幽子守護著 {guild_count} 個伺服器花園，共 {user_count} 位靈魂")

            # 詳細列出伺服器（只在伺服器不多時列出）
            if guild_count <= 10:
                guild_list = "\n".join([
                    # [Debug 修復 #1] 同樣加上 `or 0` 防呆
                    f"  - {guild.name} (ID: {guild.id}, 成員: {guild.member_count or 0})"
                    for guild in self.bot.guilds
                ])
                logger.info(f"伺服器列表：\n{guild_list}")

            # 更新最後活動時間
            self.bot.last_activity_time = time.time()

            # 記錄當前時間
            now = datetime.now(timezone.utc)
            logger.info(f"甦醒時刻：{now.strftime('%Y-%m-%d %H:%M:%S UTC')}")
            logger.info("靜待世界的回音...")

        except Exception as e:
            # 使用 logger.exception 會自動附帶完整的 Traceback，方便除錯
            logger.exception(f"幽幽子甦醒過程出錯：{e}")

    @commands.Cog.listener()
    async def on_resumed(self):
        """當幽幽子重新連接時的處理 (Gateway Resume)"""
        logger.info("幽幽子重新連接至 Discord (Resumed)")
        self.bot.last_activity_time = time.time()


def setup(bot: discord.Bot):
    bot.add_cog(SakuraAwakening(bot))
    logger.info("幽幽子的初醒模組已綻放")
