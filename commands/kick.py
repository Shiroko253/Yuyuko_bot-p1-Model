import discord
from discord.ext import commands
import logging

logger = logging.getLogger("SakuraBot.Kick")


class Kick(commands.Cog):
    """幽幽子的放逐之術，將迷途的靈魂送離冥界花園"""

    def __init__(self, bot):
        self.bot = bot
        logger.info("🌸 放逐靈魂指令已甦醒")

    @discord.slash_command(
        name="kick",
        description="幽幽子的放逐靈魂指令～將迷途的靈魂送出冥界花園"
    )
    async def kick(
        self,
        ctx: discord.ApplicationContext,
        # [Debug 修復 #1] 改用 Pycord 最標準的等號右側寫法，徹底消除 Pylance 的型別警告
        # 同時移除了 Annotated，避免 str 與 None 的型別衝突
        member: discord.Member = discord.Option(
            discord.Member, 
            description="要放逐的靈魂"
        ),
        reason: str = discord.Option(
            str, 
            description="原因", 
            required=False, 
            default=None
        ),
    ):
        """幽幽子輕撫櫻花，放逐不守規矩的靈魂"""

        # [Debug 修復 #2] 移除了 isinstance(member, discord.Member) 檢查
        # 原因：在 Slash Command 中，如果參數定義為 discord.Member，Pycord 的參數解析器
        # 已經保證了傳進來的绝对是伺服器內的成員。如果使用者輸入不在伺服器的 ID，
        # Pycord 會在執行這個函數之前就自動報錯，所以這個 if 永遠不會被觸發 (死碼)。

        if member.id == ctx.user.id:
            await ctx.respond(
                embed=self._create_embed(
                    title="🌸 靈魂無法自我放逐",
                    description="幽幽子溫柔地說：你不能放逐自己的靈魂哦～\n在冥界花園中，請善待自己。",
                    color=discord.Color.pink(),
                    footer="櫻花下的守護"
                ),
                ephemeral=True
            )
            return

        if member.id == ctx.guild.me.id:
            await ctx.respond(
                embed=self._create_embed(
                    title="🌸 無法放逐冥界守護者",
                    description="幽幽子輕笑道：我是這裡的主人，你可踢不走我呢～\n我會永遠守護這座花園。",
                    color=discord.Color.pink(),
                    footer="永恆的守護誓言"
                ),
                ephemeral=True
            )
            return

        if not ctx.user.guild_permissions.kick_members:
            await ctx.respond(
                embed=self._create_embed(
                    title="🌸 靈魂之力不足",
                    description="你的靈魂力量尚未達到放逐他人的境界～\n請向擁有『踢出成員』權限的管理者求助。",
                    color=discord.Color.gold(),
                    footer="修煉靈魂，方能掌控冥界秩序"
                ),
                ephemeral=True
            )
            return

        if not ctx.guild.me.guild_permissions.kick_members:
            await ctx.respond(
                embed=self._create_embed(
                    title="🌸 幽幽子的力量被封印了",
                    description="幽幽子的靈魂未被賦予放逐之力～\n請授予我『踢出成員』權限，讓我能守護花園的秩序。",
                    color=discord.Color.gold(),
                    footer="解除封印，恢復冥界秩序"
                ),
                ephemeral=True
            )
            return

        if ctx.guild.me.top_role <= member.top_role:
            await ctx.respond(
                embed=self._create_embed(
                    title="🌸 無法放逐更高階的靈魂",
                    description=(
                        f"目標靈魂 **{member.mention}** 的階級高於幽幽子～\n"
                        f"幽幽子角色: `{ctx.guild.me.top_role.name}`\n"
                        f"目標角色: `{member.top_role.name}`\n\n"
                        "請將幽幽子的角色提升至更高層級，方能維持冥界秩序。"
                    ),
                    color=discord.Color.gold(),
                    footer="冥界的階級秩序不可逆"
                ),
                ephemeral=True
            )
            return

        dm_status = await self._send_kick_notification(member, ctx.guild.name, reason)

        try:
            kick_reason = reason or f"由 {ctx.user.name} 施展放逐之術"
            await member.kick(reason=kick_reason)

            logger.info(f"🌸 靈魂 {member} (ID:{member.id}) 已被 {ctx.user} 放逐，原因: {kick_reason}")

            description = (
                f"**被放逐的靈魂**: {member.mention} (`{member.name}`)\n"
                f"**執行者**: {ctx.user.mention}\n"
                f"**原因**: {reason or '未提供原因'}\n"
            )
            if not dm_status:
                description += "\n⚠️ *無法私訊通知該靈魂（可能已關閉私訊）*"

            await ctx.respond(
                embed=self._create_embed(
                    title="🌸 靈魂已被放逐",
                    description=description,
                    color=discord.Color.red(),
                    footer="櫻花飄落，秩序重歸於寂"
                ),
                ephemeral=False
            )

        except discord.Forbidden as e:
            logger.error(f"❌ 放逐失敗（權限不足）: {e}")
            await ctx.respond(
                embed=self._create_embed(
                    title="🌸 放逐失敗",
                    description="幽幽子的靈魂力量被阻擋了～\n可能是權限配置有誤或目標擁有特殊保護。",
                    color=discord.Color.dark_red(),
                    footer="請檢查 Bot 權限設定"
                ),
                ephemeral=True
            )
        except Exception as e:
            logger.error(f"❌ 放逐時發生未知錯誤: {e}", exc_info=True)
            await ctx.respond(
                embed=self._create_embed(
                    title="🌸 放逐術式失敗",
                    description=f"在執行放逐時遭遇了神秘的阻力...\n錯誤: `{str(e)}`",
                    color=discord.Color.dark_red(),
                    footer="若問題持續，請聯繫冥界管理者"
                ),
                ephemeral=True
            )

    async def _send_kick_notification(self, member: discord.Member, guild_name: str, reason: str) -> bool:
        try:
            embed = discord.Embed(
                title="🌸 你的靈魂已被放逐",
                description=(
                    f"你已被伺服器 **{guild_name}** 放逐出冥界花園。\n\n"
                    f"**原因**: {reason or '未提供具體原因'}\n\n"
                    "櫻花飄落之時，便是離別之刻。\n"
                    "若有疑問，請聯繫該伺服器的管理者。"
                ),
                color=discord.Color.red(),
                timestamp=discord.utils.utcnow()
            )
            embed.set_footer(
                text="幽幽子的冥界秩序",
                # [Debug 修復 #3] 使用 display_avatar，確保縮圖 100% 顯示
                icon_url=self.bot.user.display_avatar.url
            )
            await member.send(embed=embed)
            logger.info(f"✅ 已私訊通知被踢用戶 {member}")
            return True
        except discord.Forbidden:
            logger.warning(f"⚠️ 無法私訊 {member}（用戶可能關閉了私訊）")
            return False
        except Exception as e:
            logger.error(f"❌ 私訊通知失敗: {e}")
            return False

    @staticmethod
    def _create_embed(title: str, description: str, color: discord.Color, footer: str = None) -> discord.Embed:
        embed = discord.Embed(
            title=title,
            description=description,
            color=color,
            timestamp=discord.utils.utcnow()
        )
        if footer:
            embed.set_footer(text=footer)
        return embed


def setup(bot):
    bot.add_cog(Kick(bot))
    logger.info("✨ 放逐靈魂 Cog 已載入完成")
