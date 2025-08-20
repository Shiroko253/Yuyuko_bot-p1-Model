import discord
from discord.ext import commands

class Ban(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(name="ban", description="封禁用户")
    async def ban(
        self,
        ctx: discord.ApplicationContext,
        member: discord.Member,
        reason: str = None
    ):
        await ctx.defer(ephemeral=False)  # 先延遲回覆，避免 interaction timeout

        # 嘗試獲取guild member對象
        target = None
        if isinstance(member, discord.Member):
            target = member
        elif ctx.guild:
            # 嘗試從guild取
            target = ctx.guild.get_member(member.id)
        
        if target is None:
            embed = discord.Embed(
                title="無法封禁",
                description="❌ 指定的對象不是本伺服器成員或已離開伺服器。",
                color=discord.Color.red()
            )
            await ctx.followup.send(embed=embed, ephemeral=True)
            return

        # 防止自我封禁和封禁機器人
        if target.id == ctx.user.id:
            embed = discord.Embed(
                title="無法封禁自己",
                description="⚠️ 你不能封禁你自己！",
                color=discord.Color.orange()
            )
            await ctx.followup.send(embed=embed, ephemeral=True)
            return
        if target.id == ctx.guild.me.id:
            embed = discord.Embed(
                title="無法封禁機器人",
                description="⚠️ 你不能封禁我。",
                color=discord.Color.orange()
            )
            await ctx.followup.send(embed=embed, ephemeral=True)
            return

        # 檢查權限
        if not ctx.user.guild_permissions.ban_members:
            embed = discord.Embed(
                title="權限不足",
                description="⚠️ 您沒有封禁成員的權限。",
                color=discord.Color.yellow()
            )
            await ctx.followup.send(embed=embed, ephemeral=True)
            return
        if not ctx.guild.me.guild_permissions.ban_members:
            embed = discord.Embed(
                title="權限不足",
                description="⚠️ 我沒有封禁成員的權限，請檢查我的身分組是否擁有「封禁成員」權限。",
                color=discord.Color.yellow()
            )
            await ctx.followup.send(embed=embed, ephemeral=True)
            return
        if ctx.guild.me.top_role <= target.top_role:
            embed = discord.Embed(
                title="無法封禁",
                description=(
                    "⚠️ 我的身分組層級低於此用戶，無法封禁。\n"
                    "請將我的身分組移至更高層級，並確保我有「封禁成員」權限。"
                ),
                color=discord.Color.yellow()
            )
            await ctx.followup.send(embed=embed, ephemeral=True)
            return

        # 嘗試私訊通知被ban對象
        dm_sent = True
        try:
            dm_embed = discord.Embed(
                title="您已被封禁",
                description=f"您已被伺服器 {ctx.guild.name} 封禁。\n原因：{reason or '未提供原因'}",
                color=discord.Color.red()
            )
            await target.send(embed=dm_embed)
        except Exception:
            dm_sent = False

        # 嘗試封禁
        try:
            await target.ban(reason=reason or f"由 {ctx.user} 封禁")
            embed = discord.Embed(
                title="封禁成功",
                description=(
                    f"✅ 用戶 **{target}** 已被封禁。\n"
                    f"原因：{reason or '未提供原因'}\n"
                    f"{'（未能成功私訊通知該用戶）' if not dm_sent else ''}"
                ),
                color=discord.Color.red()
            )
            await ctx.followup.send(embed=embed, ephemeral=False)
        except Exception as e:
            embed = discord.Embed(
                title="封禁失敗",
                description=f"❌ 嘗試封禁用戶時發生錯誤：{e}",
                color=discord.Color.red()
            )
            await ctx.followup.send(embed=embed, ephemeral=True)

def setup(bot):
    bot.add_cog(Ban(bot))
