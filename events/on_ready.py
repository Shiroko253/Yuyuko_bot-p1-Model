import discord
from discord.ext import commands
import logging

class OnReady(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        logging.info(f"Logged in as {self.bot.user}")

        try:
            await self.bot.change_presence(
                status=discord.Status.dnd,
                activity=discord.Activity(type=discord.ActivityType.watching, name='最愛的人')
            )
            logging.info("Successfully set bot presence")
        except Exception as e:
            logging.error(f"Failed to set presence: {e}")

def setup(bot):
    bot.add_cog(OnReady(bot))
