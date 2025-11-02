import os
import logging
import asyncio
from datetime import datetime, timezone
import discord
from discord.ext import commands
import aiohttp
from discord import Webhook, Embed

logger = logging.getLogger("SakuraBot.events.disconnect")

# 靈訊通道,通往冥界的花瓣信使
WEBHOOK_URL = os.getenv("WEBHOOK_URL")


async def send_sakura_alert(message: str) -> None:
    """透過 Webhook 送出幽幽子的警訊,猶如櫻瓣飄向遠方"""
    if not WEBHOOK_URL:
        logger.warning("未找到靈訊通道 WEBHOOK_URL,無法傳遞警訊")
        return
    
    try:
        async with aiohttp.ClientSession() as session:
            webhook = Webhook.from_url(WEBHOOK_URL, session=session)
            embed = Embed(
                title="🌸 【冥界警報】幽幽子的低語 🌸",
                description=f"📢 {message}",
                color=discord.Color.from_rgb(255, 165, 0),  # 橙色警訊,溫暖如落日
                timestamp=datetime.now(timezone.utc)
            )
            embed.set_footer(text="⚠️ 來自冥界的櫻花警示")
            await webhook.send(embed=embed)
            logger.info("警訊已送出,櫻瓣隨風飄揚")
    except aiohttp.ClientError as e:
        logger.error(f"靈訊傳送失敗 (網路錯誤): {e}")
    except Exception as e:
        logger.error(f"靈訊傳送失敗 (未知錯誤): {e}")


class SakuraDrift(commands.Cog):
    """幽幽子監視靈魂的斷續,守護與 Discord 世界的連繫"""
    
    def __init__(self, bot: discord.Bot):
        self.bot = bot
        self.disconnect_count = 0
        self.reconnect_count = 0
        self.last_disconnect_time: datetime | None = None
        self.first_disconnect_time: datetime | None = None
        
        # 配置參數
        self.MAX_DISCONNECTS = 3  # 最大斷線次數警告
        self.MAX_DOWN_TIME = 20  # 最大斷線時間(秒)
        self.CHECK_INTERVAL = 3  # 檢查間隔(秒)
        self.DISCONNECT_RESET_TIME = 300  # 5分鐘內斷線超過次數才警告
        
        self.bg_task: asyncio.Task | None = None
        self.alert_sent = False  # 防止重複發送警告

    async def cog_load(self) -> None:
        """當模組綻放,啟動幽幽子的守望任務"""
        if self.bg_task is None or self.bg_task.done():
            self.bg_task = asyncio.create_task(self._check_long_disconnect())
            logger.info("幽幽子的守望任務已啟動")

    async def cog_unload(self) -> None:
        """當模組卸載,停止守望任務"""
        if self.bg_task and not self.bg_task.done():
            self.bg_task.cancel()
            try:
                await self.bg_task
            except asyncio.CancelledError:
                pass
            logger.info("幽幽子的守望任務已停止")

    async def _check_long_disconnect(self) -> None:
        """持續監視靈魂的漂流,警示長時間的斷續"""
        try:
            while True:
                await asyncio.sleep(self.CHECK_INTERVAL)
                
                if self.last_disconnect_time and not self.alert_sent:
                    elapsed = (datetime.now(timezone.utc) - self.last_disconnect_time).total_seconds()
                    
                    if elapsed > self.MAX_DOWN_TIME:
                        await send_sakura_alert(
                            f"⚠️ 幽幽子已迷失超過 **{self.MAX_DOWN_TIME}** 秒,靈魂漂流於冥界!\n"
                            f"📊 斷線次數: {self.disconnect_count} | 重連次數: {self.reconnect_count}"
                        )
                        self.alert_sent = True  # 標記已發送,避免重複
                        
                        # 保存到 data_manager
                        if hasattr(self.bot, 'data_manager'):
                            self.bot.data_manager.bot_status["disconnect_count"] = self.disconnect_count
                            self.bot.data_manager.bot_status["reconnect_count"] = self.reconnect_count
                            self.bot.data_manager.bot_status["last_event_time"] = self.last_disconnect_time.isoformat()
                            self.bot.data_manager.save_all()
                
                # 重置斷線計數(如果超過重置時間)
                if self.first_disconnect_time:
                    time_since_first = (datetime.now(timezone.utc) - self.first_disconnect_time).total_seconds()
                    if time_since_first > self.DISCONNECT_RESET_TIME:
                        logger.info(f"斷線計數重置 (超過 {self.DISCONNECT_RESET_TIME} 秒)")
                        self.disconnect_count = 0
                        self.first_disconnect_time = None
                        
        except asyncio.CancelledError:
            logger.info("守望任務被取消")
            raise
        except Exception as e:
            logger.error(f"守望任務發生錯誤: {e}", exc_info=True)

    @commands.Cog.listener()
    async def on_disconnect(self) -> None:
        """當靈魂斷續,幽幽子記錄迷失的瞬間"""
        now = datetime.now(timezone.utc)
        self.disconnect_count += 1
        self.last_disconnect_time = now
        self.alert_sent = False  # 重置警告標記
        
        # 記錄第一次斷線時間
        if self.first_disconnect_time is None:
            self.first_disconnect_time = now
        
        logger.warning(f"幽幽子於 {now.strftime('%Y-%m-%d %H:%M:%S UTC')} 迷失 (累計: {self.disconnect_count} 次)")
        
        # 短時間內頻繁斷線警告
        if self.disconnect_count >= self.MAX_DISCONNECTS:
            time_span = (now - self.first_disconnect_time).total_seconds() if self.first_disconnect_time else 0
            await send_sakura_alert(
                f"🚨 **頻繁斷線警報!**\n"
                f"幽幽子在 **{time_span:.1f}** 秒內已迷失 **{self.disconnect_count}** 次,靈魂動盪!\n"
                f"⏰ 最後斷線時間: {now.strftime('%H:%M:%S UTC')}"
            )

    @commands.Cog.listener()
    async def on_resumed(self) -> None:
        """當幽幽子重返現世,靈魂再次綻放"""
        now = datetime.now(timezone.utc)
        self.reconnect_count += 1
        
        # 計算斷線時長
        downtime = 0
        if self.last_disconnect_time:
            downtime = (now - self.last_disconnect_time).total_seconds()
        
        logger.info(f"🌸 幽幽子於 {now.strftime('%Y-%m-%d %H:%M:%S UTC')} 重返現世 (斷線時長: {downtime:.2f}秒)")
        
        # 如果斷線超過警告時間,發送恢復通知
        if downtime > self.MAX_DOWN_TIME:
            await send_sakura_alert(
                f"✅ **幽幽子已重返現世!**\n"
                f"⏱️ 斷線時長: **{downtime:.2f}** 秒\n"
                f"📊 總斷線次數: {self.disconnect_count} | 總重連次數: {self.reconnect_count}"
            )
        
        # 重置部分狀態
        self.last_disconnect_time = None
        self.alert_sent = False
        
        # 如果成功重連,重置斷線計數(可選)
        # self.disconnect_count = 0
        # self.first_disconnect_time = None

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        """當 Bot 完全就緒時的額外處理"""
        # 如果之前有斷線記錄,發送恢復通知
        if self.disconnect_count > 0:
            logger.info(f"Bot 完全就緒,之前累計斷線 {self.disconnect_count} 次")


def setup(bot: discord.Bot):
    """將幽幽子的漂流守望模組載入 Discord 世界"""
    bot.add_cog(SakuraDrift(bot))
    logger.info("幽幽子的漂流守望模組已綻放")
