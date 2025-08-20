import discord
from discord.ext import commands
from discord.ui import View, Button
import random
import logging

class ServerInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(
        name="server_info",
        description="幽幽子為你窺探群組的靈魂資訊～"
    )
    async def server_info(self, ctx: discord.ApplicationContext):
        try:
            guild = ctx.guild
            if guild is None:
                await ctx.respond(
                    "哎呀～這個地方沒有靈魂聚集，無法窺探哦。請在群組中使用此指令～",
                    ephemeral=True
                )
                logging.info(f"Server info command failed: Not in a guild, executed by {ctx.author}")
                return

            guild_name = guild.name
            guild_id = guild.id
            member_count = guild.member_count
            owner = guild.owner
            owner_display = f"{owner.mention} ({owner})" if owner else "未知"
            if hasattr(guild, "members") and guild.members is not None:
                bot_count = sum(1 for member in guild.members if member.bot)
            else:
                bot_count = "未知"
            role_count = len(guild.roles)
            emoji_count = len(guild.emojis)
            boost_level = guild.premium_tier
            boost_count = guild.premium_subscription_count
            boost_status = f"LV.{boost_level}（{boost_count} 次加成）" if boost_level > 0 else "無加成"
            created_at = f"<t:{int(guild.created_at.timestamp())}:F>"
            guild_icon_url = guild.icon.url if guild.icon else None

            embed = discord.Embed(
                title="🌸 幽幽子窺探的群組靈魂 🌸",
                description=(
                    f"我是西行寺幽幽子，亡魂之主，現在為你揭示群組「{guild_name}」的靈魂～\n"
                    "讓我們來看看這片土地的命運吧…"
                ),
                color=discord.Color.from_rgb(255, 182, 193)
            )

            embed.add_field(name="群組之名", value=guild_name, inline=False)
            embed.add_field(name="群主", value=owner_display, inline=True)
            embed.add_field(name="群組ID", value=guild_id, inline=True)
            embed.add_field(name="靈魂數量", value=f"{member_count} (機械之魂: {bot_count})", inline=True)
            embed.add_field(name="身份之數", value=role_count, inline=True)
            embed.add_field(name="群組加成狀態", value=boost_status, inline=True)
            embed.add_field(name="表情數量", value=str(emoji_count), inline=True)
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

            async def button_callback(interaction: discord.Interaction):
                try:
                    guild = interaction.guild
                    guild_icon_url = guild.icon.url if guild and guild.icon else None
                    guild_name = guild.name if guild else "未知群組"

                    if guild_icon_url:
                        yuyuko_comments = [
                            "這就是群組的靈魂之影～很美吧？",
                            f"嘻嘻，我抓到了「{guild_name}」的圖像啦！",
                            "這片土地的標誌，生與死的交界處真是迷人呢～"
                        ]
                        await interaction.response.send_message(
                            f"{guild_icon_url}\n\n{random.choice(yuyuko_comments)}",
                            ephemeral=True
                        )
                        logging.info(f"Server icon requested by {interaction.user} in {guild_name}")
                    else:
                        await interaction.response.send_message(
                            "哎呀～這個群組沒有靈魂之影可看哦。",
                            ephemeral=True
                        )
                        logging.info(f"Server icon request failed (no icon) by {interaction.user} in {guild_name}")
                except Exception as e:
                    logging.error(f"Button interaction error in server_info: {e}")
                    await interaction.response.send_message(
                        "哎呀，發生了一點小意外…幽幽子迷路了，請稍後再試吧～",
                        ephemeral=True
                    )

            button = Button(
                label="點擊獲取群組圖貼",
                style=discord.ButtonStyle.primary,
                emoji="🖼️"
            )
            button.callback = button_callback
            view.add_item(button)

            await ctx.respond(embed=embed, view=view, ephemeral=False)
            logging.info(f"Server info command executed by {ctx.author} in {guild_name}")

        except Exception as e:
            logging.error(f"Error in server_info command: {e}")
            await ctx.respond(
                "哎呀，幽幽子好像迷路了…請稍後再試！",
                ephemeral=True
            )

def setup(bot):
    bot.add_cog(ServerInfo(bot))
