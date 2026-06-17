import os
import logging
import asyncio
from datetime import datetime, timezone, timedelta
from typing import Optional  # [Debug 修復 #1] 引入 Optional 相容 Python 3.9
import discord
from discord.ext import commands
import aiohttp
from discord import Webhook, Embed

logger = logging.getLogger("SakuraBot.events.disconnect")

# 靈訊通道，通往冥界的花瓣信使
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# 時區設定（UTC+8 馬來西亞/台灣/新加坡時區）
LOCAL_TIMEZONE = timezone(timedelta(hours=8))


def get_local_time() -> datetime:
    """獲取本地時間（UTC+8）"""
    return datetime.now(LOCAL_TIMEZONE)


def get_date_key() -> str:
    """獲取當前日期作為 key（YYYY-MM-DD）"""
    return get_local_time().strftime("%Y-%m-%d")


def format_timestamp(dt: datetime) -> str:
    """格式化時間戳為易讀格式"""
    return dt.strftime("%Y-%m-%d %H:%M:%S")


class SakuraDrift(commands.Cog):
    """幽幽子監視靈魂的斷續，守護與 Discord 世界的連繫"""

    def __init__(self, bot: discord.Bot):
        self.bot = bot
        
        # [Debug 修復 #1] 改用 Optional 確保 Python 3.9 也能正常運行
        self.last_disconnect_time: Optional[datetime] = None
        self.first_disconnect_time: Optional[datetime] = None

        # 當天計數器（用於實時警告）
        self.session_disconnect_count = 0
        self.session_reconnect_count = 0

        # 配置參數
        self.MAX_DISCONNECTS = 3          # 最大斷線次數警告
        self.MAX_DOWN_TIME = 20           # 最大斷線時間（秒）
        self.CHECK_INTERVAL = 3           # 檢查間隔（秒）
        self.DISCONNECT_RESET_TIME = 300  # 5分鐘內斷線超過次數才警告
        self.HISTORY_RETENTION_DAYS = 14  # 保留歷史記錄天數

        self.bg_task: Optional[asyncio.Task] = None
        self.alert_sent = False           # 防止重複發送警告
        
        # [Debug 修復 #2] 將 aiohttp.ClientSession 提升為類別屬性，避免頻繁創建/銷毀
        self.session: Optional[aiohttp.ClientSession] = None

        logger.info("斷線監控系統已載入，幽幽子開始守望櫻花湖")

    def _init_bot_status(self) -> None:
        """初始化 bot_status 的數據結構"""
        if not hasattr(self.bot, 'data_manager'):
            logger.warning("data_manager 不存在，無法初始化狀態")
            return

        if "history" not in self.bot.data_manager.bot_status:
            self.bot.data_manager.bot_status["history"] = {}

        today = get_date_key()
        if today not in self.bot.data_manager.bot_status["history"]:
            self.bot.data_manager.bot_status["history"][today] = {
                "disconnect": 0,
                "reconnect": 0,
                "events": []
            }

        # [Debug 修復 #3] 移除對 session_disconnect_count 的賦值
        # session_disconnect_count 純粹用於計算「短時間內連續斷線次數」，
        # 不應與「當日總斷線次數 (today_data['disconnect'])」混為一談。
        # 讓它保持 __init__ 中的 0 即可。

    async def save_event(self, event_type: str, details: dict = None) -> None:
        """保存事件到 bot_status.json 的歷史記錄"""
        if not hasattr(self.bot, 'data_manager'):
            logger.warning("data_manager 不存在，無法保存事件")
            return

        try:
            today = get_date_key()
            now = get_local_time()

            if "history" not in self.bot.data_manager.bot_status:
                self.bot.data_manager.bot_status["history"] = {}

            if today not in self.bot.data_manager.bot_status["history"]:
                self.bot.data_manager.bot_status["history"][today] = {
                    "disconnect": 0,
                    "reconnect": 0,
                    "events": []
                }

            today_data = self.bot.data_manager.bot_status["history"][today]

            if event_type == "disconnect":
                today_data["disconnect"] += 1
            elif event_type == "reconnect":
                today_data["reconnect"] += 1

            event_record = {
                "type": event_type,
                "time": format_timestamp(now),
                "timestamp": now.isoformat()
            }

            if details:
                event_record.update(details)

            today_data["events"].append(event_record)

            self._cleanup_old_records()

            await self.bot.data_manager.save_all_async()
            logger.debug(f"事件已保存: {event_type} at {format_timestamp(now)}")

        except Exception as e:
            logger.error(f"保存事件失敗: {e}", exc_info=True)

    def _cleanup_old_records(self) -> None:
        """清理過期的舊記錄，避免佔用空間"""
        if not hasattr(self.bot, 'data_manager'):
            return

        try:
            history = self.bot.data_manager.bot_status.get("history", {})
            if not history:
                return

            today = get_local_time()
            cutoff_date = (today - timedelta(days=self.HISTORY_RETENTION_DAYS)).strftime("%Y-%m-%d")

            dates_to_remove = [
                date for date in history.keys()
                if date < cutoff_date
            ]

            if dates_to_remove:
                for date in dates_to_remove:
                    events_count = len(history[date].get("events", []))
                    disconnect_count = history[date].get("disconnect", 0)
                    del history[date]
                    logger.info(
                        f"已清理舊記錄: {date} "
                        f"(斷線 {disconnect_count} 次, {events_count} 個事件)"
                    )

                logger.info(
                    f"清理完成: 刪除了 {len(dates_to_remove)} 天的舊記錄 "
                    f"（保留 {self.HISTORY_RETENTION_DAYS} 天內的記錄）"
                )

        except Exception as e:
            logger.error(f"清理舊記錄失敗: {e}", exc_info=True)

    def get_today_stats(self) -> dict:
        """獲取今天的統計資料"""
        if not hasattr(self.bot, 'data_manager'):
            return {"disconnect": 0, "reconnect": 0}

        today = get_date_key()
        history = self.bot.data_manager.bot_status.get("history", {})
        today_data = history.get(today, {"disconnect": 0, "reconnect": 0})

        return {
            "disconnect": today_data.get("disconnect", 0),
            "reconnect": today_data.get("reconnect", 0)
        }

    async def send_sakura_alert(self, message: str) -> None:
        """透過 Webhook 送出幽幽子的警訊，猶如櫻瓣飄向遠方"""
        if not WEBHOOK_URL:
            logger.warning("未找到靈訊通道 WEBHOOK_URL，無法傳遞警訊")
            return

        # [Debug 修復 #2] 使用共用的 self.session，避免頻繁創建/銷毀
        if not self.session or self.session.closed:
            logger.error("Webhook Session 未初始化或已關閉，無法發送警訊")
            return

        try:
            webhook = Webhook.from_url(WEBHOOK_URL, session=self.session)
            embed = Embed(
                title="🌸 【冥界警報】幽幽子的低語 🌸",
                description=f"📢 {message}",
                color=discord.Color.from_rgb(255, 165, 0),
                timestamp=get_local_time()
            )
            embed.set_footer(text="⚠️ 來自冥界的櫻花警示 • UTC+8")
            await webhook.send(embed=embed)
            logger.info("警訊已送出，櫻瓣隨風飄揚")
        except Exception as e:
            logger.error(f"靈訊傳送失敗: {e}", exc_info=True)

    async def cog_load(self) -> None:
        """當模組綻放，啟動幽幽子的守望任務"""
        self._init_bot_status()

        # [Debug 修復 #2] 在 cog_load 中初始化共用的 aiohttp Session
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()

        if self.bg_task is None or self.bg_task.done():
            self.bg_task = asyncio.create_task(self._check_long_disconnect())
            logger.info("幽幽子的守望任務已啟動")

    async def cog_unload(self) -> None:
        """當模組卸載，停止守望任務"""
        if self.bg_task and not self.bg_task.done():
            self.bg_task.cancel()
            try:
                await self.bg_task
            except asyncio.CancelledError:
                pass
        
        # [Debug 修復 #2] 在 cog_unload 中優雅關閉 Session，防止記憶體洩漏
        if self.session and not self.session.closed:
            await self.session.close()
            
        logger.info("幽幽子的守望任務已停止")

    async def _check_long_disconnect(self) -> None:
        """持續監視靈魂的漂流，警示長時間的斷續"""
        try:
            while True:
                await asyncio.sleep(self.CHECK_INTERVAL)

                if self.last_disconnect_time and not self.alert_sent:
                    elapsed = (get_local_time() - self.last_disconnect_time).total_seconds()

                    if elapsed > self.MAX_DOWN_TIME:
                        stats = self.get_today_stats()
                        await self.send_sakura_alert(
                            f"⚠️ 幽幽子已迷失超過 **{self.MAX_DOWN_TIME}** 秒，靈魂漂流於冥界!\n"
                            f"⏰ 斷線時間: **{format_timestamp(self.last_disconnect_time)}**\n"
                            f"📊 今日統計: 斷線 {stats['disconnect']} 次 | 重連 {stats['reconnect']} 次"
                        )
                        self.alert_sent = True

                # 重置斷線計數（如果超過重置時間）
                if self.first_disconnect_time:
                    time_since_first = (get_local_time() - self.first_disconnect_time).total_seconds()
                    if time_since_first > self.DISCONNECT_RESET_TIME:
                        logger.info(f"斷線計數重置（超過 {self.DISCONNECT_RESET_TIME} 秒）")
                        self.session_disconnect_count = 0
                        self.first_disconnect_time = None

        except asyncio.CancelledError:
            logger.info("守望任務被取消")
            raise
        except Exception as e:
            logger.error(f"守望任務發生錯誤: {e}", exc_info=True)

    @commands.Cog.listener()
    async def on_disconnect(self) -> None:
        """當靈魂斷續，幽幽子記錄迷失的瞬間"""
        now = get_local_time()
        self.session_disconnect_count += 1
        self.last_disconnect_time = now
        self.alert_sent = False

        if self.first_disconnect_time is None:
            self.first_disconnect_time = now

        logger.warning(
            f"🌸 幽幽子於 {format_timestamp(now)} 迷失（本次累計: {self.session_disconnect_count} 次）"
        )

        await self.save_event("disconnect", {
            "session_count": self.session_disconnect_count
        })

        if self.session_disconnect_count >= self.MAX_DISCONNECTS:
            time_span = (now - self.first_disconnect_time).total_seconds() if self.first_disconnect_time else 0
            stats = self.get_today_stats()
            await self.send_sakura_alert(
                f"🚨 **頻繁斷線警報!**\n"
                f"幽幽子在 **{time_span:.1f}** 秒內已迷失 **{self.session_disconnect_count}** 次，靈魂動盪!\n"
                f"⏰ 最後斷線時間: **{format_timestamp(now)}**\n"
                f"📊 今日累計: 斷線 {stats['disconnect']} 次"
            )

    @commands.Cog.listener()
    async def on_resumed(self) -> None:
        """當幽幽子重返現世，靈魂再次綻放"""
        now = get_local_time()
        self.session_reconnect_count += 1

        downtime = 0
        downtime_str = "未知"
        if self.last_disconnect_time:
            downtime = (now - self.last_disconnect_time).total_seconds()
            if downtime >= 60:
                minutes = int(downtime // 60)
                seconds = int(downtime % 60)
                downtime_str = f"{minutes}分{seconds}秒"
            else:
                downtime_str = f"{downtime:.1f}秒"

        logger.info(
            f"🌸 幽幽子於 {format_timestamp(now)} 重返現世 "
            f"（斷線時長: {downtime_str}, 本次累計重連: {self.session_reconnect_count} 次）"
        )

        await self.save_event("reconnect", {
            "downtime_seconds": downtime,
            "downtime_formatted": downtime_str,
            "session_count": self.session_reconnect_count
        })

        if downtime > self.MAX_DOWN_TIME:
            stats = self.get_today_stats()
            await self.send_sakura_alert(
                f"✅ **幽幽子已重返現世!**\n"
                f"⏱️ 斷線時長: **{downtime_str}**\n"
                f"⏰ 重連時間: **{format_timestamp(now)}**\n"
                f"📊 今日統計: 斷線 {stats['disconnect']} 次 | 重連 {stats['reconnect']} 次"
            )

        self.last_disconnect_time = None
        self.alert_sent = False

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        """當 Bot 完全就緒時的額外處理"""
        now = get_local_time()
        stats = self.get_today_stats()

        logger.info(
            f"🌸 Bot 完全就緒於 {format_timestamp(now)} "
            f"（今日統計: 斷線 {stats['disconnect']} 次, 重連 {stats['reconnect']} 次）"
        )


def setup(bot: discord.Bot):
    """將幽幽子的漂流守望模組載入 Discord 世界"""
    bot.add_cog(SakuraDrift(bot))
    logger.info("幽幽子的漂流守望模組已綻放")
