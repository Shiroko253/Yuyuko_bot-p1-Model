import discord
from discord.ext import commands
import random
import logging
from typing import Any, Dict, Union
import asyncio

class Balance(commands.Cog):
    """
    ✿ 幽幽子的幽靈幣餘額窺探 ✿
    讓幽幽子幫你優雅地查查錢包吧～
    """

    def __init__(self, bot: discord.Bot):
        self.bot = bot
        self.logger = logging.getLogger("SakuraBot.commands.balance")
        # 添加查詢鎖機制
        self.query_locks = {}

    def _get_query_lock(self, user_id: str) -> asyncio.Lock:
        """獲取用戶查詢鎖"""
        if user_id not in self.query_locks:
            self.query_locks[user_id] = asyncio.Lock()
        return self.query_locks[user_id]

    def format_number(self, num: Union[float, int]) -> str:
        """
        幽幽子溫柔地把大數字變成美麗的單位～
        """
        try:
            num = float(num)
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
        except (ValueError, TypeError):
            self.logger.warning(f"無法格式化數字: {num}")
            return "0.00"

    @discord.slash_command(
        name="balance",
        description="幽幽子為你窺探幽靈幣的數量～"
    )
    async def balance(self, ctx: discord.ApplicationContext):
        try:
            # 獲取資料管理器
            data_manager = getattr(self.bot, "data_manager", None)
            if not data_manager:
                embed = discord.Embed(
                    title="🌸 系統錯誤 🌸",
                    description="幽幽子的資料管理員暫時不在，請稍後再來～",
                    color=discord.Color.red()
                )
                embed.set_footer(text="如有問題請找管理員")
                await ctx.respond(embed=embed, ephemeral=True)
                return

            # 獲取用戶鎖，防止並發查詢
            user_lock = self._get_query_lock(str(ctx.user.id))
            async with user_lock:
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

                # 安全地載入餘額資料
                try:
                    user_balance = data_manager._load_json("economy/balance.json", {})
                except Exception as e:
                    self.logger.error(f"載入餘額資料失敗: {e}")
                    embed = discord.Embed(
                        title="🌸 資料載入錯誤 🌸",
                        description="幽幽子的錢包資料暫時無法讀取，請稍後再試～",
                        color=discord.Color.red()
                    )
                    await ctx.respond(embed=embed, ephemeral=True)
                    return

                guild_id = str(ctx.guild.id)
                user_id = str(ctx.user.id)

                # 驗證資料結構
                if not isinstance(user_balance, dict):
                    user_balance = {}
                
                user_balance.setdefault(guild_id, {})
                if not isinstance(user_balance[guild_id], dict):
                    user_balance[guild_id] = {}
                
                user_balance[guild_id].setdefault(user_id, 0)
                
                # 確保餘額是數字
                balance = user_balance[guild_id][user_id]
                try:
                    balance = float(balance)
                except (ValueError, TypeError):
                    balance = 0.0
                    self.logger.warning(f"無效的餘額資料: {user_balance[guild_id][user_id]}")

                # 幽幽子的小語錄，讓查詢變得更溫柔可愛
                yuyuko_comments = [
                    "嘻嘻，你的幽靈幣數量真有趣呢～",
                    "這些幽靈幣，會帶來什麼樣的命運呢？",
                    "靈魂與幽靈幣的交響曲，幽幽子很喜歡哦～",
                    "你的幽靈幣閃閃發光，櫻花都忍不住飄落了～",
                    "這樣的數量，會讓幽靈們羨慕吧？"
                ]

                formatted_balance = self.format_number(balance)

                embed = discord.Embed(
                    title="🌸 幽幽子的幽靈幣窺探 🌸",
                    description=(
                        f"**{ctx.user.display_name}**，讓幽幽子為你揭示吧～\n\n"
                        f"在這片靈魂之地，你的幽靈幣餘額為：\n"
                        f"**{formatted_balance} 幽靈幣**"
                    ),
                    color=discord.Color.from_rgb(255, 182, 193)
                )
                embed.set_thumbnail(url=ctx.user.display_avatar.url)
                embed.set_footer(text=random.choice(yuyuko_comments))

                await ctx.respond(embed=embed, ephemeral=False)

        except discord.errors.NotFound:
            self.logger.warning("Failed to respond due to expired interaction.")
        except Exception as e:
            self.logger.error(f"Unexpected error in balance command: {e}")
            yuyuko_error_comments = [
                "下次再試試吧～靈魂的波動有時會捉弄我們哦～",
                "幽幽子也會偶爾迷路呢…下次會順利的！",
                "哎呀～幽幽子的小手突然滑了一下，下次一定查到！"
            ]
            try:
                error_embed = discord.Embed(
                    title="🌸 哎呀，靈魂出錯了！🌸",
                    description=f"幽幽子試圖窺探你的幽靈幣時，發生了一點小意外…",
                    color=discord.Color.red()
                )
                error_embed.set_footer(text=random.choice(yuyuko_error_comments))
                await ctx.respond(embed=error_embed, ephemeral=True)
            except discord.errors.NotFound:
                self.logger.warning("Failed to send error response due to expired interaction.")

def setup(bot: discord.Bot):
    """
    ✿ 幽幽子優雅地將餘額查詢功能裝進 bot 裡 ✿
    """
    bot.add_cog(Balance(bot))
    logging.getLogger("SakuraBot.commands.balance").info("Balance Cog loaded successfully")
