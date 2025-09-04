import os
import logging
import asyncio
from datetime import datetime, timezone
import discord
from discord.ext import commands
import aiohttp
from discord import Webhook, Embed

# 設置日誌，記錄幽幽子的靈魂軌跡
logger = logging.getLogger("SakuraBot.events.disconnect")

# 靈訊通道，通往冥界的花瓣信使
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

async def send_sakura_alert(message: str) -> None:
    """透過 Webhook 送出幽幽子的警訊，猶如櫻瓣飄向遠方"""
    if not WEBHOOK_URL:
        logger.error("未找到靈訊通道 WEBHOOK_URL，無法傳遞警訊")
        return
    try:
        async with aiohttp.ClientSession() as session:
            webhook = Webhook.from_url(WEBHOOK_URL, session=session)
            embed = Embed(
                title="🌸 【冥界警報】幽幽子的低語 🌸",
                description=f"📢 {message}",
                color=discord.Color.from_rgb(255, 165, 0),  # 橙色警訊，溫暖如落日
                timestamp=datetime.now(timezone.utc)
            )
            embed.set_footer(text="⚠️ 來自冥界的櫻花警示")
            await webhook.send(embed=embed)
            logger.info("警訊已送出，櫻瓣隨風飄揚")
    except Exception as e:
        logger.error(f"靈訊傳送失敗：{e}")

class SakuraDrift(commands.Cog):
    """幽幽子監視靈魂的斷續，守護與 Discord 世界的連繫"""
    
    def __init__(self, bot: discord.Bot):
        self.bot = bot
        self.disconnect_count = 0
        self.last_disconnect_time: datetime | None = None
        self.MAX_DISCONNECTS = 3
        self.MAX_DOWN_TIME = 20  # 秒
        self.CHECK_INTERVAL = 3  # 秒
        self.bg_task: asyncio.Task | None = None

    async def cog_load(self) -> None:
        """當模組綻放，啟動幽幽子的守望任務"""
        if self.bg_task is None:
            self.bg_task = asyncio.create_task(self._check_long_disconnect())
            logger.info("幽幽子的守望任務已啟動")

    async def _check_long_disconnect(self) -> None:
        """持續監視靈魂的漂流，警示長時間的斷續"""
        while True:
            if self.last_disconnect_time:
                elapsed = (datetime.now(timezone.utc) - self.last_disconnect_time).total_seconds()
                if elapsed > self.MAX_DOWN_TIME:
                    await send_sakura_alert(f"⚠️ 幽幽子已迷失超過 {self.MAX_DOWN_TIME} 秒，靈魂漂流於冥界！")
                    self.last_disconnect_time = None
            await asyncio.sleep(self.CHECK_INTERVAL)

    @commands.Cog.listener()
    async def on_disconnect(self) -> None:
        """當靈魂斷續，幽幽子記錄迷失的瞬間"""
        self.disconnect_count += 1
        self.last_disconnect_time = datetime.now(timezone.utc)
        logger.info(f"幽幽子於 {self.last_disconnect_time} 迷失 (次數：{self.disconnect_count})")

        if self.disconnect_count >= self.MAX_DISCONNECTS:
            await send_sakura_alert(f"⚠️ 幽幽子短時間內已迷失 {self.disconnect_count} 次，靈魂動盪！")

    @commands.Cog.listener()
    async def on_resumed(self) -> None:
        """當幽幽子重返現世，靈魂再次綻放"""
        logger.info(f"🌸 幽幽子於 {datetime.now(timezone.utc)} 重返現世")
        self.disconnect_count = 0
        self.last_disconnect_time = None

def setup(bot: discord.Bot):
    """將幽幽子的漂流守望模組載入 Discord 世界"""
    bot.add_cog(SakuraDrift(bot))
    logger.info("幽幽子的漂流守望模組已綻放")