import discord
from discord.ext import commands
from discord.ui import View, Button
import random

active_giveaways = {}

class GiveawayView(View):
    def __init__(self, bot, guild_id, prize, duration, timeout=None):
        super().__init__(timeout=timeout)
        self.bot = bot
        self.guild_id = guild_id
        self.prize = prize
        self.participants = set()
        self.duration = duration

    async def on_timeout(self):
        await self.end_giveaway()

    async def end_giveaway(self):
        if self.guild_id not in active_giveaways:
            return

        giveaway = active_giveaways.pop(self.guild_id)
        channel = self.bot.get_channel(giveaway["channel_id"])
        if not channel:
            return

        if not self.participants:
            await channel.send("😢 抽獎活動結束，沒有有效的參與者。")
            return

        winner = random.choice(list(self.participants))
        embed = discord.Embed(
            title="🎉 抽獎活動結束 🎉",
            description=(
                f"**獎品**: {self.prize}\n"
                f"**獲勝者**: {winner.mention}\n\n"
                "感謝所有參與者！"
            ),
            color=discord.Color.green()
        )
        await channel.send(embed=embed)

    @discord.ui.button(label="參加抽獎", style=discord.ButtonStyle.green)
    async def participate(self, button: Button, interaction: discord.Interaction):
        if interaction.user in self.participants:
            await interaction.response.send_message("⚠️ 你已經參加過了！", ephemeral=True)
        else:
            self.participants.add(interaction.user)
            await interaction.response.send_message("✅ 你已成功參加抽獎！", ephemeral=True)

    @discord.ui.button(label="結束抽獎", style=discord.ButtonStyle.red, row=1)
    async def end_giveaway_button(self, button: Button, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ 只有管理員可以結束抽獎活動。", ephemeral=True)
            return

        await self.end_giveaway()
        await interaction.response.send_message("🔔 抽獎活動已結束！", ephemeral=True)
        self.stop()

class Giveaway(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(name="start_giveaway", description="開始抽獎活動")
    async def start_giveaway(
        self,
        ctx: discord.ApplicationContext,
        duration: int = discord.Option(..., description="抽獎持續時間（秒）"),
        prize: str = discord.Option(..., description="獎品名稱")
    ):
        if not ctx.user.guild_permissions.administrator:
            await ctx.respond("❌ 你需要管理員權限才能使用此指令。", ephemeral=True)
            return

        if ctx.guild.id in active_giveaways:
            await ctx.respond("⚠️ 已經有正在進行的抽獎活動。", ephemeral=True)
            return

        embed = discord.Embed(
            title="🎉 抽獎活動開始了！ 🎉",
            description=(
                f"**獎品**: {prize}\n"
                f"**活動持續時間**: {duration} 秒\n\n"
                "點擊下方的按鈕參與抽獎！"
            ),
            color=discord.Color.gold()
        )
        embed.set_footer(text="祝你好運！")

        view = GiveawayView(self.bot, ctx.guild.id, prize, duration, timeout=duration)

        await ctx.respond(embed=embed, view=view)
        # 拿到已發送的訊息
        message = await ctx.interaction.original_response()

        active_giveaways[ctx.guild.id] = {
            "message_id": message.id,
            "channel_id": ctx.channel_id,
            "prize": prize,
            "view": view
        }

def setup(bot):
    bot.add_cog(Giveaway(bot))
