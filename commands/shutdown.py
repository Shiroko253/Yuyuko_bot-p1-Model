import discord
from discord.ext import commands
import logging
import os
import asyncio
from datetime import datetime, timezone
import aiohttp

logger = logging.getLogger("SakuraBot.Shutdown")

AUTHOR_ID = int(os.getenv("AUTHOR_ID", 0))


async def send_webhook_message(bot, content: str, color: discord.Color):
    """向 Webhook 發送訊息"""
    webhook_url = os.getenv("WEBHOOK_URL")
    
    if not webhook_url:
        logger.error("❌ Webhook URL 未配置")
        raise ValueError("Webhook URL 未配置")
    
    try:
        icon_url = bot.user.avatar.url if bot.user.avatar else bot.user.default_avatar.url
        
        embed = discord.Embed(
            title="🌸 幽幽子的飄渺呢喃",
            description=content,
            color=color,
            timestamp=datetime.now(timezone.utc)
        )
        embed.set_footer(
            text="來自冥界的微風與魂魄之語～",
            icon_url=icon_url
        )
        
        # 使用 aiohttp 正確發送 Webhook
        async with aiohttp.ClientSession() as session:
            webhook = discord.Webhook.from_url(webhook_url, session=session)
            await webhook.send(embed=embed)
            logger.info("✅ Webhook 訊息已發送")
            
    except Exception as e:
        logger.error(f"❌ 發送 Webhook 失敗: {e}")
        raise


class ShutdownCog(commands.Cog):
    """
    🌸 幽幽子的安眠指令 🌸
    讓幽幽子安靜地沉眠,靈魂歸於冥界
    """
    
    def __init__(self, bot):
        self.bot = bot
        logger.info("🌸 關機指令已甦醒")

    @discord.slash_command(
        name="shutdown",
        description="讓幽幽子安靜地沉眠～只有特別的人才能使用"
    )
    async def shutdown(self, ctx: discord.ApplicationContext):
        """幽幽子的安眠時刻,靈魂歸於寂靜"""
        
        # === 權限檢查 ===
        if ctx.user.id != AUTHOR_ID:
            await ctx.respond(
                embed=discord.Embed(
                    title="🌸 權限不足",
                    description=(
                        "嘻嘻，只有特別的人才能讓幽幽子安靜下來～\n"
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
            # === 獲取 Bot 頭像 ===
            icon_url = self.bot.user.avatar.url if self.bot.user.avatar else self.bot.user.default_avatar.url
            
            # === 回應關機確認 ===
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
                icon_url=ctx.user.avatar.url if ctx.user.avatar else None
            )
            
            await ctx.respond(embed=shutdown_embed, ephemeral=False)
            logger.info(f"🌸 {ctx.user.name} 啟動了關機程序")
            
            # === 發送 Webhook 通知 ===
            try:
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
            except Exception as e:
                logger.warning(f"⚠️ Webhook 發送失敗，但繼續關機流程: {e}")
            
            # === 保存所有數據 ===
            data_manager = getattr(self.bot, "data_manager", None)
            if data_manager:
                try:
                    await data_manager.save_all_async()
                    logger.info("💾 所有數據已保存")
                except Exception as e:
                    logger.error(f"❌ 數據保存失敗: {e}")
            
            # === 等待並關閉 Bot ===
            await asyncio.sleep(3)
            
            logger.info("🌸 幽幽子即將沉眠，Bot 正在關閉...")
            await self.bot.close()
            logger.info("✅ Bot 已成功關閉")
            
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
            
            try:
                await ctx.respond(embed=error_embed, ephemeral=True)
            except:
                # 如果已經 respond 過，使用 send
                await ctx.send(embed=error_embed)


def setup(bot):
    bot.add_cog(ShutdownCog(bot))
    logger.info("✨ 關機 Cog 已載入完成")
