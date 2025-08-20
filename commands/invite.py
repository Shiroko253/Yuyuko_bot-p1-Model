import discord
from discord.ext import commands
from urllib.parse import urlencode
import random

class InviteCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(name="invite", description="生成幽幽子的邀請鏈接，邀她共舞於你的伺服器")
    async def invite(self, ctx: discord.ApplicationContext):
        if not self.bot.user:
            await ctx.respond(
                "哎呀～幽幽子的靈魂似乎尚未降臨此處，請稍後再試哦。",
                ephemeral=True
            )
            return

        client_id = self.bot.user.id
        # 設置推薦權限，方便管理
        permissions = discord.Permissions(
            manage_channels=True,
            manage_roles=True,
            ban_members=True,
            kick_members=True
        )
        query = {
            "client_id": client_id,
            "permissions": permissions.value,
            "scope": "bot applications.commands"
        }
        invite_url = f"https://discord.com/oauth2/authorize?{urlencode(query)}"

        embed = discord.Embed(
            title="邀請幽幽子降臨你的伺服器",
            description=(
                "幽幽子輕拂櫻花，緩緩飄至你的身旁。\n"
                "與她共賞生死輪迴，品味片刻寧靜吧～\n\n"
                f"🌸 **[點此邀請幽幽子]({invite_url})** 🌸"
            ),
            color=discord.Color.from_rgb(255, 182, 193)
        )

        if self.bot.user.avatar:
            embed.set_thumbnail(url=self.bot.user.display_avatar.url)

        yuyuko_quotes = [
            "生與死不過一線之隔，何不輕鬆以對？",
            "櫻花散落之時，便是與我共舞之刻。",
            "肚子餓了呢～有沒有好吃的供品呀？"
        ]
        embed.set_footer(text=random.choice(yuyuko_quotes))

        await ctx.respond(embed=embed)

def setup(bot):
    bot.add_cog(InviteCog(bot))
