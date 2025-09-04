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
            embed = discord.Embed(
                title="🌸 抽獎活動結束 🌸",
                description="哎呀～冥界今天沒有靈魂參與抽獎呢，下次再來吧！",
                color=discord.Color.from_rgb(205, 133, 232)
            )
            embed.set_footer(text="幽幽子：好想吃點心…")
            await channel.send(embed=embed)
            return

        winner_id = random.choice(list(self.participants))
        winner = channel.guild.get_member(winner_id)
        winner_mention = winner.mention if winner else f"<@{winner_id}>"

        embed = discord.Embed(
            title="🌸 冥界抽獎結果公布 🌸",
            description=(
                f"**獎品**: {self.prize}\n"
                f"**幸運靈魂**: {winner_mention}\n\n"
                "幽幽子：恭喜你被櫻花選中！賞花、吃點心，亡魂也會幸福～"
            ),
            color=discord.Color.from_rgb(205, 133, 232)
        )
        embed.set_footer(text="幽幽子：感謝所有亡魂的參與～")
        await channel.send(embed=embed)

    @discord.ui.button(label="參加抽獎（冥界賞花）", style=discord.ButtonStyle.primary, emoji="🌸")
    async def participate(self, button: Button, interaction: discord.Interaction):
        user_id = interaction.user.id
        if user_id in self.participants:
            await interaction.response.send_message("⚠️ 你已經參加過啦！幽幽子都記得呢～", ephemeral=True)
        else:
            self.participants.add(user_id)
            await interaction.response.send_message("✅ 你已成為冥界抽獎參加者！祝你櫻花降臨，好運連連～", ephemeral=True)

    @discord.ui.button(label="結束抽獎", style=discord.ButtonStyle.red, emoji="🔚", row=1)
    async def end_giveaway_button(self, button: Button, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ 只有群組主人或管理員才能結束抽獎哦～", ephemeral=True)
            return

        await self.end_giveaway()
        await interaction.response.send_message("🔔 冥界抽獎活動已結束！感謝大家參與～", ephemeral=True)
        self.stop()

class Giveaway(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(name="start_giveaway", description="開啟幽幽子的冥界抽獎活動")
    async def start_giveaway(
        self,
        ctx: discord.ApplicationContext,
        duration: int = discord.Option(description="抽獎持續時間（秒）"),
        prize: str = discord.Option(description="獎品名稱")
    ):
        if not ctx.user.guild_permissions.administrator:
            await ctx.respond("❌ 你需要管理員權限才能開啟冥界抽獎哦～", ephemeral=True)
            return

        if ctx.guild.id in active_giveaways:
            await ctx.respond("⚠️ 冥界已經有一場抽獎正在進行！", ephemeral=True)
            return

        embed = discord.Embed(
            title="🌸 幽幽子的冥界抽獎開始啦！🌸",
            description=(
                f"**獎品**: {prize}\n"
                f"**活動持續時間**: {duration} 秒\n\n"
                "快來參加吧！幽幽子正在賞花等待幸運亡魂降臨～"
            ),
            color=discord.Color.from_rgb(205, 133, 232)
        )
        embed.set_footer(text="幽幽子：賞花、吃點心、抽獎三連發！祝大家好運～")

        view = GiveawayView(self.bot, ctx.guild.id, prize, duration, timeout=duration)

        await ctx.respond(embed=embed, view=view)
        message = await ctx.interaction.original_response()

        active_giveaways[ctx.guild.id] = {
            "message_id": message.id,
            "channel_id": ctx.channel_id,
            "prize": prize,
            "view": view
        }

def setup(bot):
    bot.add_cog(Giveaway(bot))