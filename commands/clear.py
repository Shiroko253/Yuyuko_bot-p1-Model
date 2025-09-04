import discord
from discord.ext import commands
from discord import ApplicationContext, Interaction
from datetime import datetime, timedelta, timezone

class Clear(commands.Cog):
    """
    ✿ 冥界清掃隊 ✿
    幽幽子命令妖夢化身為清掃小隊，把靈魂們的雜訊優雅地清理掉～
    """
    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(name="clear", description="讓妖夢清掃冥界的雜訊～")
    @commands.has_permissions(administrator=True)
    async def clear(self, ctx: ApplicationContext, amount: int):
        await ctx.defer(ephemeral=True)

        # 櫻花語氣檢查
        if amount <= 0:
            embed = discord.Embed(
                title="🌸 幽幽子的提醒",
                description="請輸入一個大於 0 的數字哦～妖夢才能清掃靈魂的雜訊！",
                color=0xFFA500
            ).set_footer(text="櫻花飄落也有數量，清掃要有度")
            await ctx.followup.send(embed=embed)
            return

        if amount > 100:
            embed = discord.Embed(
                title="🌸 妖夢快要累壞啦！",
                description="幽幽子禁止一次清掃超過 100 條消息～請分批進行，讓妖夢慢慢來！",
                color=0xFFA500
            ).set_footer(text="冥界的清掃也要溫柔進行")
            await ctx.followup.send(embed=embed)
            return

        cutoff_date = datetime.now(tz=timezone.utc) - timedelta(days=14)

        try:
            deleted = await ctx.channel.purge(limit=amount, after=cutoff_date)
            if deleted:
                embed = discord.Embed(
                    title="🌸 妖夢已完成清掃～",
                    description=f"已優雅地清除 {len(deleted)} 條靈魂雜訊。\n幽幽子在櫻花下微笑讚賞妖夢～",
                    color=0x00FFCC
                ).set_footer(text="冥界清掃完畢，櫻花更美了～")
            else:
                embed = discord.Embed(
                    title="🌸 沒有靈魂可清掃～",
                    description="所有消息都超過了 14 天限制，櫻花已將舊靈魂帶走～",
                    color=0xFFFF99
                ).set_footer(text="冥界清掃受限，請重新嘗試")
            await ctx.followup.send(embed=embed)

        except discord.Forbidden:
            embed = discord.Embed(
                title="⛔ 妖夢被困住了！",
                description="幽幽子發現權限不足，妖夢無法清掃消息。\n請聯繫管理員幫幽幽子和妖夢加點力量吧～",
                color=0xFF6699
            ).set_footer(text="請給機器人『刪除消息』權限")
            await ctx.followup.send(embed=embed)

        except discord.HTTPException as e:
            embed = discord.Embed(
                title="❌ 櫻花舞亂了！",
                description=f"API 發生錯誤：{getattr(e, 'text', str(e))}\n幽幽子輕輕地安慰妖夢，下次再試～",
                color=0xFF3366
            ).set_footer(text="櫻花飄落有時，請稍後再試")
            await ctx.followup.send(embed=embed)

        except Exception as e:
            embed = discord.Embed(
                title="❌ 冥界迷霧！",
                description=f"發生未知錯誤：{str(e)}\n幽幽子正揮舞櫻花幫你驅散迷霧～",
                color=0x990033
            ).set_footer(text="如有問題請聯絡幽幽子或管理員")
            await ctx.followup.send(embed=embed)

    @clear.error
    async def clear_error(self, ctx: ApplicationContext, error):
        if isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(
                title="⛔ 妖夢不聽你的話！",
                description="你沒有管理員權限，妖夢只聽幽幽子的指令哦～",
                color=0xFF3366
            ).set_footer(text="冥界清掃需要主人的授權")
            await ctx.respond(embed=embed, ephemeral=True)
        else:
            embed = discord.Embed(
                title="❌ 冥界櫻花迷路了！",
                description=f"發生未知錯誤：{str(error)}\n幽幽子和妖夢一起努力排查～",
                color=0x990033
            ).set_footer(text="如有問題請回報給幽幽子")
            await ctx.respond(embed=embed, ephemeral=True)

def setup(bot):
    """
    ✿ 幽幽子優雅地將清掃指令裝進 bot ✿
    """
    bot.add_cog(Clear(bot))