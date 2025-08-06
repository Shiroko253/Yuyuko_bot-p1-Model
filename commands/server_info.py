import discord
from discord.ext import commands
from discord.ui import Button, View
from discord import Interaction
import random
import logging  # ✅ 加入 logging 模組

class ServerInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(name="server_info", description="幽幽子為你窺探群組的靈魂資訊～")
    async def server_info(self, interaction: Interaction):
        guild = interaction.guild
        if guild is None:
            await interaction.response.send_message(
                "哎呀～這個地方沒有靈魂聚集，無法窺探哦。請在群組中使用此指令～",
                ephemeral=True
            )
            return

        guild_name = guild.name
        guild_id = guild.id
        member_count = guild.member_count
        bot_count = sum(1 for member in guild.members if member.bot) if guild.members else "未知"
        role_count = len(guild.roles)
        created_at = f"<t:{int(guild.created_at.timestamp())}:F>"
        guild_icon_url = guild.icon.url if guild.icon else None
        owner = guild.owner

        embed = discord.Embed(
            title="🌸 幽幽子窺探的群組靈魂 🌸",
            description=(
                f"我是西行寺幽幽子，亡魂之主，現在為你揭示群組「{guild_name}」的靈魂～\n"
                "讓我們來看看這片土地的命運吧…"
            ),
            color=discord.Color.from_rgb(255, 182, 193)
        )

        embed.add_field(name="群組之名", value=guild_name, inline=False)
        embed.add_field(name="靈魂領主", value=f"{owner}（ID: {owner.id}）", inline=False)
        embed.add_field(name="靈魂聚集之地", value=guild_id, inline=False)
        embed.add_field(name="靈魂數量", value=f"{member_count} (機械之魂: {bot_count})", inline=True)
        embed.add_field(name="身份之數", value=role_count, inline=True)
        embed.add_field(name="此地誕生之日", value=created_at, inline=False)

        if guild_icon_url:
            embed.set_thumbnail(url=guild_icon_url)

        yuyuko_quotes = [
            "這片土地的靈魂真熱鬧…有沒有好吃的供品呀？",
            "櫻花下的群組，靈魂們的命運真是迷人～",
            "生與死的交界處，這裡的氣息讓我感到舒適呢。"
        ]
        embed.set_footer(text=random.choice(yuyuko_quotes))

        view = View(timeout=180)

        async def button_callback(button_interaction: Interaction):
            try:
                if guild_icon_url:
                    yuyuko_comments = [
                        "這就是群組的靈魂之影～很美吧？",
                        f"嘻嘻，我抓到了「{guild_name}」的圖像啦！",
                        "這片土地的標誌，生與死的交界處真是迷人呢～"
                    ]
                    await button_interaction.response.send_message(
                        f"{guild_icon_url}\n\n{random.choice(yuyuko_comments)}",
                        ephemeral=True
                    )
                else:
                    await button_interaction.response.send_message(
                        "哎呀～這個群組沒有靈魂之影可看哦。",
                        ephemeral=True
                    )
            except Exception as e:
                logging.error(f"按鈕互動錯誤: {e}", exc_info=True)  # ✅ 替換 print
                await button_interaction.response.send_message(
                    "哎呀，發生了一點小意外…稍後再試試吧～",
                    ephemeral=True
                )

        button = Button(
            label="點擊獲取群組圖貼",
            style=discord.ButtonStyle.primary,
            emoji="🖼️"
        )
        button.callback = button_callback
        view.add_item(button)

        await interaction.response.send_message(embed=embed, view=view)

def setup(bot):
    bot.add_cog(ServerInfo(bot))
