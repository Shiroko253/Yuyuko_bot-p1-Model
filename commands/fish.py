import discord
from discord.ext import commands

class Fish(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @commands.slash_command(name="fish", description="暫時無法使用該指令")
    async def fish(self, ctx: discord.ApplicationContext):
        embed = discord.Embed(
            title="🚧 指令維護中",
            description="很抱歉暫時無法使用該指令，目前還在製作和維護中，請稍後等待。",
            color=discord.Color.red()
        )
        embed.set_footer(text="很抱歉無法使用")
        await ctx.respond(embed=embed, ephemeral=True)

    @commands.slash_command(name="fish_backpack", description="暫時無法使用該指令")
    async def fish_backpack(self, ctx: discord.ApplicationContext):
        embed = discord.Embed(
            title="🚧 指令維護中",
            description="很抱歉暫時無法使用該指令，目前還在製作和維護中，請稍後等待。",
            color=discord.Color.red()
        )
        embed.set_footer(text="很抱歉無法使用")
        await ctx.respond(embed=embed, ephemeral=True)

    @commands.slash_command(name="fish_shop", description="暫時無法使用該指令")
    async def fish_shop(self, ctx: discord.ApplicationContext):
        embed = discord.Embed(
            title="🚧 指令維護中",
            description="很抱歉暫時無法使用該指令，目前還在製作和維護中，請稍後等待。",
            color=discord.Color.red()
        )
        embed.set_footer(text="很抱歉無法使用")
        await ctx.respond(embed=embed, ephemeral=True)

def setup(bot: discord.Bot):
    bot.add_cog(Fish(bot))