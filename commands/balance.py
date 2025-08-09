import discord
from discord.ext import commands
import random
import logging
import os
import json

def load_json(file, default={}):
    """載入 JSON 檔案"""
    try:
        with open(file, "r", encoding="utf-8") as f:
            return json.load(f) or default
    except FileNotFoundError:
        logging.info(f"Creating empty JSON file: {file}")
        os.makedirs(os.path.dirname(file), exist_ok=True)
        with open(file, "w", encoding="utf-8") as f:
            json.dump(default, f, indent=4, ensure_ascii=False)
        return default
    except Exception as e:
        logging.error(f"Failed to load JSON file {file}: {e}")
        return default

class Balance(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(name="balance", description="幽幽子為你窺探幽靈幣的數量～")
    async def balance(self, ctx: discord.ApplicationContext):
        def format_number(num):
            if num >= 1e20:
                return f"{num / 1e20:.2f} 兆京"
            elif num >= 1e16:
                return f"{num / 1e16:.2f} 京"
            elif num >= 1e12:
                return f"{num / 1e12:.2f} 兆"
            elif num >= 1e8:
                return f"{num / 1e8:.2f} 億"
            else:
                return f"{num:.2f}"

        try:
            await ctx.defer(ephemeral=False)

            # 修正：如果在DM就直接回覆錯誤訊息
            if ctx.guild is None:
                await ctx.respond(
                    embed=discord.Embed(
                        title="🌸 無法查詢幽靈幣 🌸",
                        description="幽幽子只能在伺服器裡窺探幽靈幣哦～請到伺服器頻道使用指令！",
                        color=discord.Color.red()
                    ),
                    ephemeral=True
                )
                return

            user_balance = load_json("economy/balance.json")
            guild_id = str(ctx.guild.id)
            user_id = str(ctx.user.id)

            if guild_id not in user_balance:
                user_balance[guild_id] = {}

            balance = user_balance[guild_id].get(user_id, 0)

            yuyuko_comments = [
                "嘻嘻，你的幽靈幣數量真有趣呢～",
                "這些幽靈幣，會帶來什麼樣的命運呢？",
                "靈魂與幽靈幣的交響曲，幽幽子很喜歡哦～",
                "你的幽靈幣閃閃發光，櫻花都忍不住飄落了～",
                "這樣的數量，會讓幽靈們羨慕吧？"
            ]

            formatted_balance = format_number(balance)

            embed = discord.Embed(
                title="🌸 幽幽子的幽靈幣窺探 🌸",
                description=(
                    f"**{ctx.user.display_name}**，讓幽幽子為你揭示吧～\n\n"
                    f"在這片靈魂之地，你的幽靈幣餘額為：\n"
                    f"**{formatted_balance} 幽靈幣**"
                ),
                color=discord.Color.from_rgb(255, 182, 193)
            )
            embed.set_footer(text=random.choice(yuyuko_comments))

            await ctx.respond(embed=embed, ephemeral=False)

        except Exception as e:
            logging.error(f"Unexpected error in balance command: {e}")
            if isinstance(e, discord.errors.NotFound) and getattr(e, "code", None) == 10062:
                logging.warning("Interaction expired in balance command, cannot respond.")
            else:
                try:
                    yuyuko_error_comments = [
                        "下次再試試吧～靈魂的波動有時會捉弄我們哦～"
                    ]
                    await ctx.respond(
                        embed=discord.Embed(
                            title="🌸 哎呀，靈魂出錯了！🌸",
                            description=f"幽幽子試圖窺探你的幽靈幣時，發生了一點小意外…\n錯誤：{e}",
                            color=discord.Color.red()
                        ).set_footer(text=random.choice(yuyuko_error_comments)),
                        ephemeral=True
                    )
                except discord.errors.NotFound:
                    logging.warning("Failed to respond due to expired interaction.")

def setup(bot):
    bot.add_cog(Balance(bot))
