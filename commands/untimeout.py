import discord
from discord.ext import commands
from datetime import datetime
from zoneinfo import ZoneInfo
import logging

logger = logging.getLogger("SakuraBot.Untimeout")


class Untimeout(commands.Cog):
    """
    🌸 幽幽子的解禁法令 🌸
    讓被禁言的亡魂重獲自由,在櫻花樹下再次歌唱～
    """

    def __init__(self, bot: discord.Bot):
        self.bot = bot
        self.tz = ZoneInfo('Asia/Taipei')
        logger.info("🌸 解禁術式已於櫻花樹下甦醒")

    @discord.slash_command(
        name="untimeout",
        description="🌸 幽幽子法令:解除亡魂的禁言狀態"
    )
    async def untimeout(
        self,
        ctx: discord.ApplicationContext,
        member: discord.Member = discord.Option(
            discord.Member,
            name="成員",
            description="要解除禁言的成員",
            required=True
        )
    ):
        """
        解除指定成員的禁言狀態

        只有擁有管理成員權限的人才能使用,
        幽幽子會讓亡魂重獲自由～
        """
        try:
            # ----------- 權限檢查 -----------
            if not ctx.author.guild_permissions.moderate_members:
                embed = discord.Embed(
                    title="🌸 權限不足!",
                    description=(
                        "呼呼～只有冥界主人才有權放出亡魂的聲音哦!\n"
                        "你需要「管理成員」權限才能使用此術式～"
                    ),
                    color=discord.Color.from_rgb(205, 133, 232)
                )
                embed.set_footer(
                    text="賞花時要安靜,解除禁言也要有規則 · 幽幽子",
                    icon_url=self.bot.user.avatar.url if self.bot.user.avatar else None
                )
                await ctx.respond(embed=embed, ephemeral=True)
                return

            await ctx.defer()

            # ----------- 環境檢查 -----------
            if not ctx.guild or not ctx.guild.me:
                embed = discord.Embed(
                    title="❌ 操作失敗",
                    description="此指令只能在冥界(伺服器)內使用,\n幽幽子迷路了...",
                    color=discord.Color.red()
                )
                embed.set_footer(text="冥界的路好複雜啊 · 幽幽子")
                await ctx.followup.send(embed=embed, ephemeral=True)
                return

            bot_member = ctx.guild.me

            # ----------- 權限檢查:機器人 -----------
            if not bot_member.guild_permissions.moderate_members:
                embed = discord.Embed(
                    title="❌ 機器人權限不足",
                    description=(
                        "呀啦呀啦～幽幽子沒有法力可以解除禁言!\n"
                        "請賦予機器人「管理成員」權限～"
                    ),
                    color=discord.Color.red()
                )
                embed.set_footer(text="權限不足,法術無法施展 · 幽幽子")
                await ctx.followup.send(embed=embed, ephemeral=True)
                return

            # ----------- 檢查 Pycord 支援的屬性 -----------
            if not hasattr(member, "communication_disabled_until"):
                # 這表示使用的 pycord 版本不支援 timeout API
                embed = discord.Embed(
                    title="❌ 版本不支援",
                    description=(
                        "你目前使用的 Pycord 版本似乎不支援解除禁言的屬性。\n"
                        "請升級 py-cord (`pip install -U py-cord`) 至 v2.x 以上，"
                        "或使用支援 `communication_disabled_until` 的套件版本。"
                    ),
                    color=discord.Color.red()
                )
                embed.set_footer(text="請升級 Pycord 後重試 · 幽幽子")
                await ctx.followup.send(embed=embed, ephemeral=True)
                return

            # ----------- 檢查是否被禁言 -----------
            comm_disabled_until = member.communication_disabled_until
            now = discord.utils.utcnow()
            if not comm_disabled_until or comm_disabled_until < now:
                embed = discord.Embed(
                    title="ℹ️ 亡魂本就自由!",
                    description=(
                        f"{member.mention} 現在已是自由的亡魂,\n"
                        "並沒有被禁言哦,無需解除～"
                    ),
                    color=discord.Color.blue()
                )
                embed.set_thumbnail(url=member.display_avatar.url)
                embed.set_footer(
                    text="自由靈魂才能賞花、吃點心 · 幽幽子",
                    icon_url=self.bot.user.avatar.url if self.bot.user.avatar else None
                )
                await ctx.followup.send(embed=embed, ephemeral=True)
                return

            # ----------- 記錄原禁言信息 -----------
            original_timeout = comm_disabled_until
            remaining_time = (original_timeout - now).total_seconds()
            if remaining_time < 0:
                remaining_time = 0
            remaining_minutes = int(remaining_time / 60)
            remaining_hours = remaining_minutes // 60
            remaining_mins = remaining_minutes % 60

            time_str = ""
            if remaining_hours > 0:
                time_str += f"{remaining_hours} 小時 "
            if remaining_mins > 0 or remaining_hours == 0:
                time_str += f"{remaining_mins} 分鐘"

            # ----------- 執行解除禁言 -----------
            try:
                # use the Pycord attribute name
                await member.edit(
                    communication_disabled_until=None,
                    reason=f"被 {ctx.author.name} ({ctx.author.id}) 解除禁言"
                )

                # ----------- 成功回應 -----------
                embed = discord.Embed(
                    title="🔓 幽幽子解除冥界禁言令!",
                    description=(
                        f"呼呼～{member.mention} 的禁言狀態已被幽幽子解除!\n"
                        "亡魂可以再次在櫻花樹下歌唱啦～"
                    ),
                    color=discord.Color.from_rgb(144, 238, 144),  # 淺綠色
                    timestamp=datetime.now(self.tz)
                )

                embed.add_field(
                    name="📋 解禁詳情",
                    value=(
                        f"```yaml\n"
                        f"解禁對象: {member.name}\n"
                        f"執行者: {ctx.author.name}\n"
                        f"剩餘時間: {time_str}\n"
                        f"```"
                    ),
                    inline=False
                )

                embed.add_field(
                    name="🌸 溫馨提醒",
                    value=(
                        "• 請遵守伺服器規則\n"
                        "• 避免再次被禁言\n"
                        "• 珍惜發言的權利"
                    ),
                    inline=False
                )

                embed.set_footer(
                    text="賞花、吃點心、暢所欲言! · 幽幽子",
                    icon_url=self.bot.user.avatar.url if self.bot.user.avatar else None
                )
                embed.set_thumbnail(url=member.display_avatar.url)

                await ctx.followup.send(embed=embed)

                logger.info(
                    f"🔓 {ctx.author.name} 解除了 {member.name} 的禁言 "
                    f"(原剩餘時間: {time_str})"
                )

                # ----------- 嘗試 DM 通知 -----------
                try:
                    dm_embed = discord.Embed(
                        title=f"🌸 你在 {ctx.guild.name} 的禁言已解除",
                        description=(
                            "呼呼～幽幽子解除了你的禁言術式!\n"
                            "你可以再次在冥界自由發言了～"
                        ),
                        color=discord.Color.from_rgb(144, 238, 144)
                    )

                    dm_embed.add_field(
                        name="📋 解禁信息",
                        value=(
                            f"```yaml\n"
                            f"解禁者: {ctx.author.name}\n"
                            f"原剩餘時間: {time_str}\n"
                            f"```"
                        ),
                        inline=False
                    )

                    dm_embed.add_field(
                        name="💡 溫馨提醒",
                        value="請遵守伺服器規則,避免再次被禁言哦～",
                        inline=False
                    )

                    dm_embed.set_footer(
                        text="珍惜發言權利 · 幽幽子",
                        icon_url=self.bot.user.avatar.url if self.bot.user.avatar else None
                    )

                    await member.send(embed=dm_embed)
                except (discord.Forbidden, discord.HTTPException):
                    logger.debug(f"無法向 {member.name} 發送解禁通知 DM")

            except discord.Forbidden:
                embed = discord.Embed(
                    title="❌ 解除禁言失敗",
                    description=(
                        f"哎呀,幽幽子的法力被限制了...\n"
                        f"無法解除 {member.mention} 的禁言!\n\n"
                        "可能的原因:\n"
                        "• 目標擁有管理員權限\n"
                        "• 機器人權限不足\n"
                        "• 角色階級問題"
                    ),
                    color=discord.Color.red()
                )
                embed.set_footer(text="有時候亡魂太強也沒辦法呢 · 幽幽子")
                await ctx.followup.send(embed=embed)
                logger.warning(f"⚠️ 解除禁言失敗: {member.name} (Forbidden)")

            except TypeError as e:
                # This often indicates the installed library version does not accept the kwarg
                embed = discord.Embed(
                    title="❌ 解除禁言失敗（版本不相容）",
                    description=(
                        "幽幽子試圖解除禁言，但所使用的 Discord 函式庫版本不支援 "
                        "`communication_disabled_until` 參數。\n"
                        "請升級 py-cord (`pip install -U py-cord`) 至 v2.x 以上，"
                        "或改用支援的版本後重試。\n"
                        f"錯誤: {e}"
                    ),
                    color=discord.Color.red()
                )
                embed.set_footer(text="請升級函式庫後重試 · 幽幽子")
                await ctx.followup.send(embed=embed, ephemeral=True)
                logger.error(f"❌ 解除禁言失敗: TypeError - {e}")

            except discord.HTTPException as e:
                embed = discord.Embed(
                    title="❌ 解除禁言失敗",
                    description=f"呼呼～操作失敗了...\n錯誤: {e}",
                    color=discord.Color.red()
                )
                embed.set_footer(text="冥界的網路好像不太穩 · 幽幽子")
                await ctx.followup.send(embed=embed, ephemeral=True)
                logger.error(f"❌ 解除禁言失敗: HTTPException - {e}")

        except Exception as e:
            logger.exception(f"❌ 解除禁言指令發生錯誤: {e}")
            error_embed = discord.Embed(
                title="❌ 術式崩壞",
                description=(
                    "哎呀,執行解禁術式時遭遇了不明之力...\n"
                    "請稍後再試或使用 `/feedback` 回報給幽幽子的主人～"
                ),
                color=discord.Color.dark_red()
            )
            error_embed.set_footer(text="術式受阻,請稍後重試 · 幽幽子")

            try:
                if not ctx.interaction.response.is_done():
                    await ctx.respond(embed=error_embed, ephemeral=True)
                else:
                    await ctx.followup.send(embed=error_embed, ephemeral=True)
            except Exception:
                logger.exception("❌ 無法發送解禁錯誤訊息")


def setup(bot: discord.Bot):
    """將解禁術式註冊於幽幽子的靈魂"""
    bot.add_cog(Untimeout(bot))
    logger.info("🌸 解禁模組已於櫻花樹下綻放完成")
