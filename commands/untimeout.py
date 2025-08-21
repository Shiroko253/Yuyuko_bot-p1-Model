import discord
from discord.ext import commands

class Untimeout(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(
        name="untimeout",
        description="解除禁言狀態"
    )
    async def untimeout(self, ctx, member: discord.Member):
        # 權限檢查
        if not ctx.author.guild_permissions.moderate_members:
            embed = discord.Embed(
                title="⚠️ 權限不足",
                description="你沒有權限使用這個指令。",
                color=discord.Color.orange()
            )
            await ctx.respond(embed=embed, ephemeral=True)
            return

        # 檢查目標成員是否被禁言
        if not member.timed_out_until or member.timed_out_until < discord.utils.utcnow():
            embed = discord.Embed(
                title="ℹ️ 成員未被禁言",
                description=f"{member.mention} 目前沒有被禁言。",
                color=discord.Color.blue()
            )
            await ctx.respond(embed=embed, ephemeral=True)
            return

        try:
            await member.edit(timed_out_until=None, reason=f"UnTimeout by {ctx.author} ({ctx.author.id})")
            embed = discord.Embed(
                title="🔓 成員解除禁言",
                description=f"{member.mention} 的禁言狀態已被解除。",
                color=discord.Color.green()
            )
            embed.set_footer(text="希望成員能遵守規則")
            await ctx.respond(embed=embed)
        except discord.Forbidden:
            embed = discord.Embed(
                title="❌ 無法解除禁言",
                description=f"權限不足，無法解除 {member.mention} 的禁言。",
                color=discord.Color.red()
            )
            await ctx.respond(embed=embed, ephemeral=True)
        except discord.HTTPException as e:
            embed = discord.Embed(
                title="❌ 解除禁言失敗",
                description=f"操作失敗：{e}",
                color=discord.Color.red()
            )
            await ctx.respond(embed=embed, ephemeral=True)
        except Exception as e:
            embed = discord.Embed(
                title="❌ 不明錯誤",
                description=f"發生未知錯誤：{e}",
                color=discord.Color.red()
            )
            await ctx.respond(embed=embed, ephemeral=True)

def setup(bot):
    bot.add_cog(Untimeout(bot))
