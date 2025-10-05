import discord
import random
import logging
import time  # ✅ 新增：用於 uptime 計算
from discord.ext import commands
from datetime import datetime
from typing import List, Dict, Any

logger = logging.getLogger("SakuraBot.commands.about_bot")

class SakuraWhisper(commands.Cog):
    """幽幽子以櫻花瓣訴說她的靈魂故事"""
    
    def __init__(self, bot: discord.Bot):
        self.bot = bot
        self._init_quotes()
        self._init_colors()
        self._init_times()

    def _init_quotes(self) -> None:
        self.quotes = [
            "🌸 櫻花飄落之際，生死不過一念。",
            "👻 有沒有好吃的呀？我有點餓了呢～",
            "🎭 與我共舞吧，別讓靈魂孤單。",
            "🌙 冥界之夜，最適合說鬼故事了～",
            "🍵 來杯茶吧，一起聊聊天？",
            "💫 靈魂的光芒，永不熄滅～"
        ]
        
        self.greetings = {
            "morning": "🌅 清晨的櫻花綻放，靈魂輕舞",
            "afternoon": "☀️ 午後的微風拂過，櫻瓣飄落", 
            "evening": "🌙 夜晚的亡魂低語，冥界靜謐",
            "night": "🌙 深夜的冥界，更加神秘～"
        }

    def _init_colors(self) -> None:
        self.colors = {
            "cherry_blossom": discord.Color.from_rgb(255, 182, 193),
            "sakura_pink": discord.Color.from_rgb(255, 105, 180),
            "ghost_white": discord.Color.from_rgb(248, 248, 255),
            "midnight_purple": discord.Color.from_rgb(75, 0, 130)
        }

    def _init_times(self) -> None:
        self.time_ranges = {
            "morning": (5, 12),
            "afternoon": (12, 18),
            "evening": (18, 21),
            "night": (21, 24),
            "deep_night": (0, 5)
        }

    def _get_time_greeting(self) -> str:
        current_hour = datetime.now().hour
        for period, (start, end) in self.time_ranges.items():
            if start <= current_hour < end:
                return self.greetings.get(period, "🌸 時辰已至，幽靈現身")
        return "🌸 時辰已至，幽靈現身"

    def _create_bot_embed(self, ctx: discord.ApplicationContext) -> discord.Embed:
        greeting = self._get_time_greeting()
        embed = discord.Embed(
            title="🌸 西行寺幽幽子的呢喃",
            description=(
                f"{greeting}，{ctx.author.mention}！\n\n"
                "我是西行寺幽幽子，冥界櫻花下的亡魂之主。\n"
                "來吧，與我共舞於 `/` 指令之間，探索生死的奧秘～\n"
                "若迷失於冥界，不妨呼喚 `/help`，我將輕聲指引。"
            ),
            color=self.colors["cherry_blossom"],
            timestamp=datetime.now()
        )

        if self.bot.user.avatar:
            embed.set_thumbnail(url=self.bot.user.display_avatar.url)

        embed.add_field(
            name="👻 幽幽子的靈魂資訊",
            value=(
                f"**👤 名稱：** {self.bot.user.name}\n"
                f"**🔢 機器人ID：** `{self.bot.user.id}`\n"
                f"**⚡ 開發語言：** Python + Pycord\n"
                f"**✨ 運行狀態：** 🟢 在線\n"  # ✅ slash command 時一定在線
                f"**📊 伺服器數量：** {len(self.bot.guilds)} 個\n"
                f"**👥 用戶數量：** {len(self.bot.users)} 位"
            ),
            inline=False
        )

        embed.add_field(
            name="🖌️ 契約之人",
            value=(
                "**👤 開發者：** `Miya253 (Shiroko253)`\n"
                "**🔗 [GitHub 契約之地](https://github.com/Shiroko253/Yuyuko_bot)**\n"      # ✅ 移除空格
                "**💬 [Discord 交流群](https://discord.gg/2eRTxPAx3z)**"                     # ✅ 移除空格
            ),
            inline=False
        )

        embed.set_footer(text=random.choice(self.quotes))
        return embed

    @discord.slash_command(name="about-me", description="關於幽幽子的一切，隨櫻花瓣飄落～")
    async def whisper_self(self, ctx: discord.ApplicationContext) -> None:
        try:
            if not self.bot.user:
                await ctx.respond("🌸 幽幽子的靈魂似乎迷失於冥界，暫時無法現身...", ephemeral=True)
                return
            embed = self._create_bot_embed(ctx)
            await ctx.respond(embed=embed)
        except discord.DiscordException as e:
            logger.error(f"About command error: {e}")
            await ctx.respond("🌸 幽幽子的靈魂出現了異常...請稍後再試～", ephemeral=True)

    @discord.slash_command(name="stats", description="查看幽幽子的狀態統計")
    async def show_stats(self, ctx: discord.ApplicationContext) -> None:
        try:
            # ✅ 修復：正確計算運行時間
            if hasattr(self.bot, 'start_time'):
                uptime_seconds = time.time() - self.bot.start_time
                days = int(uptime_seconds // 86400)
                hours = int((uptime_seconds % 86400) // 3600)
                minutes = int((uptime_seconds % 3600) // 60)
                uptime_str = f"{days}天 {hours}小時 {minutes}分"
            else:
                uptime_str = "未知"

            embed = discord.Embed(
                title="📊 幽幽子的狀態報告",
                color=self.colors["sakura_pink"],
                timestamp=datetime.now()
            )

            embed.add_field(
                name="📈 基本數據",
                value=(
                    f"**📊 伺服器數：** {len(self.bot.guilds)}\n"
                    f"**👥 用戶數：** {len(self.bot.users)}\n"
                    f"**🤖 機器人數：** {len([m for g in self.bot.guilds for m in g.members if m.bot])}\n"
                    f"**⏰ 運行時間：** {uptime_str}"
                ),
                inline=False
            )

            total_commands = len(self.bot.commands)
            slash_commands = len([c for c in self.bot.commands if hasattr(c, 'callback')])
            embed.add_field(
                name="🔧 指令資訊",
                value=(
                    f"**🔢 總指令數：** {total_commands}\n"
                    f"**✨ 斜線指令：** {slash_commands}\n"
                    f"**📝 文字指令：** {total_commands - slash_commands}"
                ),
                inline=False
            )

            await ctx.respond(embed=embed)

        except Exception as e:
            logger.error(f"Stats command error: {e}")
            await ctx.respond("🌸 狀態查詢出現問題...", ephemeral=True)

def setup(bot: discord.Bot) -> None:
    bot.add_cog(SakuraWhisper(bot))
    logger.info("🌸 幽幽子的自我呢喃模組已綻放")
