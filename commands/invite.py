import discord
from discord.ext import commands
from urllib.parse import urlencode
import random
import logging

logger = logging.getLogger("SakuraBot.Invite")


class InviteCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(
        name="invite",
        description="生成幽幽子的邀請鏈接，邀她共舞於你的伺服器"
    )
    async def invite(self, ctx: discord.ApplicationContext):
        if not self.bot.user:
            logger.warning("Bot user 未加載，幽幽子尚未降臨。")
            await ctx.respond(
                "哎呀～幽幽子的靈魂似乎尚未降臨此處，請稍後再試哦。",
                ephemeral=True
            )
            return

        client_id = self.bot.user.id

        # 補齊 Bot 正常運作所需的基本權限
        permissions = discord.Permissions(
            # 基本訊息能力
            read_messages=True,
            send_messages=True,
            send_messages_in_threads=True,
            embed_links=True,
            attach_files=True,
            read_message_history=True,
            add_reactions=True,
            use_external_emojis=True,
            # 管理能力
            manage_messages=True,
            manage_channels=True,
            manage_roles=True,
            ban_members=True,
            kick_members=True,
            moderate_members=True,
        )

        query = {
            "client_id": client_id,
            "permissions": permissions.value,
            "scope": "bot applications.commands"
        }
        invite_url = f"https://discord.com/oauth2/authorize?{urlencode(query)}"

        embed = discord.Embed(
            title="🌸 邀請幽幽子降臨你的伺服器 🌸",
            description=(
                "幽幽子輕拂櫻花，緩緩飄至你的身旁～\n"
                "與她共賞生死輪迴，品味片刻寧靜吧～\n\n"
                f"🌸 **[點此邀請幽幽子]({invite_url})** 🌸"
            ),
            color=discord.Color.from_rgb(255, 182, 193)
        )
        
        # [Debug 優化] 移除多餘的 if 判斷，直接使用 display_avatar
        # 確保無論 Bot 是否有自訂大頭貼，都能完美顯示縮圖 (若無自訂則顯示 Discord 預設頭貼)
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)

        yuyuko_quotes = [
            "生與死不過一線之隔，何不輕鬆以對？",
            "櫻花散落之時，便是與我共舞之刻。",
            "肚子餓了呢～有沒有好吃的供品呀？",
            "幽幽子在冥界等你，櫻花樹下一起賞舞吧～",
            "邀請幽幽子，靈魂也會變得輕盈哦！"
        ]
        embed.set_footer(text=random.choice(yuyuko_quotes))

        await ctx.respond(embed=embed)


def setup(bot):
    bot.add_cog(InviteCog(bot))
    logger.info("Invite Cog 已載入，櫻花邀請函準備發送～")
