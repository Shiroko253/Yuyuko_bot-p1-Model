import discord
from discord.ext import commands

class Kick(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(name="kick", description="踢出用户")
    async def kick(
        self,
        ctx: discord.ApplicationContext,
        member: discord.Member,
        reason: str = None
    ):
        # 不能踢自己或機器人
        if member.id == ctx.user.id:
            embed = discord.Embed(
                title="无法踢出自己",
                description="⚠️ 你不能踢出你自己！",
                color=discord.Color.orange()
            )
            await ctx.respond(embed=embed, ephemeral=True)
            return

        if member.id == ctx.guild.me.id:
            embed = discord.Embed(
                title="无法踢出机器人",
                description="⚠️ 你不能踢出我。",
                color=discord.Color.orange()
            )
            await ctx.respond(embed=embed, ephemeral=True)
            return

        # 權限檢查
        if not ctx.user.guild_permissions.kick_members:
            embed = discord.Embed(
                title="权限不足",
                description="⚠️ 您没有踢出成员的权限。",
                color=discord.Color.yellow()
            )
            await ctx.respond(embed=embed, ephemeral=True)
            return

        if not ctx.guild.me.guild_permissions.kick_members:
            embed = discord.Embed(
                title="权限不足",
                description="⚠️ 我没有踢出成员的权限，请检查我的角色是否拥有 **踢出成员** 的权限。",
                color=discord.Color.yellow()
            )
            await ctx.respond(embed=embed, ephemeral=True)
            return

        if ctx.guild.me.top_role <= member.top_role:
            embed = discord.Embed(
                title="无法踢出",
                description=(
                    "⚠️ 我的角色权限不足，无法踢出此用户。\n"
                    "请将我的角色移动到服务器的 **最高层级**，"
                    "并确保我的角色拥有 **踢出成员** 的权限。"
                ),
                color=discord.Color.yellow()
            )
            await ctx.respond(embed=embed, ephemeral=True)
            return

        # 嘗試私訊通知被踢對象
        dm_sent = True
        try:
            dm_embed = discord.Embed(
                title="您已被踢出服务器",
                description=f"您已被伺服器 **{ctx.guild.name}** 踢出。\n原因：{reason or '未提供原因'}",
                color=discord.Color.red()
            )
            await member.send(embed=dm_embed)
        except Exception:
            dm_sent = False

        # 嘗試踢出
        try:
            await member.kick(reason=reason or f"由 {ctx.user} 踢出")
            embed = discord.Embed(
                title="踢出成功",
                description=(
                    f"✅ 用户 **{member}** 已被踢出。\n"
                    f"原因：{reason or '未提供原因'}\n"
                    f"{'（未能成功私讯通知该用户）' if not dm_sent else ''}"
                ),
                color=discord.Color.red()
            )
            # 公開
            await ctx.respond(embed=embed, ephemeral=False)
        except Exception as e:
            embed = discord.Embed(
                title="踢出失败",
                description=f"❌ 尝试踢出用户时发生错误：{e}",
                color=discord.Color.red()
            )
            await ctx.respond(embed=embed, ephemeral=True)

def setup(bot):
    bot.add_cog(Kick(bot))
