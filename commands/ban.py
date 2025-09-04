import discord
from discord.ext import commands
import logging

def make_embed(title, description, color, footer=None):
    """
    幽幽子的 embed 工廠，讓訊息更優雅。
    """
    embed = discord.Embed(title=title, description=description, color=color)
    if footer:
        embed.set_footer(text=footer)
    return embed

class Ban(commands.Cog):
    """
    ✿ 幽幽子的冥界放逐 ✿
    把所有檢查、訊息、放逐通知都優雅地拆分，減少重複～
    """

    def __init__(self, bot):
        self.bot = bot

    async def check_target_valid(self, ctx, target):
        if target is None:
            return make_embed(
                "🌸 冥界放逐失敗",
                "❌ 幽幽子找不到這位靈魂，他可能早已離開冥界。",
                discord.Color.red(),
                "櫻花飄落之時，總有靈魂消散"
            )
        if target.id == ctx.user.id:
            return make_embed(
                "🌸 無法放逐自己",
                "⚠️ 嘻嘻，幽幽子不會讓你自己把自己放逐喔～",
                discord.Color.orange(),
                "自我放逐？靈魂還是留下吧～"
            )
        if target.id == ctx.guild.me.id:
            return make_embed(
                "🌸 無法放逐幽幽子",
                "⚠️ 幽幽子的靈魂太輕盈，怎麼也抓不住呢～",
                discord.Color.orange(),
                "幽幽子只會守護，不會被放逐"
            )
        if target == ctx.guild.owner:
            return make_embed(
                "🌸 不能放逐冥界主人",
                "⚠️ 冥界的主人是無法被放逐的哦～",
                discord.Color.orange(),
                "幽幽子會一直守護主人的靈魂"
            )
        return None

    async def check_permissions(self, ctx, target):
        if not ctx.user.guild_permissions.ban_members:
            return make_embed(
                "🌸 權限不足",
                "⚠️ 您沒有放逐靈魂的權限，幽幽子只能聽主人的話唷～",
                discord.Color.yellow(),
                "只有真正的亡魂主人才可放逐他人"
            )
        if not ctx.guild.me.guild_permissions.ban_members:
            return make_embed(
                "🌸 幽幽子權限不足",
                "⚠️ 幽幽子沒有放逐靈魂的權限，要幫我加一點力氣嗎？",
                discord.Color.yellow(),
                "請給幽幽子『封禁成員』的力量吧～"
            )
        if ctx.guild.me.top_role <= target.top_role:
            return make_embed(
                "🌸 放逐失敗",
                "⚠️ 幽幽子的身分組層級低於此靈魂，無法送他離開冥界～\n請將幽幽子的身分組調高一點，並確保有「封禁成員」權限。",
                discord.Color.yellow(),
                "靈魂的層級也有高低，冥界規則不可違"
            )
        return None

    async def send_dm_notification(self, target, guild_name, reason_text):
        try:
            dm_embed = make_embed(
                "🌸 你被幽幽子從冥界放逐了",
                f"你已被伺服器 **{guild_name}** 的幽幽子冥界放逐。\n原因：{reason_text}\n\n冥界的櫻花瓣為你飄落，願你在新的世界找到歸宿～",
                discord.Color.red(),
                "冥界之外，還有新的靈魂故事"
            )
            await target.send(embed=dm_embed)
            return True
        except discord.Forbidden:
            return False
        except Exception as e:
            logging.error(f"DM 發送失敗: {e}")
            return False

    @discord.slash_command(name="ban", description="幽幽子冥界放逐：溫柔送走靈魂～")
    async def ban(
        self,
        ctx: discord.ApplicationContext,
        member: discord.Member,
        reason: str = None
    ):
        await ctx.defer(ephemeral=False)

        target = member if isinstance(member, discord.Member) else ctx.guild.get_member(member.id) if ctx.guild else None

        # 檢查對象合法性
        invalid_embed = await self.check_target_valid(ctx, target)
        if invalid_embed:
            await ctx.followup.send(embed=invalid_embed, ephemeral=True)
            return

        # 權限檢查
        permission_embed = await self.check_permissions(ctx, target)
        if permission_embed:
            await ctx.followup.send(embed=permission_embed, ephemeral=True)
            return

        # reason 格式統一
        reason_text = f"[幽幽子放逐] {reason or '未提供原因'}"

        # DM 通知
        dm_sent = await self.send_dm_notification(target, ctx.guild.name, reason_text)

        # 放逐行為
        try:
            await target.ban(reason=reason_text)
            embed = make_embed(
                "🌸 冥界放逐成功",
                (
                    f"✅ 靈魂 **{target}** 已被幽幽子溫柔地送離冥界～\n"
                    f"原因：{reason_text}\n"
                    f"{'（幽幽子未能成功私訊通知該靈魂）' if not dm_sent else '（幽幽子已將放逐訊息送達）'}\n\n"
                    "願櫻花指引他的靈魂前往新的世界。"
                ),
                discord.Color.purple(),
                "幽幽子的冥界，靈魂的故事永遠繼續～"
            )
            await ctx.followup.send(embed=embed, ephemeral=False)
        except Exception as e:
            embed = make_embed(
                "🌸 冥界放逐失敗",
                f"❌ 放逐時冥界出現靈魂波動錯誤：{e}\n幽幽子會再試著幫你處理的～",
                discord.Color.red(),
                "有時候，靈魂的命運也是謎"
            )
            await ctx.followup.send(embed=embed, ephemeral=True)

def setup(bot):
    """
    ✿ 幽幽子優雅地將冥界放逐功能裝進 bot 裡 ✿
    """
    bot.add_cog(Ban(bot))