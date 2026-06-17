import discord
from discord.ext import commands
import logging
import os
import asyncio
from datetime import datetime, timezone
import aiohttp

logger = logging.getLogger("SakuraBot.Shutdown")

AUTHOR_ID = int(os.getenv("AUTHOR_ID", 0))
OFFLINE_WEBHOOK_URL = os.getenv("OFFLINE_WEBHOOK_URL")


async def send_webhook_message(bot, content: str, color: discord.Color):
    """向 Webhook 發送關機通知"""
    if not OFFLINE_WEBHOOK_URL:
        logger.error("❌ OFFLINE_WEBHOOK_URL 未配置")
        return

    try:
        # [Debug 修復 #1] 使用 display_avatar 簡化邏輯，確保 100% 有頭貼
        icon_url = bot.user.display_avatar.url

        embed = discord.Embed(
            title="🌸 幽幽子的飄渺呢喃",
            description=content,
            color=color,
            timestamp=datetime.now(timezone.utc)
        )
        embed.set_footer(text="來自冥界的微風與魂魄之語～", icon_url=icon_url)

        # [Debug 修復 #2] 關機前直接使用臨時 session 即可，無需檢查 bot.session
        async with aiohttp.ClientSession() as temp_session:
            webhook = discord.Webhook.from_url(OFFLINE_WEBHOOK_URL, session=temp_session)
            await webhook.send(embed=embed)
            logger.info("✅ 關機 Webhook 訊息已發送")

    except Exception as e:
        logger.error(f"❌ 發送 Webhook 失敗: {e}")


class ShutdownCog(commands.Cog):
    """
    🌸 幽幽子的安眠指令 🌸
    讓幽幽子安靜地沉眠，靈魂歸於冥界
    """

    def __init__(self, bot):
        self.bot = bot
        logger.info("🌸 關機指令已甦醒")

    @discord.slash_command(
        name="shutdown",
        description="讓幽幽子安靜地沉眠～只有特別的人才能使用"
    )
    async def shutdown(self, ctx: discord.ApplicationContext):
        if ctx.user.id != AUTHOR_ID:
            await ctx.respond(
                embed=discord.Embed(
                    title="🌸 權限不足",
                    description=(
                        f"嘻嘻，只有特別的人才能讓幽幽子安靜下來～\n"
                        f"你還不是那個人哦，{ctx.user.mention}！\n\n"
                        "櫻花樹下的守護者，不會輕易離去呢～"
                    ),
                    color=discord.Color.orange(),
                    timestamp=discord.utils.utcnow()
                ).set_footer(text="幽幽子會繼續守護大家"),
                ephemeral=True
            )
            logger.warning(f"⚠️ {ctx.user.name} (ID:{ctx.user.id}) 嘗試使用 shutdown 但權限不足")
            return

        try:
            # [Debug 修復 #1] 使用 display_avatar
            icon_url = self.bot.user.display_avatar.url

            shutdown_embed = discord.Embed(
                title="🌸 幽幽子即將沉眠 🌸",
                description=(
                    "夜櫻下，幽幽子輕輕閉上雙眼…\n"
                    "靈魂歸於冥界，在夢中繼續守護著大家。\n\n"
                    "感謝所有人的陪伴，\n"
                    "櫻花飄落時，便是幽幽子安眠之刻。\n\n"
                    "**晚安，夢裡見～** 💤"
                ),
                color=discord.Color.from_rgb(205, 133, 232),
                timestamp=datetime.now(timezone.utc)
            )
            shutdown_embed.set_thumbnail(url=icon_url)
            shutdown_embed.set_footer(
                text=f"由 {ctx.user.name} 啟動關機程序",
                icon_url=ctx.user.display_avatar.url  # [Debug 修復 #1]
            )

            await ctx.respond(embed=shutdown_embed, ephemeral=False)
            logger.info(f"🌸 {ctx.user.name} 啟動了關機程序")

            # 1. Webhook 通知
            await send_webhook_message(
                self.bot,
                (
                    "🔴 **幽幽子飄然離去，魂魄歸於冥界…**\n\n"
                    "「夜櫻下的安眠，是幽幽子的幸福時刻～」\n\n"
                    f"關機執行者: {ctx.user.name} (`{ctx.user.id}`)\n"
                    f"關機時間: <t:{int(datetime.now(timezone.utc).timestamp())}:F>"
                ),
                discord.Color.from_rgb(205, 133, 232)
            )

            # 2. 保存數據
            data_manager = getattr(self.bot, "data_manager", None)
            if data_manager:
                try:
                    await data_manager.save_all_async()
                    logger.info("💾 所有數據已保存")
                except Exception as e:
                    logger.error(f"❌ 數據保存失敗: {e}")

            await asyncio.sleep(2)

            # 3. 優雅關閉 Bot (這會自動斷開 Gateway 連線)
            logger.info("🌸 幽幽子即將沉眠，Bot 正在關閉...")
            await self.bot.close()

        except Exception as e:
            logger.error(f"❌ 關機指令執行失敗: {e}", exc_info=True)
            
            error_embed = discord.Embed(
                title="🌸 關機失敗",
                description=(
                    "哎呀，幽幽子好像被什麼纏住了，無法沉眠…\n\n"
                    f"**錯誤訊息**: `{str(e)}`\n\n"
                    "請檢查日誌或聯絡開發者！"
                ),
                color=discord.Color.red(),
                timestamp=discord.utils.utcnow()
            )
            error_embed.set_footer(text="幽幽子依然在守護著大家")
            
            # [Debug 修復 #3] 防止 InteractionResponded 異常
            try:
                if ctx.response.is_done():
                    await ctx.followup.send(embed=error_embed, ephemeral=True)
                else:
                    await ctx.respond(embed=error_embed, ephemeral=True)
            except Exception:
                pass


def setup(bot):
    bot.add_cog(ShutdownCog(bot))
    logger.info("✨ 關機 Cog 已載入完成")
