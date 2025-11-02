import discord
from discord.ext import commands
from discord.commands import Option
import logging
import random

logger = logging.getLogger("SakuraBot.commands.ban")


def make_embed(title, description, color, footer=None, thumbnail=None):
    """
    幽幽子的 embed 工廠,讓訊息更優雅。
    """
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
    操縱死亡的能力,將靈魂送往彼岸～
    """

    def __init__(self, bot: discord.Bot):
        self.bot = bot
        
        # 幽幽子的放逐語錄
        self.banish_quotes = [
            "櫻花飄落之際,願你的靈魂安息。",
            "西行妖樹下,生與死不過一念之間。",
            "冥界的櫻花為你綻放,前往彼岸吧。",
            "幽幽子會記住你的,在櫻花盛開的季節。",
            "生者與死者,終將在櫻花樹下重逢。",
            "死亡並非終結,而是新生的開始。"
        ]
        
        # 失敗時的輕嘆
        self.failure_quotes = [
            "哎呀～這次失敗了呢。",
            "冥界的力量似乎不夠呢...",
            "櫻花飄亂了,下次會順利的。",
            "嗯～靈魂的波動有點奇怪。"
        ]

    async def check_target_valid(self, ctx: discord.ApplicationContext, target: discord.Member):
        """檢查封禁目標是否合法"""
        if target is None:
            return make_embed(
                "🌸 靈魂已散",
                "這位靈魂似乎早已離開冥界,幽幽子也無法觸及了呢...\n\n"
                "*櫻花飄落處,不見當年人*",
                discord.Color.from_rgb(255, 182, 193),
                "找不到的靈魂,就像消逝的櫻花"
            )
        
        if target.id == ctx.user.id:
            return make_embed(
                "🌸 自我放逐？",
                "嘻嘻～你想讓幽幽子放逐自己嗎？\n"
                "這可不行哦,靈魂還要好好守護呢！\n\n"
                "*生命如櫻,怎可自凋*",
                discord.Color.from_rgb(255, 192, 203),
                "幽幽子不會讓你做傻事的～"
            )
        
        if target.id == self.bot.user.id:
            return make_embed(
                "🌸 無法放逐幽幽子",
                "啊啦～想讓幽幽子離開冥界嗎？\n"
                "我可是這裡的主人,怎麼可能被放逐呢～\n\n"
                "*亡靈公主,永駐白玉樓*",
                discord.Color.from_rgb(230, 230, 250),
                "幽幽子會一直守護著這片冥界哦♪"
            )
        
        if target == ctx.guild.owner:
            return make_embed(
                "🌸 冥界之主不可觸",
                "這位可是冥界的主人呢～\n"
                "連幽幽子也無法違逆主人的意志。\n\n"
                "*主從有序,冥界之理*",
                discord.Color.from_rgb(255, 215, 0),
                "主人的靈魂,幽幽子會永遠守護"
            )
        
        return None

    async def check_permissions(self, ctx: discord.ApplicationContext, target: discord.Member):
        """檢查權限"""
        if not ctx.user.guild_permissions.ban_members:
            return make_embed(
                "🌸 權限不足",
                "你還沒有操縱死亡的能力呢～\n"
                "只有擁有**封禁成員**權限的人,才能請幽幽子放逐靈魂。\n\n"
                "*死亡之力,非凡人可掌*",
                discord.Color.from_rgb(255, 165, 0),
                "向管理員申請權限吧～"
            )
        
        if not self.bot.guild_permissions.ban_members:
            return make_embed(
                "🌸 幽幽子的力量不夠",
                "哎呀～幽幽子沒有**封禁成員**的權限呢。\n"
                "請讓管理員賜予幽幽子這份力量吧！\n\n"
                "*無力之時,櫻花亦無法飄落*",
                discord.Color.from_rgb(255, 140, 0),
                "給幽幽子『封禁成員』權限就可以了～"
            )
        
        if self.bot.top_role <= target.top_role:
            return make_embed(
                "🌸 身份層級不足",
                f"這位靈魂的身份層級 ({target.top_role.mention}) 高於幽幽子 ({self.bot.top_role.mention})...\n"
                "冥界的規則是無法違背的呢。\n\n"
                "*階級有別,靈魂亦有高低*",
                discord.Color.from_rgb(255, 127, 80),
                "請將幽幽子的身份組移到更高位置～"
            )
        
        return None

    async def send_dm_notification(self, target: discord.Member, guild_name: str, reason_text: str, banner_name: str):
        """發送私訊通知"""
        try:
            dm_embed = discord.Embed(
                title="🌸 冥界的邀請函",
                description=(
                    f"### 來自西行寺幽幽子的訊息\n\n"
                    f"> 在 **{guild_name}** 的白玉樓中,\n"
                    f"> 幽幽子決定將你的靈魂送往彼岸。\n\n"
                    f"**執行者:** {banner_name}\n"
                    f"**原因:** {reason_text}\n\n"
                    f"───────────────────\n\n"
                    f"*櫻花飄落之際,生死不過一念。*\n"
                    f"*願你在新的世界找到歸宿。*\n\n"
                    f"───────────────────\n\n"
                    f"如有疑問,請聯繫伺服器管理員。"
                ),
                color=discord.Color.from_rgb(255, 182, 193),
                timestamp=discord.utils.utcnow()
            )
            dm_embed.set_footer(
                text="西行寺幽幽子 · 冥界的亡靈公主",
                icon_url=self.bot.user.avatar.url if self.bot.user.avatar else None
            )
            dm_embed.set_thumbnail(url=target.display_avatar.url)
            
            await target.send(embed=dm_embed)
            return True
        except discord.Forbidden:
            logger.warning(f"無法發送私訊給 {target} (權限不足)")
            return False
        except Exception as e:
            logger.error(f"發送私訊失敗: {e}")
            return False

    @discord.slash_command(
        name="ban",
        description="🌸 幽幽子的冥界放逐：將靈魂送往彼岸"
    )
    async def ban(
        self,
        ctx: discord.ApplicationContext,
        member: discord.Member,
        reason: str = None,
        delete_messages: int = 0
    ):
        """
        冥界放逐指令
        
        Parameters:
        -----------
        member: 要放逐的成員
        reason: 放逐原因
        delete_messages: 刪除該成員多少天內的訊息
        """
        await ctx.defer(ephemeral=False)

        target = member

        # 檢查目標合法性
        invalid_embed = await self.check_target_valid(ctx, target)
        if invalid_embed:
            await ctx.followup.send(embed=invalid_embed, ephemeral=True)
            return

        # 權限檢查
        permission_embed = await self.check_permissions(ctx, target)
        if permission_embed:
            await ctx.followup.send(embed=permission_embed, ephemeral=True)
            return

        # 整理原因
        reason_text = reason or "未說明原因,隨櫻花飄落而去"
        full_reason = f"[幽幽子的冥界放逐] {reason_text}"

        # 發送私訊通知
        dm_sent = await self.send_dm_notification(
            target,
            ctx.guild.name,
            reason_text,
            ctx.user.name
        )

        # 執行放逐
        try:
            await target.ban(
                reason=full_reason,
                delete_message_days=delete_messages
            )
            
            # 成功 Embed
            success_embed = discord.Embed(
                title="🌸 冥界放逐完成",
                description=(
                    f"### 靈魂已送往彼岸\n\n"
                    f"**被放逐者:** {target.mention} (`{target.id}`)\n"
                    f"**執行者:** {ctx.user.mention}\n"
                    f"**原因:** {reason_text}\n"
                    f"**訊息清理:** {'已刪除 ' + str(delete_messages) + ' 天內的訊息' if delete_messages > 0 else '未刪除訊息'}\n"
                    f"**私訊通知:** {'✅ 已送達' if dm_sent else '❌ 未送達 (對方可能關閉私訊)'}\n\n"
                    f"───────────────────\n\n"
                    f"*{random.choice(self.banish_quotes)}*"
                ),
                color=discord.Color.from_rgb(147, 112, 219),
                timestamp=discord.utils.utcnow()
            )
            success_embed.set_thumbnail(url=target.display_avatar.url)
            success_embed.set_footer(
                text="西行寺幽幽子 · 操縱死亡的能力",
                icon_url=self.bot.user.avatar.url if self.bot.user.avatar else None
            )
            
            await ctx.followup.send(embed=success_embed)
            logger.info(
                f"{ctx.user} ({ctx.user.id}) 放逐了 {target} ({target.id}), "
                f"原因: {reason_text}"
            )
            
        except discord.Forbidden:
            error_embed = make_embed(
                "🌸 冥界放逐失敗",
                "幽幽子的力量無法觸及這個靈魂...\n\n"
                "**可能的原因:**\n"
                "• 幽幽子的身份組層級不夠高\n"
                "• 缺少必要的權限\n"
                "• 目標擁有管理員權限\n\n"
                f"*{random.choice(self.failure_quotes)}*",
                discord.Color.red(),
                "請檢查幽幽子的權限設定～"
            )
            await ctx.followup.send(embed=error_embed, ephemeral=True)
            logger.error(f"放逐失敗 (Forbidden): {target}")
            
        except Exception as e:
            error_embed = make_embed(
                "🌸 冥界波動異常",
                f"在放逐靈魂時,冥界出現了意外的波動...\n\n"
                f"**錯誤訊息:** `{str(e)}`\n\n"
                f"*{random.choice(self.failure_quotes)}*",
                discord.Color.red(),
                "請稍後再試,或聯繫管理員"
            )
            await ctx.followup.send(embed=error_embed, ephemeral=True)
            logger.exception(f"放逐指令發生錯誤: {e}")


def setup(bot: discord.Bot):
    """將幽幽子的冥界放逐功能裝進 bot 裡"""
    bot.add_cog(Ban(bot))
    logger.info("冥界放逐系統已載入")
