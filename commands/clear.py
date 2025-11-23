import discord
from discord.ext import commands
from discord import ApplicationContext, Option
from datetime import datetime, timedelta, timezone
import logging

logger = logging.getLogger("SakuraBot.commands.clear")


class Clear(commands.Cog):
    """
    ✿ 冥界清掃隊 ✿
    幽幽子命令妖夢化身為清掃小隊，把靈魂們的雜訊優雅地清理掉～
    """
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @discord.slash_command(
        name="clear",
        description="讓妖夢清掃冥界的雜訊～"
    )
    @commands.has_permissions(manage_messages=True)
    async def clear(
        self,
        ctx: ApplicationContext,
        amount: int = Option(
            int,
            description="要清除的消息數量（1-100）",
            min_value=1,
            max_value=100,
            required=True
        )
    ) -> None:
        """清除指定數量的消息"""
        await ctx.defer(ephemeral=True)

        try:
            # Discord API 限制：只能刪除 14 天內的消息
            cutoff_date = datetime.now(tz=timezone.utc) - timedelta(days=14)

            # 執行清除
            deleted = await ctx.channel.purge(limit=amount, after=cutoff_date)
            deleted_count = len(deleted)

            if deleted_count > 0:
                embed = discord.Embed(
                    title="🌸 妖夢已完成清掃～",
                    description=(
                        f"已優雅地清除 **{deleted_count}** 條靈魂雜訊。\n"
                        f"幽幽子在櫻花下微笑讚賞妖夢～"
                    ),
                    color=discord.Color.from_rgb(0, 255, 204)  # 青綠色
                ).set_footer(text="冥界清掃完畢，櫻花更美了～")
                
                logger.info(
                    f"用戶 {ctx.user.id} 在頻道 {ctx.channel.id} "
                    f"清除了 {deleted_count} 條消息"
                )
            else:
                embed = discord.Embed(
                    title="🌸 沒有靈魂可清掃～",
                    description=(
                        "所有消息都超過了 14 天限制，櫻花已將舊靈魂帶走～\n"
                        "Discord 不允許刪除超過 14 天的消息哦。"
                    ),
                    color=discord.Color.from_rgb(255, 255, 153)  # 淺黃色
                ).set_footer(text="冥界清掃受限於時空法則")
                
                logger.info(
                    f"用戶 {ctx.user.id} 在頻道 {ctx.channel.id} "
                    f"嘗試清除消息但沒有可刪除的消息"
                )

            await ctx.followup.send(embed=embed)

        except discord.Forbidden:
            embed = discord.Embed(
                title="⛔ 妖夢被困住了！",
                description=(
                    "幽幽子發現權限不足，妖夢無法清掃消息。\n"
                    "請聯繫管理員幫幽幽子和妖夢加點力量吧～"
                ),
                color=discord.Color.from_rgb(255, 102, 153)  # 粉紅色
            ).set_footer(text="請給機器人『管理消息』權限")
            
            await ctx.followup.send(embed=embed)
            logger.warning(
                f"用戶 {ctx.user.id} 嘗試清除消息但 bot 權限不足 "
                f"(頻道 {ctx.channel.id})"
            )

        except discord.HTTPException as e:
            embed = discord.Embed(
                title="❌ 櫻花舞亂了！",
                description=(
                    f"Discord API 發生錯誤：{getattr(e, 'text', str(e))}\n"
                    f"幽幽子輕輕地安慰妖夢，下次再試～"
                ),
                color=discord.Color.from_rgb(255, 51, 102)  # 深粉色
            ).set_footer(text="櫻花飄落有時，請稍後再試")
            
            await ctx.followup.send(embed=embed)
            logger.error(
                f"清除消息時發生 HTTPException: {e} "
                f"(用戶 {ctx.user.id}, 頻道 {ctx.channel.id})"
            )

        except Exception as e:
            embed = discord.Embed(
                title="❌ 冥界迷霧！",
                description=(
                    f"發生未知錯誤：{str(e)}\n"
                    f"幽幽子正揮舞櫻花幫你驅散迷霧～"
                ),
                color=discord.Color.from_rgb(153, 0, 51)  # 暗紅色
            ).set_footer(text="如有問題請聯絡幽幽子或管理員")
            
            await ctx.followup.send(embed=embed)
            logger.exception(
                f"清除消息時發生未知錯誤 (用戶 {ctx.user.id}, 頻道 {ctx.channel.id}): {e}"
            )

    @clear.error
    async def clear_error(
        self,
        ctx: ApplicationContext,
        error: commands.CommandError
    ) -> None:
        """清除指令的錯誤處理"""
        if isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(
                title="⛔ 妖夢不聽你的話！",
                description=(
                    "你沒有 **管理消息** 權限，妖夢只聽有權限者的指令哦～\n"
                    "請向伺服器管理員申請權限，或請有權限的人協助清掃。"
                ),
                color=discord.Color.from_rgb(255, 51, 102)  # 深粉色
            ).set_footer(text="冥界清掃需要主人的授權")
            
            try:
                await ctx.respond(embed=embed, ephemeral=True)
            except discord.InteractionResponded:
                await ctx.followup.send(embed=embed, ephemeral=True)
            
            logger.warning(
                f"用戶 {ctx.user.id} 嘗試使用 clear 但缺少權限"
            )

        elif isinstance(error, commands.BotMissingPermissions):
            embed = discord.Embed(
                title="⛔ 妖夢的力量不足！",
                description=(
                    "幽幽子發現機器人缺少必要權限：\n"
                    f"**{', '.join(error.missing_permissions)}**\n\n"
                    "請聯繫伺服器管理員為幽幽子添加權限～"
                ),
                color=discord.Color.from_rgb(255, 102, 153)  # 粉紅色
            ).set_footer(text="妖夢需要『管理消息』權限才能清掃")
            
            try:
                await ctx.respond(embed=embed, ephemeral=True)
            except discord.InteractionResponded:
                await ctx.followup.send(embed=embed, ephemeral=True)
            
            logger.warning(
                f"Bot 缺少權限執行 clear: {error.missing_permissions}"
            )

        else:
            embed = discord.Embed(
                title="❌ 冥界櫻花迷路了！",
                description=(
                    f"發生未知錯誤：{str(error)}\n"
                    f"幽幽子和妖夢一起努力排查～"
                ),
                color=discord.Color.from_rgb(153, 0, 51)  # 暗紅色
            ).set_footer(text="如有問題請回報給幽幽子")
            
            try:
                await ctx.respond(embed=embed, ephemeral=True)
            except discord.InteractionResponded:
                await ctx.followup.send(embed=embed, ephemeral=True)
            
            logger.exception(f"Clear 指令發生未知錯誤: {error}")


def setup(bot: discord.Bot) -> None:
    """
    ✿ 幽幽子優雅地將清掃指令裝進 bot ✿
    """
    bot.add_cog(Clear(bot))
    logger.info("🌸 Clear 清掃系統已載入")
