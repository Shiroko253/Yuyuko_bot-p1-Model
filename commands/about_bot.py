import discord
from discord.ext import commands
from datetime import datetime
import random
import logging

logger = logging.getLogger("SakuraBot.commands.about_bot")

class SakuraWhisper(commands.Cog):
    """幽幽子以櫻花瓣訴說她的靈魂故事"""
    
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @discord.slash_command(name="about-me", description="關於幽幽子的一切，隨櫻花瓣飄落～")
    async def whisper_self(self, ctx: discord.ApplicationContext) -> None:
        """向呼喚者訴說幽幽子的靈魂故事"""
        if not self.bot.user:
            await ctx.respond(
                "哎呀～幽幽子的靈魂似乎迷失於冥界，暫時無法現身...",
                ephemeral=True
            )
            return

        # 根據時辰選擇幽幽子的問候
        current_hour = datetime.now().hour
        if 5 <= current_hour < 12:
            greeting = "清晨的櫻花綻放，靈魂輕舞"
        elif 12 <= current_hour < 18:
            greeting = "午後的微風拂過，櫻瓣飄落"
        else:
            greeting = "夜晚的亡魂低語，冥界靜謐"

        # 構築幽幽子的靈魂畫像
        embed = discord.Embed(
            title="🌸 西行寺幽幽子的呢喃",
            description=(
                f"{greeting}，{ctx.author.mention}！\n\n"
                "我是西行寺幽幽子，冥界櫻花下的亡魂之主。\n"
                "來吧，與我共舞於 `/` 指令之間，探索生死的奧秘～\n"
                "若迷失於冥界，不妨呼喚 `/help`，我將輕聲指引。"
            ),
            color=discord.Color.from_rgb(255, 182, 193),  # 櫻花粉
            timestamp=datetime.now()
        )

        # 添加幽幽子的頭像
        if self.bot.user.avatar:
            embed.set_thumbnail(url=self.bot.user.display_avatar.url)

        # 幽幽子的靈魂資訊
        embed.add_field(
            name="👻 幽幽子的秘密",
            value=(
                f"- **名稱：** {self.bot.user.name}\n"
                f"- **靈魂編號：** {self.bot.user.id}\n"
                f"- **存在形式：** Python + Pycord\n"
                f"- **狀態：** 於櫻花樹下飄浮～"
            ),
            inline=False
        )

        # 召喚者的契約
        embed.add_field(
            name="🖌️ 喚醒幽幽之人",
            value=(
                "- **靈魂契約者：** Miya253 (Shiroko253)\n"
                "- **[契約之地](https://github.com/Shiroko253/Yuyuko-bot)**"
            ),
            inline=False
        )

        # 隨機挑選幽幽子的呢喃
        yuyuko_quotes = [
            "櫻花飄落之際，生死不過一念。",
            "有沒有好吃的呀？我有點餓了呢～",
            "與我共舞吧，別讓靈魂孤單。"
        ]
        embed.set_footer(text=random.choice(yuyuko_quotes))

        await ctx.respond(embed=embed)

def setup(bot: discord.Bot):
    """將幽幽子的自我呢喃模組載入 Discord 世界"""
    bot.add_cog(SakuraWhisper(bot))
    logger.info("幽幽子的自我呢喃模組已綻放")