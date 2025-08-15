import discord
from discord.ext import commands
from datetime import datetime
import random

class AboutMe(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @commands.slash_command(name="about-me", description="關於幽幽子的一切～")
    async def about_me(self, ctx: discord.ApplicationContext):
        if not self.bot.user:
            await ctx.respond(
                "哎呀～幽幽子的靈魂似乎飄散了，暫時無法現身哦。",
                ephemeral=True
            )
            return

        current_hour = datetime.now().hour
        if 5 <= current_hour < 12:
            greeting = "清晨的櫻花正綻放"
        elif 12 <= current_hour < 18:
            greeting = "午後的微風輕拂花瓣"
        else:
            greeting = "夜晚的亡魂低語陣陣"

        embed = discord.Embed(
            title="🌸 關於幽幽子",
            description=(
                f"{greeting}，{ctx.author.mention}！\n\n"
                "我是西行寺幽幽子，亡魂之主，櫻花下的舞者。\n"
                "來吧，使用 `/` 指令與我共舞，探索生與死的奧秘～\n"
                "若迷失方向，不妨試試 `/help`，我會輕聲指引你。"
            ),
            color=discord.Color.from_rgb(255, 182, 193),
            timestamp=datetime.now()
        )

        if self.bot.user.avatar:
            embed.set_thumbnail(url=self.bot.user.display_avatar.url)

        embed.add_field(
            name="👻 幽幽子的秘密",
            value=(
                f"- **名稱：** {self.bot.user.name}\n"
                f"- **靈魂編號：** {self.bot.user.id}\n"
                f"- **存在形式：** Python + Pycord\n"
                f"- **狀態：** 飄浮中～"
            ),
            inline=False
        )

        embed.add_field(
            name="🖌️ 召喚我之人",
            value=(
                "- **靈魂契約者：** Miya253 (Shiroko253)\n"
                "- **[契約之地](https://github.com/Shiroko253/Yuyuko-bot)**"
            ),
            inline=False
        )

        yuyuko_quotes = [
            "櫻花飄落之際，生死不過一念。",
            "有沒有好吃的呀？我有點餓了呢～",
            "與我共舞吧，別讓靈魂孤單。"
        ]
        embed.set_footer(text=random.choice(yuyuko_quotes))

        await ctx.respond(embed=embed)

def setup(bot: discord.Bot):
    bot.add_cog(AboutMe(bot))