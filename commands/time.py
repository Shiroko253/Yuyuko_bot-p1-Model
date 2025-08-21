import discord
from discord.ext import commands
import time

class Time(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        if not hasattr(self.bot, "last_activity_time"):
            self.bot.last_activity_time = time.time()

    @discord.slash_command(name="time", description="獲取機器人最後活動時間")
    async def time_command(self, ctx: discord.ApplicationContext):
        current_time = time.time()
        last_time = getattr(self.bot, "last_activity_time", current_time)
        idle_seconds = current_time - last_time
import discord
from discord.ext import commands
import time

class Time(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        if not hasattr(self.bot, "last_activity_time"):
            self.bot.last_activity_time = time.time()

    @discord.slash_command(name="time", description="獲取機器人最後活動時間")
    async def time_command(self, ctx: discord.ApplicationContext):
        current_time = time.time()
        last_time = getattr(self.bot, "last_activity_time", current_time)
        idle_seconds = current_time - last_time

        if idle_seconds >= 86400:
            value = idle_seconds / 86400
            unit = "天"
            color = discord.Color.dark_blue()
        elif idle_seconds >= 3600:
            value = idle_seconds / 3600
            unit = "小時"
            color = discord.Color.orange()
        else:
            value = idle_seconds / 60
            unit = "分鐘"
            color = discord.Color.green()

        embed = discord.Embed(
            title="最後一次活動時間",
            description=f"機器人上次活動時間是 **{value:.2f} {unit}前**。",
            color=color
        )
        embed.set_footer(text="製作:'死亡協會'")

        await ctx.respond(embed=embed, ephemeral=True)

def setup(bot):
    bot.add_cog(Time(bot))
        if idle_seconds >= 86400:
            value = idle_seconds / 86400
            unit = "天"
            color = discord.Color.dark_blue()
        elif idle_seconds >= 3600:
            value = idle_seconds / 3600
            unit = "小時"
            color = discord.Color.orange()
        else:
            value = idle_seconds / 60
            unit = "分鐘"
            color = discord.Color.green()

        embed = discord.Embed(
            title="最後一次活動時間",
            description=f"機器人上次活動時間是 **{value:.2f} {unit}前**。",
            color=color
        )
        embed.set_footer(text="製作:'死亡協會'")

        await ctx.respond(embed=embed, ephemeral=True)

def setup(bot):
    bot.add_cog(Time(bot))
