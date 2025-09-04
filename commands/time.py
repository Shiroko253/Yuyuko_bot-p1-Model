import discord
from discord.ext import commands
import time

class Time(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        if not hasattr(self.bot, "last_activity_time"):
            self.bot.last_activity_time = time.time()

    @discord.slash_command(name="time", description="幽幽子報告機器人最後活動時間")
    async def time_command(self, ctx: discord.ApplicationContext):
        current_time = time.time()
        last_time = getattr(self.bot, "last_activity_time", current_time)
        idle_seconds = current_time - last_time

        if idle_seconds >= 86400:
            value = idle_seconds / 86400
            unit = "天"
            color = discord.Color.from_rgb(205, 133, 232)  # 冥界粉紫
            idle_phrase = "幽幽子都快餓扁了，等待賞花的亡魂們要耐心呀～"
        elif idle_seconds >= 3600:
            value = idle_seconds / 3600
            unit = "小時"
            color = discord.Color.orange()
            idle_phrase = "幽幽子在冥界小憩…要不要叫她吃點心？"
        else:
            value = idle_seconds / 60
            unit = "分鐘"
            color = discord.Color.green()
            idle_phrase = "幽幽子剛剛才活躍過哦，亡魂們不用等太久～"

        embed = discord.Embed(
            title="🌸 幽幽子的最後一次冥界活動 🌸",
            description=(
                f"機器人上次活動是 **{value:.2f} {unit}前**。\n"
                f"{idle_phrase}"
            ),
            color=color
        )
        embed.set_footer(text="幽幽子：閒著就賞花、吃點心、發呆吧～")

        await ctx.respond(embed=embed, ephemeral=True)

def setup(bot):
    bot.add_cog(Time(bot))