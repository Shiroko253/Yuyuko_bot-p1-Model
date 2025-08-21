import discord
from discord.ext import commands
from discord import ApplicationContext, Interaction
from datetime import datetime, timedelta, timezone

class Clear(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(name="clear", description="清除指定数量的消息")
    @commands.has_permissions(administrator=True)
    async def clear(self, ctx: ApplicationContext, amount: int):
        await ctx.defer(ephemeral=True)

        if amount <= 0:
            embed = discord.Embed(
                title="⚠️ 無效數字",
                description="請輸入一個大於 0 的數字。",
                color=0xFFA500
            )
            await ctx.followup.send(embed=embed)
            return

        if amount > 100:
            embed = discord.Embed(
                title="⚠️ 超出限制",
                description="無法一次性刪除超過 100 條消息。",
                color=0xFFA500
            )
            await ctx.followup.send(embed=embed)
            return

        cutoff_date = datetime.now(tz=timezone.utc) - timedelta(days=14)

        try:
            deleted = await ctx.channel.purge(limit=amount, after=cutoff_date)
            if deleted:
                embed = discord.Embed(
                    title="✅ 清理成功",
                    description=f"已刪除 {len(deleted)} 條消息。",
                    color=0x00FF00
                )
            else:
                embed = discord.Embed(
                    title="⚠️ 無消息刪除",
                    description="沒有消息被刪除，可能所有消息都超過了 14 天限制。",
                    color=0xFFFF00
                )
            await ctx.followup.send(embed=embed)

        except discord.Forbidden:
            embed = discord.Embed(
                title="⛔ 權限錯誤",
                description="機器人缺少刪除消息的權限，請聯繫管理員進行配置。",
                color=0xFF0000
            )
            await ctx.followup.send(embed=embed)

        except discord.HTTPException as e:
            embed = discord.Embed(
                title="❌ 清理失敗",
                description=f"發生 API 錯誤：{getattr(e, 'text', str(e))}",
                color=0xFF0000
            )
            await ctx.followup.send(embed=embed)

        except Exception as e:
            embed = discord.Embed(
                title="❌ 清理失敗",
                description=f"發生未知錯誤：{str(e)}",
                color=0xFF0000
            )
            await ctx.followup.send(embed=embed)

    @clear.error
    async def clear_error(self, ctx: ApplicationContext, error):
        if isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(
                title="⛔ 無權限操作",
                description="你沒有管理員權限，無法執行此操作。",
                color=0xFF0000
            )
            await ctx.respond(embed=embed, ephemeral=True)
        else:
            embed = discord.Embed(
                title="❌ 指令錯誤",
                description=f"發生未知錯誤：{str(error)}",
                color=0xFF0000
            )
            await ctx.respond(embed=embed, ephemeral=True)

def setup(bot):
    bot.add_cog(Clear(bot))
