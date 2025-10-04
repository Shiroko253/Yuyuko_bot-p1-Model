import logging
import time
from discord.ext import commands
from utils.alerts import send_sakura_alert

logger = logging.getLogger("SakuraBot")

class SakuraDisconnectWatcher(commands.Cog):
    """監視幽幽子與現世的連結，記錄每一次的斷裂與重繫"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._last_disconnect_time = None

    @commands.Cog.listener()
    async def on_disconnect(self):
        """當幽幽子與 Discord 世界的連結中斷"""
        self._last_disconnect_time = time.time()
        
        # 更新斷線次數
        if hasattr(self.bot, 'data_manager'):
            self.bot.data_manager.bot_status["disconnect_count"] += 1
            self.bot.data_manager.bot_status["last_event_time"] = time.time()
            try:
                self.bot.data_manager._save_json(
                    f"{self.bot.data_manager.config_dir}/bot_status.json",
                    self.bot.data_manager.bot_status
                )
                logger.info("已記錄斷線事件，櫻花暫時凋零")
            except Exception as e:
                logger.error(f"保存斷線狀態失敗：{e}")
        else:
            logger.warning("data_manager 不存在，無法記錄斷線狀態")

        # 🌸 發送斷線警報
        try:
            await send_sakura_alert("⚠️ 幽幽子與現世的連結中斷，櫻花飄落...")
        except Exception as e:
            logger.error(f"發送斷線通知失敗：{e}")

    @commands.Cog.listener()
    async def on_resumed(self):
        """當幽幽子重新與 Discord 世界建立連結"""
        reconnect_time = time.time()
        downtime = reconnect_time - self._last_disconnect_time if self._last_disconnect_time else 0

        # 更新重連次數
        if hasattr(self.bot, 'data_manager'):
            self.bot.data_manager.bot_status["reconnect_count"] += 1
            self.bot.data_manager.bot_status["last_event_time"] = reconnect_time
            try:
                self.bot.data_manager._save_json(
                    f"{self.bot.data_manager.config_dir}/bot_status.json",
                    self.bot.data_manager.bot_status
                )
                logger.info(f"幽幽子已重返現世，斷線時長：{downtime:.2f} 秒")
            except Exception as e:
                logger.error(f"保存重連狀態失敗：{e}")

        # 🌸 發送重連通知
        try:
            if downtime > 0:
                await send_sakura_alert(f"🌸 幽幽子已歸來！斷線時長：{downtime:.2f} 秒，櫻花再度綻放。")
            else:
                await send_sakura_alert("🌸 幽幽子已歸來！櫻花再度綻放。")
        except Exception as e:
            logger.error(f"發送重連通知失敗：{e}")

def setup(bot: commands.Bot):
    bot.add_cog(SakuraDisconnectWatcher(bot))
    logger.info("幽幽子的斷線守護模組已綻放")
