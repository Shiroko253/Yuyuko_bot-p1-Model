import discord
from discord.ext import commands
from datetime import datetime, timedelta

class Timeout(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @discord.slash_command(
        name="timeout",
        description="幽幽子法令：禁言嘈雜的亡魂（以分鐘為單位）"
    )
    async def timeout(
        self,
        ctx: discord.ApplicationContext,
        member: discord.Member,
        duration: int
    ):
        if not ctx.author.guild_permissions.moderate_members:
            embed = discord.Embed(
                title="🌸 權限不足！",
                description="只有冥界主人才有權讓亡魂安靜哦～",
                color=discord.Color.from_rgb(205, 133, 232)
            )
            embed.set_footer(text="幽幽子：賞花時要保持安靜～")
            await ctx.respond(embed=embed, ephemeral=True)
            return

        await ctx.defer(ephemeral=True)
        
        if not ctx.guild or not ctx.guild.me:
            embed = discord.Embed(
                title="❌ 操作失敗",
                description="此指令只能在冥界（伺服器）內使用，幽幽子迷路了…",
                color=discord.Color.red()
            )
            embed.set_footer(text="幽幽子：冥界的路好複雜啊～")
            await ctx.respond(embed=embed, ephemeral=True)
            return

        bot_member = ctx.guild.me

        if not bot_member.guild_permissions.moderate_members:
            embed = discord.Embed(
                title="❌ 操作失敗",
                description="幽幽子沒有法力可以禁言亡魂，請賦予機器人適當權限。",
                color=discord.Color.red()
            )
            embed.set_footer(text="幽幽子：權限不足，賞花只能看不能說～")
            await ctx.respond(embed=embed, ephemeral=True)
            return

        if member.top_role >= bot_member.top_role:
            embed = discord.Embed(
                title="❌ 操作失敗",
                description=f"幽幽子無法禁言 {member.mention}，他的靈魂太強大啦！",
                color=discord.Color.red()
            )
            embed.set_footer(text="幽幽子：強者的亡魂賞花都很安靜…")
            await ctx.respond(embed=embed, ephemeral=True)
            return

        try:
            mute_time = datetime.utcnow() + timedelta(minutes=duration)
            await member.timeout(mute_time, reason=f"Timeout by {ctx.author} for {duration} minutes")
            embed = discord.Embed(
                title="⛔ 冥界禁言令 ⛔",
                description=(
                    f"{member.mention} 被幽幽子禁言 **{duration} 分鐘**！\n"
                    "賞花時要安靜，亡魂們才會幸福～"
                ),
                color=discord.Color.from_rgb(205, 133, 232)
            )
            embed.set_footer(text="幽幽子：安靜下來，享受櫻花與美食吧～")
            await ctx.respond(embed=embed, ephemeral=False)
        except discord.Forbidden:
            embed = discord.Embed(
                title="❌ 禁言失敗",
                description=f"幽幽子的法力被限制，無法禁言 {member.mention}。",
                color=discord.Color.red()
            )
            embed.set_footer(text="幽幽子：有時候亡魂太強也沒辦法呢…")
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
            embed.set_footer(text="幽幽子：亡魂太吵了，系統都崩潰啦～")
            await ctx.respond(embed=embed, ephemeral=True)

def setup(bot: commands.Bot):
    bot.add_cog(Timeout(bot))