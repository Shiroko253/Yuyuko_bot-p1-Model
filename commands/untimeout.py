import discord
from discord.ext import commands

class Untimeout(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(
        name="untimeout",
        description="幽幽子法令：解除亡魂的禁言狀態"
    )
    async def untimeout(self, ctx: discord.ApplicationContext, member: discord.Member):
        # 權限檢查
        if not ctx.author.guild_permissions.moderate_members:
            embed = discord.Embed(
                title="🌸 權限不足！",
                description="只有冥界主人才有權放出亡魂的聲音哦～",
                color=discord.Color.from_rgb(205, 133, 232)
            )
            embed.set_footer(text="幽幽子：賞花時要安靜，解除禁言也要有規則～")
            await ctx.respond(embed=embed, ephemeral=True)
            return

        # 檢查目標成員是否被禁言
        if not member.timed_out_until or member.timed_out_until < discord.utils.utcnow():
            embed = discord.Embed(
                title="ℹ️ 亡魂自由！",
                description=f"{member.mention} 現在已是自由的亡魂，無需解除禁言。",
                color=discord.Color.blue()
            )
            embed.set_footer(text="幽幽子：自由靈魂才能賞花、吃點心～")
            await ctx.respond(embed=embed, ephemeral=True)
            return

        try:
            await member.edit(timed_out_until=None, reason=f"UnTimeout by {ctx.author} ({ctx.author.id})")
            embed = discord.Embed(
                title="🔓 幽幽子解除冥界禁言令！",
                description=f"{member.mention} 的禁言狀態已被幽幽子解除，亡魂可以再次發聲啦～",
                color=discord.Color.from_rgb(205, 133, 232)
            )
            embed.set_footer(text="幽幽子：賞花、吃點心、暢所欲言！")
            await ctx.respond(embed=embed)
        except discord.Forbidden:
            embed = discord.Embed(
                title="❌ 無法解除禁言",
                description=f"幽幽子的法力被限制，無法解除 {member.mention} 的禁言。",
                color=discord.Color.red()
            )
            embed.set_footer(text="幽幽子：有時候亡魂太強也沒辦法呢…")
            await ctx.respond(embed=embed, ephemeral=True)
        except discord.HTTPException as e:
            embed = discord.Embed(
                title="❌ 解除禁言失敗",
                description=f"操作失敗：{e}",
                color=discord.Color.red()
            )
            embed.set_footer(text="幽幽子：冥界的網路好像不太穩…")
            await ctx.respond(embed=embed, ephemeral=True)
        except Exception as e:
            embed = discord.Embed(
                title="❌ 不明錯誤",
                description=f"發生未知錯誤：{e}",
                color=discord.Color.red()
            )
            embed.set_footer(text="幽幽子：亡魂的聲音太神秘了…")
            await ctx.respond(embed=embed, ephemeral=True)

def setup(bot):
    bot.add_cog(Untimeout(bot))