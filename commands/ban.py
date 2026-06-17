import discord
from discord.ext import commands
import random
import logging

logger = logging.getLogger("SakuraBot.commands.ban")


def make_embed(title, description, color, footer=None, thumbnail=None):
    """幽幽子的 embed 工廠，讓訊息更優雅。"""
    embed = discord.Embed(
        title=title,
        description=description,
        color=color,
        timestamp=discord.utils.utcnow()
    )
    if footer:
        embed.set_footer(text=footer)
    if thumbnail:
        embed.set_thumbnail(url=thumbnail)
    return embed


class Ban(commands.Cog):
    """
    ✿ 幽幽子的冥界放逐 ✿
    操縱死亡的能力，將靈魂送往彼岸～
    支援封禁伺服器內成員（member 參數）或不在伺服器的用戶（user_id 參數）
    """

    def __init__(self, bot: discord.Bot):
        self.bot = bot

        self.banish_quotes = [
            "櫻花飄落之際，願你的靈魂安息。",
            "西行妖樹下，生與死不過一念之間。",
            "冥界的櫻花為你綻放，前往彼岸吧。",
            "幽幽子會記住你的，在櫻花盛開的季節。",
            "生者與死者，終將在櫻花樹下重逢。",
            "死亡並非終結，而是新生的開始。"
        ]

        self.failure_quotes = [
            "哎呀～這次失敗了呢。",
            "冥界的力量似乎不夠呢...",
            "櫻花飄亂了，下次會順利的。",
            "嗯～靈魂的波動有點奇怪。"
        ]

    async def _resolve_target(self, ctx, member, user_id: str):
        if member is None and not user_id:
            return None, None, make_embed("🌸 請指定目標", "請選擇伺服器成員，或輸入 User ID。", discord.Color.red())
        if member is not None:
            return member.id, member, None
        try:
            target_id = int(user_id.strip())
        except ValueError:
            return None, None, make_embed("🌸 ID 格式錯誤", "不是有效的 Discord User ID。\n請輸入純數字，例如 `123456789012345678`。", discord.Color.red())

        target_user = self.bot.get_user(target_id)
        if target_user is None:
            try:
                target_user = await self.bot.fetch_user(target_id)
            except discord.NotFound:
                pass
            except Exception as e:
                logger.warning(f"fetch_user({target_id}) 失敗: {e}")
        return target_id, target_user, None

    async def _check_target_valid(self, ctx, target_id: int, target_user):
        if target_id == ctx.user.id:
            return make_embed("🌸 自我放逐？", "嘻嘻～你想讓幽幽子放逐自己嗎？\n這可不行哦，靈魂還要好好守護呢！\n\n*生命如櫻，怎可自凋*", discord.Color.from_rgb(255, 192, 203), "幽幽子不會讓你做傻事的～")
        if target_id == self.bot.user.id:
            return make_embed("🌸 無法放逐幽幽子", "啊啦～想讓幽幽子離開冥界嗎？\n我可是這裡的主人，怎麼可能被放逐呢～\n\n*亡靈公主，永駐白玉樓*", discord.Color.from_rgb(230, 230, 250), "幽幽子會一直守護著這片冥界哦♪")
        if ctx.guild.owner_id == target_id:
            return make_embed("🌸 冥界之主不可觸", "這位可是冥界的主人呢～\n連幽幽子也無法違逆主人的意志。\n\n*主從有序，冥界之理*", discord.Color.from_rgb(255, 215, 0), "主人的靈魂，幽幽子會永遠守護")
        return None

    async def _check_permissions(self, ctx, target_user):
        if not ctx.user.guild_permissions.ban_members:
            return make_embed("🌸 權限不足", "你還沒有操縱死亡的能力呢～\n只有擁有**封禁成員**權限的人，才能請幽幽子放逐靈魂。\n\n*死亡之力，非凡人可掌*", discord.Color.from_rgb(255, 165, 0), "向管理員申請權限吧～")
        bot_member = ctx.guild.me
        if not bot_member.guild_permissions.ban_members:
            return make_embed("🌸 幽幽子的力量不夠", "哎呀～幽幽子沒有**封禁成員**的權限呢。\n請讓管理員賜予幽幽子這份力量吧！\n\n*無力之時，櫻花亦無法飄落*", discord.Color.from_rgb(255, 140, 0), "給幽幽子『封禁成員』權限就可以了～")
        if isinstance(target_user, discord.Member):
            if bot_member.top_role <= target_user.top_role:
                return make_embed("🌸 身份層級不足", f"這位靈魂的身份層級 ({target_user.top_role.mention}) 高於幽幽子 ({bot_member.top_role.mention})...\n冥界的規則是無法違背的呢。\n\n*階級有別，靈魂亦有高低*", discord.Color.from_rgb(255, 127, 80), "請將幽幽子的身份組移到更高位置～")
        return None

    async def _send_dm_notification(self, target_user, guild_name: str, reason_text: str, banner_name: str) -> bool:
        if target_user is None:
            return False
        try:
            dm_embed = discord.Embed(
                title="🌸 冥界的邀請函",
                description=(
                    "### 來自西行寺幽幽子的訊息\n\n"
                    f"> 在 **{guild_name}** 的白玉樓中，\n"
                    "> 幽幽子決定將你的靈魂送往彼岸。\n\n"
                    f"**執行者:** {banner_name}\n"
                    f"**原因:** {reason_text}\n\n"
                    "───────────────────\n\n"
                    "*櫻花飄落之際，生死不過一念。*\n"
                    "*願你在新的世界找到歸宿。*\n\n"
                    "───────────────────\n\n"
                    "如有疑問，請聯繫伺服器管理員。"
                ),
                color=discord.Color.from_rgb(255, 182, 193),
                timestamp=discord.utils.utcnow()
            )
            dm_embed.set_footer(text="西行寺幽幽子 · 冥界的亡靈公主", icon_url=self.bot.user.display_avatar.url)
            dm_embed.set_thumbnail(url=target_user.display_avatar.url)
            await target_user.send(embed=dm_embed)
            return True
        except discord.Forbidden:
            logger.warning(f"無法發送私訊給 {target_user}（權限不足）")
            return False
        except Exception as e:
            logger.error(f"發送私訊失敗: {e}")
            return False

    @discord.slash_command(
        name="ban",
        description="🌸 幽幽子的冥界放逐：選擇成員或輸入 User ID 皆可"
    )
    async def ban(
        self,
        ctx: discord.ApplicationContext,
        # [Debug 修復] 明確指定 input_type 為對應的型別！
        # 這是 Pycord 最穩健的寫法，能徹底消除 IDE 警告並確保 min_value 正確運作。
        member: discord.Member = discord.Option(
            discord.Member,
            description="選擇伺服器內的成員（與 user_id 擇一，優先使用此項）",
            required=False,
            default=None
        ),
        user_id: str = discord.Option(
            str,
            description="不在伺服器時輸入 User ID（Hackban 模式）",
            required=False,
            default=""
        ),
        reason: str = discord.Option(
            str,
            description="放逐原因", 
            required=False, 
            default=None
        ),
        # [Debug 修復] 使用 discord.SlashCommandOptionType.integer 確保 Pycord 100% 識別為整數
        # 這樣 min_value 和 max_value 就不會再報 AttributeError 了！
        delete_messages: int = discord.Option(
            discord.SlashCommandOptionType.integer,
            description="刪除幾天內的訊息（0–7，預設 0）",
            required=False,
            default=0,
            min_value=0,
            max_value=7
        )
    ):
        await ctx.defer(ephemeral=False)

        target_id, target_user, resolve_error = await self._resolve_target(ctx, member, user_id)
        if resolve_error:
            await ctx.followup.send(embed=resolve_error, ephemeral=True)
            return

        valid_error = await self._check_target_valid(ctx, target_id, target_user)
        if valid_error:
            await ctx.followup.send(embed=valid_error, ephemeral=True)
            return

        perm_error = await self._check_permissions(ctx, target_user)
        if perm_error:
            await ctx.followup.send(embed=perm_error, ephemeral=True)
            return

        delete_message_seconds = delete_messages * 86400
        reason_text = reason or "未說明原因，隨櫻花飄落而去"
        is_hackban = not isinstance(target_user, discord.Member)
        mode_tag = "Hackban" if is_hackban else "冥界放逐"
        full_reason = f"[幽幽子 {mode_tag}] {reason_text}"

        dm_sent = await self._send_dm_notification(target_user, ctx.guild.name, reason_text, ctx.user.name)

        try:
            await ctx.guild.ban(
                discord.Object(id=target_id),
                reason=full_reason,
                delete_message_seconds=delete_message_seconds
            )

            display_name = str(target_user) if target_user else f"ID: {target_id}"
            avatar_url = target_user.display_avatar.url if target_user else None
            mode_display = "🔍 Hackban（ID 封禁）" if is_hackban else "👤 伺服器成員封禁"
            dm_display = "✅ 已送達" if dm_sent else "❌ 未送達（對方可能關閉私訊）"
            msg_display = f"已刪除 {delete_messages} 天內的訊息" if delete_messages > 0 else "未刪除訊息"

            success_embed = discord.Embed(
                title=f"🌸 冥界放逐完成{'（Hackban）' if is_hackban else ''}",
                description=(
                    "### 靈魂已送往彼岸\n\n"
                    f"**被放逐者:** {display_name} (`{target_id}`)\n"
                    f"**執行者:** {ctx.user.mention}\n"
                    f"**原因:** {reason_text}\n"
                    f"**模式:** {mode_display}\n"
                    f"**訊息清理:** {msg_display}\n"
                    f"**私訊通知:** {dm_display}\n\n"
                    "───────────────────\n\n"
                    f"*{random.choice(self.banish_quotes)}*"
                ),
                color=discord.Color.from_rgb(147, 112, 219),
                timestamp=discord.utils.utcnow()
            )
            if avatar_url:
                success_embed.set_thumbnail(url=avatar_url)
            success_embed.set_footer(text="西行寺幽幽子 · 操縱死亡的能力", icon_url=self.bot.user.display_avatar.url)

            await ctx.followup.send(embed=success_embed)
            logger.info(f"{ctx.user} ({ctx.user.id}) 封禁了 {display_name} ({target_id}), 模式: {mode_tag}, 原因: {reason_text}")

        except discord.NotFound:
            await ctx.followup.send(embed=make_embed("🌸 找不到此靈魂", f"ID `{target_id}` 不存在或已被封禁。", discord.Color.red()), ephemeral=True)
        except discord.Forbidden:
            await ctx.followup.send(embed=make_embed("🌸 冥界放逐失敗", "幽幽子的力量無法觸及這個靈魂...\n\n**可能的原因:**\n• 幽幽子的身份組層級不夠高\n• 缺少必要的權限\n• 目標擁有管理員權限\n\n*{}*".format(random.choice(self.failure_quotes)), discord.Color.red(), "請檢查幽幽子的權限設定～"), ephemeral=True)
            logger.error(f"放逐失敗（Forbidden）: {target_id}")
        except Exception as e:
            await ctx.followup.send(embed=make_embed("🌸 冥界波動異常", f"在放逐靈魂時，冥界出現了意外的波動...\n\n**錯誤訊息:** `{str(e)}`\n\n*{random.choice(self.failure_quotes)}*", discord.Color.red(), "請稍後再試，或聯繫管理員"), ephemeral=True)
            logger.exception(f"放逐指令發生錯誤: {e}")


def setup(bot: discord.Bot):
    bot.add_cog(Ban(bot))
    logger.info("冥界放逐系統已載入")
