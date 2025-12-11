import discord
from discord.ext import commands
from datetime import datetime
import random
import logging
import time

logger = logging.getLogger("SakuraBot.commands.about_bot")


class SakuraWhisper(commands.Cog):
    """幽幽子以櫻花瓣訴說她的靈魂故事"""
    
    def __init__(self, bot: discord.Bot):
        self.bot = bot
        self.yuyuko_quotes = [
            "櫻花飄落之際，生死不過一念。",
            "有沒有好吃的呀？我有點餓了呢～",
            "與我共舞吧，別讓靈魂孤單。",
            "冥界的春天，是最美的呢。",
            "妖夢～今天的點心準備好了嗎？",
            "生與死，如櫻花綻放與凋零。",
            "啊啊～又是悠閒的一天♪"
        ]
    
    @discord.slash_command(
        name="about-me",
        description="關於幽幽子的一切，隨櫻花瓣飄落～"
    )
    async def whisper_self(self, ctx: discord.ApplicationContext) -> None:
        """向呼喚者訴說幽幽子的靈魂故事"""
        if not self.bot.user:
            await ctx.respond(
                "哎呀～幽幽子的靈魂似乎迷失於冥界，暫時無法現身...",
                ephemeral=True
            )
            return
        
        # 計算幽幽子的運行時間
        uptime_seconds = time.time() - getattr(self.bot, "start_time", time.time())
        uptime_str = self._format_uptime(uptime_seconds)
        
        # 根據時辰選擇幽幽子的問候
        greeting = self._get_greeting()
        
        # 構築幽幽子的靈魂畫像
        embed = discord.Embed(
            title="🌸 西行寺幽幽子的呢喃",
            description=(
                f"{greeting}，{ctx.author.mention}！\n\n"
                "> *我是西行寺幽幽子，冥界櫻花下的亡魂之主。*\n"
                "> *來吧，與我共舞於 `/` 指令之間，探索生死的奧秘～*\n\n"
                "若迷失於冥界，不妨呼喚 `/help`，我將輕聲指引。"
            ),
            color=discord.Color.from_rgb(255, 182, 193),  # 櫻花粉
            timestamp=datetime.now()
        )
        
        # 添加幽幽子的頭像
        if self.bot.user.avatar:
            embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        
        # 幽幽子的基本資訊
        embed.add_field(
            name="👻 幽幽子的秘密",
            value=(
                f"```yaml\n"
                f"名稱: {self.bot.user.name}\n"
                f"靈魂編號: {self.bot.user.id}\n"
                f"存在形式: Python + Pycord\n"
                f"已甦醒時長: {uptime_str}\n"
                f"守護的花園: {len(self.bot.guilds)} 個伺服器\n"
                f"感知的靈魂: {sum(g.member_count for g in self.bot.guilds)} 位\n"
                f"```"
            ),
            inline=False
        )
        
        # 召喚者的契約
        embed.add_field(
            name="🖌️ 喚醒幽幽之人",
            value=(
                "**靈魂契約者:** Miya253 (Shiroko253)\n"
                "**契約之地:** [GitHub Repository](https://github.com/Shiroko253/Yuyuko-bot)\n"
                "**創建時刻:** <t:1623245700:F>"
            ),
            inline=False
        )
        
        # 幽幽子的能力
        embed.add_field(
            name="✨ 幽幽子的能力",
            value=(
                "```\n"
                "🎮 遊戲系統 | 💰 經濟系統\n"
                "🤖 AI 對話  | 🎭 彩蛋互動\n"
                "📊 統計功能 | 🌸 更多探索中...\n"
                "```"
            ),
            inline=False
        )
        
        # 隨機挑選幽幽子的呢喃
        embed.set_footer(
            text=f"💭 {random.choice(self.yuyuko_quotes)}",
            icon_url=self.bot.user.avatar.url if self.bot.user.avatar else None
        )
        
        # 添加裝飾圖片 (可選)
        # embed.set_image(url="https://example.com/yuyuko_banner.png")
        
        await ctx.respond(embed=embed)
        logger.info(f"{ctx.author} ({ctx.author.id}) 查看了 about-me")
    
    @discord.slash_command(
        name="stats",
        description="查看幽幽子的靈魂統計數據"
    )
    async def stats(self, ctx: discord.ApplicationContext) -> None:
        """顯示 Bot 的運行統計"""
        if not self.bot.user:
            await ctx.respond("統計數據迷失於冥界...", ephemeral=True)
            return
        
        # 計算運行時間
        uptime_seconds = time.time() - getattr(self.bot, "start_time", time.time())
        uptime_str = self._format_uptime(uptime_seconds)
        
        # 計算延遲
        latency_ms = round(self.bot.latency * 1000, 2)
        
        # 獲取統計數據
        total_guilds = len(self.bot.guilds)
        total_users = sum(g.member_count for g in self.bot.guilds)
        total_channels = sum(len(g.channels) for g in self.bot.guilds)
        
        # 獲取斷線統計 (如果有的話)
        disconnect_count = 0
        reconnect_count = 0
        if hasattr(self.bot, 'data_manager'):
            bot_status = self.bot.data_manager.bot_status
            disconnect_count = bot_status.get("disconnect_count", 0)
            reconnect_count = bot_status.get("reconnect_count", 0)
        
        embed = discord.Embed(
            title="📊 幽幽子的靈魂數據",
            description="冥界的記憶與統計",
            color=discord.Color.from_rgb(138, 43, 226),  # 紫色
            timestamp=datetime.now()
        )
        
        if self.bot.user.avatar:
            embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        
        # 運行狀態
        embed.add_field(
            name="⚡ 運行狀態",
            value=(
                f"```yaml\n"
                f"運行時長: {uptime_str}\n"
                f"延遲: {latency_ms} ms\n"
                f"斷線次數: {disconnect_count}\n"
                f"重連次數: {reconnect_count}\n"
                f"```"
            ),
            inline=True
        )
        
        # 伺服器統計
        embed.add_field(
            name="🏰 守護範圍",
            value=(
                f"```yaml\n"
                f"伺服器: {total_guilds}\n"
                f"頻道: {total_channels}\n"
                f"用戶: {total_users}\n"
                f"```"
            ),
            inline=True
        )
        
        # 系統資訊
        embed.add_field(
            name="🖥️ 靈魂構成",
            value=(
                f"```yaml\n"
                f"語言: Python 3.x\n"
                f"框架: Pycord\n"
                f"主機: Linux\n"
                f"```"
            ),
            inline=True
        )
        
        embed.set_footer(text="數據實時更新中...")
        
        await ctx.respond(embed=embed)
        logger.info(f"{ctx.author} ({ctx.author.id}) 查看了統計數據")
    

    def _format_uptime(self, seconds: float) -> str:
        """格式化運行時間"""
        days = int(seconds // 86400)
        hours = int((seconds % 86400) // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        parts = []
        if days > 0:
            parts.append(f"{days}天")
        if hours > 0:
            parts.append(f"{hours}小時")
        if minutes > 0:
            parts.append(f"{minutes}分鐘")
        if secs > 0 or not parts:
            parts.append(f"{secs}秒")
        
        return " ".join(parts)
    
    def _get_greeting(self) -> str:
        """根據時間獲取問候語"""
        current_hour = datetime.now().hour
        
        greetings = {
            (5, 8): "清晨的櫻花初綻，露珠輕顫",
            (8, 12): "晨光灑落白玉樓，靈魂甦醒",
            (12, 14): "正午的陽光溫暖，櫻瓣紛飛",
            (14, 18): "午後的微風拂過，時光悠閒",
            (18, 20): "黃昏的餘暉染紅天際，靜謐降臨",
            (20, 23): "夜幕低垂，亡魂低語徘徊",
            (23, 5): "深夜的冥界寂靜，唯有櫻花作伴"
        }
        
        for (start, end), greeting in greetings.items():
            if start <= current_hour < end or (start > end and (current_hour >= start or current_hour < end)):
                return greeting
        
        return "櫻花飄落的時刻"


def setup(bot: discord.Bot):
    """將幽幽子的自我呢喃模組載入 Discord 世界"""
    bot.add_cog(SakuraWhisper(bot))
    logger.info("幽幽子的自我呢喃模組已綻放")
