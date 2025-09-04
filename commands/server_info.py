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
                    "哎呀～這個地方沒有靈魂聚集，幽幽子什麼都看不到呢！請到群組中使用這個指令吧～",
                    ephemeral=True
                )
                logging.info(f"Server info command failed: Not in a guild, executed by {ctx.author}")
                return

            guild_name = guild.name
            guild_id = guild.id
            member_count = guild.member_count
            owner = guild.owner
            owner_display = f"{owner.mention} ({owner})" if owner else "未知"
            bot_count = sum(1 for member in guild.members if member.bot) if hasattr(guild, "members") else "未知"
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
                    f"─── 西行寺 幽幽子の冥界情報 ───\n"
                    f"櫻花飄落的季節，幽幽子窺探著群組「{guild_name}」的靈魂流動…\n"
                    "亡魂們的聚會會有什麼美味佳餚嗎？\n"
                    "請感受冥界主人的溫柔注視吧～"
                ),
                color=discord.Color.from_rgb(205, 133, 232)  # 紫櫻色
            )

            embed.add_field(name="群組之名", value=f"🌸 {guild_name}", inline=False)
            embed.add_field(name="群主", value=f"👑 {owner_display}", inline=True)
            embed.add_field(name="群組ID", value=f"`{guild_id}`", inline=True)
            embed.add_field(name="靈魂數量", value=f"👻 {member_count}（機械之魂: {bot_count}）", inline=True)
            embed.add_field(name="身份之數", value=f"🎭 {role_count}", inline=True)
            embed.add_field(name="群組加成狀態", value=f"✨ {boost_status}", inline=True)
            embed.add_field(name="表情數量", value=f"😆 {emoji_count}", inline=True)
            embed.add_field(name="此地誕生之日", value=f"⏳ {created_at}", inline=False)

            if guild_icon_url:
                embed.set_thumbnail(url=guild_icon_url)

            yuyuko_quotes = [
                "這片土地的靈魂真熱鬧…有沒有好吃的供品呀？",
                "冥界的櫻花最美，群組的靈魂也很閃耀呢～",
                "生與死的交界處，聚會最適合吃點甜點！",
                "亡魂的聚集地…要不要一起賞花、吃點心？",
                "命運的流轉，就像櫻花隨風飄落般美麗…"
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
                            "這就是群組靈魂的外貌～有點可愛吧？",
                            f"嘻嘻，我偷窺到了「{guild_name}」的冥界圖像！",
                            "生死交界的標誌，幽幽子覺得很美味…咦？好像說錯了！"
                        ]
                        await interaction.response.send_message(
                            f"{guild_icon_url}\n\n{random.choice(yuyuko_comments)}",
                            ephemeral=True
                        )
                        logging.info(f"Server icon requested by {interaction.user} in {guild_name}")
                    else:
                        await interaction.response.send_message(
                            "哎呀～這個群組沒有靈魂之影呢，下次再偷窺吧！",
                            ephemeral=True
                        )
                        logging.info(f"Server icon request failed (no icon) by {interaction.user} in {guild_name}")
                except Exception as e:
                    logging.error(f"Button interaction error in server_info: {e}")
                    await interaction.response.send_message(
                        "幽幽子迷路了…冥界的路太複雜，下次再來吧！",
                        ephemeral=True
                    )

            button = Button(
                label="偷窺群組靈魂之影",
                style=discord.ButtonStyle.primary,
                emoji="👻"
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
    logging.info("ServerInfo setup called!")
    bot.add_cog(ServerInfo(bot))