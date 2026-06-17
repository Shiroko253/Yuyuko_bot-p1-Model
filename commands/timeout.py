import discord
from discord.ext import commands
from datetime import datetime, timedelta
from typing import Optional
from zoneinfo import ZoneInfo
import logging

logger = logging.getLogger("SakuraBot.Timeout")


class Timeout(commands.Cog):
    """
    🌸 幽幽子的禁言法令 🌸
    讓嘈雜的亡魂在櫻花樹下安靜片刻～
    """

    def __init__(self, bot: discord.Bot):
        self.bot = bot
        self.tz  = ZoneInfo("Asia/Taipei")
        logger.info("🌸 禁言術式已於櫻花樹下甦醒")

    @discord.slash_command(
        name="timeout",
        description="🌸 幽幽子法令：讓嘈雜的亡魂安靜片刻（以分鐘為單位）"
    )
    async def timeout(
        self,
        ctx: discord.ApplicationContext,
        # [修復 #1] Option 改為預設值寫法，消除 Pylance 警告
        member: Optional[discord.Member] = discord.Option(
            discord.Member,
            name="成員",
            description="要禁言的成員",
            required=True
        ),
        duration: Optional[int] = discord.Option(
            int,
            name="時長",
            description="禁言時長（分鐘，最長 27 天）",
            required=True,
            min_value=1,
            max_value=40320
        ),
        reason: Optional[str] = discord.Option(
            str,
            name="原因",
            description="禁言原因（選填）",
            required=False,
            default=None
        )
    ):
        try:
            if not ctx.author.guild_permissions.moderate_members:
                await ctx.respond(
                    embed=discord.Embed(
                        title="🌸 權限不足!",
                        description="呼呼～只有冥界主人才有權讓亡魂安靜哦!\n你需要「管理成員」權限才能使用此術式～",
                        color=discord.Color.from_rgb(205, 133, 232)
                    ).set_footer(
                        text="賞花時要保持安靜 · 幽幽子",
                        icon_url=self.bot.user.avatar.url if self.bot.user.avatar else None
                    ),
                    ephemeral=True
                )
                return

            await ctx.defer()

            if not ctx.guild or not ctx.guild.me:
                await ctx.followup.send(
                    embed=discord.Embed(
                        title="❌ 操作失敗",
                        description="此指令只能在冥界（伺服器）內使用，幽幽子迷路了...",
                        color=discord.Color.red()
                    ).set_footer(text="冥界的路好複雜啊 · 幽幽子"),
                    ephemeral=True
                )
                return

            bot_member = ctx.guild.me

            if not bot_member.guild_permissions.moderate_members:
                await ctx.followup.send(
                    embed=discord.Embed(
                        title="❌ 機器人權限不足",
                        description="呀啦呀啦～幽幽子沒有法力可以禁言亡魂!\n請賦予機器人「管理成員」權限～",
                        color=discord.Color.red()
                    ).set_footer(text="權限不足，法術無法施展 · 幽幽子"),
                    ephemeral=True
                )
                return

            if member.id == ctx.author.id:
                await ctx.followup.send(
                    embed=discord.Embed(
                        title="🌸 術式無效",
                        description="呼呼～你不能禁言自己哦!\n要安靜的話，可以自己閉嘴呢～",
                        color=discord.Color.gold()
                    ).set_footer(text="自我禁言不需要法術 · 幽幽子"),
                    ephemeral=True
                )
                return

            if member.id == self.bot.user.id:
                await ctx.followup.send(
                    embed=discord.Embed(
                        title="🌸 術式無效",
                        description="呼呼～幽幽子可不會自己禁言自己呢!\n要是幽幽子安靜了，誰來賞花吃點心呢?",
                        color=discord.Color.gold()
                    ).set_thumbnail(
                        url=self.bot.user.avatar.url if self.bot.user.avatar else None
                    ).set_footer(text="幽幽子需要說話才能吃飽 · 幽幽子"),
                    ephemeral=True
                )
                return

            if member.id == ctx.guild.owner_id:
                await ctx.followup.send(
                    embed=discord.Embed(
                        title="🌸 無法施法",
                        description=f"呼呼～{member.mention} 是這個冥界的主人呢!\n幽幽子可不敢對主人施展禁言術式～",
                        color=discord.Color.gold()
                    ).set_footer(text="冥界主人的權威不可侵犯 · 幽幽子"),
                    ephemeral=True
                )
                return

            if member.top_role >= bot_member.top_role:
                await ctx.followup.send(
                    embed=discord.Embed(
                        title="❌ 無法禁言",
                        description=f"呼呼～{member.mention} 的靈魂太強大了!\n他的角色階級比幽幽子還高，無法施展法術～",
                        color=discord.Color.red()
                    ).set_footer(text="強者的亡魂不受約束 · 幽幽子"),
                    ephemeral=True
                )
                return

            if member.top_role >= ctx.author.top_role and ctx.author.id != ctx.guild.owner_id:
                await ctx.followup.send(
                    embed=discord.Embed(
                        title="❌ 無法禁言",
                        description=f"呼呼～{member.mention} 的角色比你還高呢!\n你無法對階級更高的人使用此術式～",
                        color=discord.Color.red()
                    ).set_footer(text="尊重階級秩序 · 幽幽子"),
                    ephemeral=True
                )
                return

            try:
                mute_until   = datetime.now(self.tz) + timedelta(minutes=duration)
                full_reason  = f"被 {ctx.author.name} 禁言 {duration} 分鐘"
                if reason:
                    full_reason += f" | 原因: {reason}"

                await member.timeout(mute_until, reason=full_reason)

                hours    = duration // 60
                minutes_ = duration % 60
                parts    = []
                if hours:
                    parts.append(f"{hours} 小時")
                if minutes_ or not hours:
                    parts.append(f"{minutes_} 分鐘")
                time_str = " ".join(parts)

                embed = discord.Embed(
                    title="⛔ 冥界禁言令",
                    description=f"呼呼～{member.mention} 被幽幽子施展了禁言術式!\n在櫻花樹下安靜 **{time_str}** 吧～",
                    color=discord.Color.from_rgb(205, 133, 232),
                    timestamp=datetime.now(self.tz)
                )
                embed.add_field(
                    name="📋 禁言詳情",
                    value=f"```yaml\n目標: {member.name}\n時長: {time_str}\n執行者: {ctx.author.name}\n```",
                    inline=False
                )
                if reason:
                    embed.add_field(name="📝 禁言原因", value=f"```\n{reason}\n```", inline=False)
                embed.add_field(
                    name="⏰ 解禁時間",
                    value=f"<t:{int(mute_until.timestamp())}:F>",
                    inline=False
                )
                embed.set_footer(
                    text="安靜下來，享受櫻花與美食吧 · 幽幽子",
                    icon_url=self.bot.user.avatar.url if self.bot.user.avatar else None
                )
                embed.set_thumbnail(url=member.display_avatar.url)

                await ctx.followup.send(embed=embed)
                logger.info(
                    f"🔇 {ctx.author.name} 禁言了 {member.name} {duration} 分鐘"
                    + (f" | 原因: {reason}" if reason else "")
                )

                try:
                    dm_embed = discord.Embed(
                        title=f"🌸 你在 {ctx.guild.name} 被禁言了",
                        description=f"呼呼～你被幽幽子施展了禁言術式!\n請在櫻花樹下安靜 **{time_str}**～",
                        color=discord.Color.from_rgb(205, 133, 232)
                    )
                    if reason:
                        dm_embed.add_field(name="📝 原因", value=reason, inline=False)
                    dm_embed.add_field(
                        name="⏰ 解禁時間",
                        value=f"<t:{int(mute_until.timestamp())}:F>",
                        inline=False
                    )
                    dm_embed.set_footer(
                        text="請遵守伺服器規則 · 幽幽子",
                        icon_url=self.bot.user.avatar.url if self.bot.user.avatar else None
                    )
                    await member.send(embed=dm_embed)
                except (discord.Forbidden, discord.HTTPException):
                    logger.debug(f"無法向 {member.name} 發送禁言通知 DM")

            except discord.Forbidden:
                await ctx.followup.send(
                    embed=discord.Embed(
                        title="❌ 禁言失敗",
                        description=f"哎呀，幽幽子的法力被限制了...\n無法禁言 {member.mention}！",
                        color=discord.Color.red()
                    ).set_footer(text="有時候亡魂太強也沒辦法呢 · 幽幽子")
                )
                logger.warning(f"⚠️ 禁言失敗: {member.name} (Forbidden)")

            except discord.HTTPException as e:
                await ctx.followup.send(
                    embed=discord.Embed(
                        title="❌ 禁言失敗",
                        description=f"呼呼～操作失敗了...\n錯誤: {e}",
                        color=discord.Color.red()
                    ).set_footer(text="亡魂太吵，系統都崩潰啦 · 幽幽子"),
                    ephemeral=True
                )
                logger.error(f"❌ 禁言失敗: HTTPException - {e}")

        except Exception as e:
            logger.exception(f"❌ 禁言指令發生錯誤: {e}")
            error_embed = discord.Embed(
                title="❌ 術式崩壞",
                description="哎呀，執行禁言術式時遭遇了不明之力...\n請稍後再試或使用 `/feedback` 回報～",
                color=discord.Color.dark_red()
            ).set_footer(text="術式受阻，請稍後重試 · 幽幽子")
            try:
                if not ctx.interaction.response.is_done():
                    await ctx.respond(embed=error_embed, ephemeral=True)
                else:
                    await ctx.followup.send(embed=error_embed, ephemeral=True)
            except Exception:
                logger.exception("❌ 無法發送禁言錯誤訊息")


def setup(bot: discord.Bot):
    bot.add_cog(Timeout(bot))
    logger.info("🌸 禁言模組已於櫻花樹下綻放完成")
