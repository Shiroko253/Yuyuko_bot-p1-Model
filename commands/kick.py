import discord
from discord.ext import commands
import logging

class Kick(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(name="kick", description="幽幽子的放逐靈魂指令～踢出用戶")
    async def kick(
        self,
        ctx: discord.ApplicationContext,
        member: discord.Member,
        reason: str = None
    ):
        if member.id == ctx.user.id:
            embed = discord.Embed(
                title="🌸 無法放逐自己～",
                description="幽幽子輕聲告訴你：你不能放逐自己的靈魂哦！",
                color=discord.Color.orange()
            ).set_footer(text="櫻花下，請善待自己的靈魂")
            await ctx.respond(embed=embed, ephemeral=True)
            return

        if member.id == ctx.guild.me.id:
            embed = discord.Embed(
                title="🌸 無法踢出幽幽子～",
                description="幽幽子在冥界飄蕩，你可踢不走我呢～",
                color=discord.Color.orange()
            ).set_footer(text="幽幽子會一直守護大家")
            await ctx.respond(embed=embed, ephemeral=True)
            return

        if not ctx.user.guild_permissions.kick_members:
            embed = discord.Embed(
                title="🌸 權限不足",
                description="靈魂之力不足，你沒有放逐其他人的權限哦～",
                color=discord.Color.yellow()
            ).set_footer(text="請找管理員或幽幽子幫忙")
            await ctx.respond(embed=embed, ephemeral=True)
            return

        if not ctx.guild.me.guild_permissions.kick_members:
            embed = discord.Embed(
                title="🌸 幽幽子權限不足",
                description="幽幽子的靈魂未被賦予放逐之力，請給我『踢出成員』權限～",
                color=discord.Color.yellow()
            ).set_footer(text="請提升我的角色權限")
            await ctx.respond(embed=embed, ephemeral=True)
            return

        if ctx.guild.me.top_role <= member.top_role:
            embed = discord.Embed(
                title="🌸 無法放逐高階靈魂",
                description=(
                    "幽幽子的角色層級不夠高，無法放逐此靈魂～\n"
                    "請將幽幽子的角色移至伺服器最高層級，並賦予『踢出成員』權限。"
                ),
                color=discord.Color.yellow()
            ).set_footer(text="冥界秩序由角色層級決定")
            await ctx.respond(embed=embed, ephemeral=True)
            return

        dm_sent = True
        try:
            dm_embed = discord.Embed(
                title="🌸 你被幽幽子放逐了～",
                description=f"你已被伺服器 **{ctx.guild.name}** 放逐。\n原因：{reason or '未提供原因'}",
                color=discord.Color.red()
            ).set_footer(text="櫻花飄落，請靜待靈魂安息")
            await member.send(embed=dm_embed)
        except Exception as e:
            logging.warning(f"無法私訊通知被踢用戶 {member}: {e}")
            dm_sent = False

        try:
            await member.kick(reason=reason or f"由 {ctx.user} 放逐")
            embed = discord.Embed(
                title="🌸 放逐成功～",
                description=(
                    f"幽幽子已將靈魂 **{member}** 放逐出伺服器。\n"
                    f"原因：{reason or '未提供原因'}\n"
                    f"{'（未能成功私訊通知該靈魂）' if not dm_sent else ''}"
                ),
                color=discord.Color.red()
            ).set_footer(text="櫻花飄落，新的秩序降臨")
            await ctx.respond(embed=embed, ephemeral=False)
        except Exception as e:
            logging.error(f"放逐失敗: {e}")
            embed = discord.Embed(
                title="🌸 放逐失敗～",
                description=f"幽幽子放逐時遇到阻礙：{e}",
                color=discord.Color.red()
            ).set_footer(text="如有疑問請聯絡管理員或幽幽子")
            await ctx.respond(embed=embed, ephemeral=True)

def setup(bot):
    bot.add_cog(Kick(bot))