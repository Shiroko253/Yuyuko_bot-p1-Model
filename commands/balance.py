import discord
from discord.ext import commands
import random
import logging
from typing import Any, Dict

class Balance(commands.Cog):
    """
    ✿ 幽幽子的幽靈幣餘額窺探 ✿
    讓幽幽子幫你優雅地查查錢包吧～
    """

    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @discord.slash_command(
        name="balance",
        description="幽幽子為你窺探幽靈幣的數量～"
    )
    async def balance(self, ctx: discord.ApplicationContext):
        def format_number(num: float) -> str:
            """
            幽幽子溫柔地把大數字變成美麗的單位～
            """
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

            # 幽幽子只在伺服器裡窺探錢包喔～
            if ctx.guild is None:
                embed = discord.Embed(
                    title="🌸 無法查詢幽靈幣 🌸",
                    description="幽幽子只能在伺服器裡窺探幽靈幣哦～請到伺服器頻道使用指令！",
                    color=discord.Color.red()
                )
                embed.set_footer(text="僅限伺服器查詢")
                await ctx.respond(embed=embed, ephemeral=True)
                return

            # 溫柔地從資料管理員那裡要來你的錢包
            user_balance: Dict[str, Any] = self.bot.data_manager.load_json("economy/balance.json", {})
            guild_id = str(ctx.guild.id)
            user_id = str(ctx.user.id)

            # 防止錢包消失（幽幽子會幫你補上0元）
            user_balance.setdefault(guild_id, {})
            user_balance[guild_id].setdefault(user_id, 0)

            balance = user_balance[guild_id][user_id]

            # 幽幽子的小語錄，讓查詢變得更溫柔可愛
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
            logging.exception(f"Unexpected error in balance command: {e}")
            yuyuko_error_comments = [
                "下次再試試吧～靈魂的波動有時會捉弄我們哦～",
                "幽幽子也會偶爾迷路呢…下次會順利的！",
                "哎呀～幽幽子的小手突然滑了一下，下次一定查到！"
            ]
            try:
                error_embed = discord.Embed(
                    title="🌸 哎呀，靈魂出錯了！🌸",
                    description=f"幽幽子試圖窺探你的幽靈幣時，發生了一點小意外…\n錯誤：{e}",
                    color=discord.Color.red()
                )
                error_embed.set_footer(text=random.choice(yuyuko_error_comments))
                await ctx.respond(embed=error_embed, ephemeral=True)
            except discord.errors.NotFound:
                logging.warning("Failed to respond due to expired interaction.")

def setup(bot: discord.Bot):
    """
    ✿ 幽幽子優雅地將餘額查詢功能裝進 bot 裡 ✿
    """
    bot.add_cog(Balance(bot))
    logging.info("Balance Cog loaded successfully")