import discord
from discord.ext import commands

class Help(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @commands.slash_command(name="help", description="暫時無法使用該指令")
    async def help(self, ctx: discord.ApplicationContext):
        embed = discord.Embed(
            title="🚧 指令維護中",
            description="很抱歉暫時無法使用該指令，目前還在製作和維護中，請稍後等待。",
            color=discord.Color.red()
        )
        embed.set_footer(text="很抱歉無法使用")
        await ctx.respond(embed=embed, ephemeral=True)

def setup(bot: discord.Bot):
    bot.add_cog(Help(bot))