import discord
from discord.ext import commands
import time
import logging

logger = logging.getLogger("SakuraBot.Time")


class Time(commands.Cog):
    """
    🌸 幽幽子的時間感知 🌸
    讓幽幽子告訴你她最後一次活動的時間～
    """
    
    def __init__(self, bot: discord.Bot):
        self.bot = bot
        if not hasattr(self.bot, "last_activity_time"):
            self.bot.last_activity_time = time.time()
        logger.info("🕐 時間模組已載入")

    @discord.slash_command(
        name="time", 
        description="幽幽子報告機器人最後活動時間"
    )
    async def time_command(self, ctx: discord.ApplicationContext):
        """查詢機器人最後活動時間"""
        try:
            current_time = time.time()
            last_time = getattr(self.bot, "last_activity_time", current_time)
            idle_seconds = current_time - last_time
            
            # 根據閒置時間決定顯示單位和樣式
            if idle_seconds >= 86400:  # 1天以上
                value = idle_seconds / 86400
                unit = "天"
                color = discord.Color.from_rgb(205, 133, 232)  # 冥界粉紫
                emoji = "🌙"
                idle_phrase = "幽幽子都快餓扁了，等待賞花的亡魂們要耐心呀～"
                status = "長時間休眠中"
            elif idle_seconds >= 3600:  # 1小時以上
                value = idle_seconds / 3600
                unit = "小時"
                color = discord.Color.orange()
                emoji = "🌸"
                idle_phrase = "幽幽子在冥界小憩…要不要叫她吃點心？"
                status = "小憩中"
            elif idle_seconds >= 60:  # 1分鐘以上
                value = idle_seconds / 60
                unit = "分鐘"
                color = discord.Color.green()
                emoji = "✨"
                idle_phrase = "幽幽子剛剛才活躍過哦，亡魂們不用等太久～"
                status = "活躍中"
            else:  # 1分鐘以內
                value = idle_seconds
                unit = "秒"
                color = discord.Color.from_rgb(144, 238, 144)  # 淺綠色
                emoji = "⚡"
                idle_phrase = "幽幽子正在全力工作中！靈魂們請稍候～"
                status = "極度活躍"
            
            embed = discord.Embed(
                title=f"{emoji} 幽幽子的最後一次冥界活動 {emoji}",
                description=(
                    f"**狀態：** {status}\n"
                    f"**閒置時間：** {value:.2f} {unit}\n\n"
                    f"{idle_phrase}"
                ),
                color=color
            )
            
            # 添加額外資訊
            embed.add_field(
                name="📊 詳細數據",
                value=(
                    f"```yaml\n"
                    f"閒置秒數: {idle_seconds:.0f} 秒\n"
                    f"上次活動: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(last_time))}\n"
                    f"當前時間: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(current_time))}\n"
                    f"```"
                ),
                inline=False
            )
            
            embed.set_footer(
                text="幽幽子：閒著就賞花、吃點心、發呆吧～",
                icon_url=self.bot.user.avatar.url if self.bot.user and self.bot.user.avatar else None
            )
            embed.timestamp = discord.utils.utcnow()
            
            await ctx.respond(embed=embed, ephemeral=True)
            logger.info(f"👤 用戶 {ctx.user.name} 查詢了機器人活動時間（閒置 {idle_seconds:.0f} 秒）")
            
        except Exception as e:
            logger.error(f"❌ 時間查詢失敗: {e}", exc_info=True)
            try:
                error_embed = discord.Embed(
                    title="🌸 時間查詢失敗",
                    description="幽幽子在查看時間時迷糊了...請稍後再試～",
                    color=discord.Color.red()
                )
                error_embed.set_footer(text="冥界的時間有時也會迷路呢～")
                await ctx.respond(embed=error_embed, ephemeral=True)
            except Exception:
                pass


def setup(bot: discord.Bot):
    """載入時間模組"""
    bot.add_cog(Time(bot))
    logger.info("🕐 時間 Cog 已成功載入")
