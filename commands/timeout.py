import discord
from discord.ext import commands
from datetime import datetime, timedelta

class Timeout(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @discord.slash_command(
        name="timeout",
        description="禁言指定的使用者（以分鐘為單位）"
    )
    async def timeout(
        self,
        ctx: discord.ApplicationContext,
        member: discord.Member,
        duration: int
    ):
        if not ctx.author.guild_permissions.moderate_members:
            embed = discord.Embed(
                title="⚠️ 權限不足",
                description="你沒有權限使用這個指令。",
                color=discord.Color.orange()
            )
            await ctx.respond(embed=embed, ephemeral=True)
            return

        await ctx.defer(ephemeral=True)
        
        # 先檢查 guild 和 bot_member 是否存在
        if not ctx.guild or not ctx.guild.me:
            embed = discord.Embed(
                title="❌ 操作失敗",
                description="此指令只能在伺服器中使用，或機器人資訊加載失敗。",
                color=discord.Color.red()
            )
            await ctx.respond(embed=embed, ephemeral=True)
            return

        bot_member = ctx.guild.me

        # 機器人權限檢查
        if not bot_member.guild_permissions.moderate_members:
            embed = discord.Embed(
                title="❌ 操作失敗",
                description="機器人缺少禁言權限，請確認角色權限設置。",
                color=discord.Color.red()
            )
            await ctx.respond(embed=embed, ephemeral=True)
            return

        # 角色層級檢查
        if member.top_role >= bot_member.top_role:
            embed = discord.Embed(
                title="❌ 操作失敗",
                description=f"無法禁言 {member.mention}，因為他們的角色高於或等於機器人。",
                color=discord.Color.red()
            )
            await ctx.respond(embed=embed, ephemeral=True)
            return

        # 禁言操作
        try:
            mute_time = datetime.utcnow() + timedelta(minutes=duration)
            await member.timeout(mute_time, reason=f"Timeout by {ctx.author} for {duration} minutes")
            embed = discord.Embed(
                title="⛔ 成員禁言",
                description=f"{member.mention} 已被禁言 **{duration} 分鐘**。",
                color=discord.Color.dark_red()
            )
            embed.set_footer(text="請遵守伺服器規則")
            await ctx.respond(embed=embed, ephemeral=False)
        except discord.Forbidden:
            embed = discord.Embed(
                title="❌ 無法禁言",
                description=f"權限不足，無法禁言 {member.mention} 或回應訊息。",
                color=discord.Color.red()
            )
            try:
                await ctx.respond(embed=embed, ephemeral=False)
            except discord.Forbidden:
                print("無法回應權限不足的錯誤訊息，請檢查機器人權限。")
        except discord.HTTPException as e:
            embed = discord.Embed(
                title="❌ 禁言失敗",
                description=f"操作失敗：{e}",
                color=discord.Color.red()
            )
            await ctx.respond(embed=embed, ephemeral=True)

def setup(bot: commands.Bot):
    bot.add_cog(Timeout(bot))
