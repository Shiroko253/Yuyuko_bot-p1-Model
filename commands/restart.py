import os
import sys
import logging
import asyncio
import aiohttp
from datetime import datetime, timezone
import discord
from discord.ext import commands

AUTHOR_ID = int(os.getenv("AUTHOR_ID", 0))
RESTART_WEBHOOK_URL = os.getenv("RESTART_WEBHOOK_URL")

logger = logging.getLogger("SakuraBot.Restart")


async def send_webhook_message(bot: discord.Bot, content: str, color: discord.Color) -> None:
    """向冥界傳遞重啟訊息"""
    if not RESTART_WEBHOOK_URL:
        logger.error("RESTART_WEBHOOK_URL 未於冥界配置")
        return

    # [Debug 修復 #2] 使用 display_avatar 簡化邏輯，確保 100% 有頭貼
    icon_url = bot.user.display_avatar.url

    embed = discord.Embed(
        title="🌸 幽幽子的飄渺呢喃",
        description=content,
        color=color,
        timestamp=datetime.now(timezone.utc)
    )
    embed.set_footer(text="來自冥界的微風與魂魄之語～", icon_url=icon_url)

    try:
        # [Debug 修復 #2] 重啟前直接使用臨時 session 即可，無需檢查 bot.session
        async with aiohttp.ClientSession() as temp_session:
            webhook = discord.Webhook.from_url(RESTART_WEBHOOK_URL, session=temp_session)
            await webhook.send(embed=embed)
            logger.info("透過臨時通道向冥界傳遞重啟訊息")
    except Exception as e:
        logger.error(f"向冥界傳遞訊息時發生異常: {e}", exc_info=True)


class RestartCog(commands.Cog):
    """
    🌸 幽幽子的重啟之舞 🌸
    讓幽幽子優雅地沉睡，再於櫻花樹下重新甦醒～
    """

    def __init__(self, bot: discord.Bot):
        self.bot = bot
        logger.info("重啟術式已於冥界花園中準備就緒")

    @discord.slash_command(
        name="restart",
        description="🌸 讓幽幽子重新起舞（僅限冥界主人）"
    )
    async def restart(self, ctx: discord.ApplicationContext):
        if ctx.user.id != AUTHOR_ID:
            embed = discord.Embed(
                title="❌ 冥界之力受阻",
                description=(
                    "只有靈魂的主人才能喚醒幽幽子重生。\n"
                    "你還不具備這份力量呢～"
                ),
                color=discord.Color.dark_purple()
            )
            await ctx.respond(embed=embed, ephemeral=True)
            logger.warning(f"未授權用戶 {ctx.user.name}({ctx.user.id}) 嘗試執行重啟")
            return

        try:
            # [Debug 修復 #2] 使用 display_avatar
            icon_url = self.bot.user.display_avatar.url

            embed = discord.Embed(
                title="🌸 幽幽子即將沉睡",
                description=(
                    "幽幽子要輕輕閉上雙眼，稍作休息。\n"
                    "待櫻花再次綻放時，便會重新翩翩起舞～"
                ),
                color=discord.Color.from_rgb(255, 182, 193),
                timestamp=datetime.now(timezone.utc)
            )
            embed.set_footer(text="靈魂即將歸於寂靜，再度甦醒 · 幽幽子", icon_url=icon_url)

            await ctx.respond(embed=embed, ephemeral=True)
            logger.info(f"冥界主人 {ctx.user.name}({ctx.user.id}) 啟動重啟術式")

            # 1. 發送 Webhook 通知
            await send_webhook_message(
                self.bot,
                "🔄 **幽幽子輕輕轉身，即將於櫻花樹下再度現身...**",
                discord.Color.orange()
            )

            # 2. 保存所有數據
            await self.bot.data_manager.save_all_async()
            logger.info("所有冥界記憶已封存完畢")

            await asyncio.sleep(2)

            # 3. [Debug 修復 #1] 關鍵！優雅關閉 Bot，斷開 Gateway 連線
            # 如果直接 os.execv，Gateway 會被強制切斷，導致 Discord 顯示 Bot 異常離線
            logger.info("正在優雅關閉 Gateway 連線...")
            await self.bot.close()
            
            logger.info("幽幽子即將重生，靈魂歸於寂靜後再度甦醒")
            
            # 4. 執行進程替換 (重啟)
            # 注意：os.execv 在 Linux/Docker 下表現完美。
            # 如果您是在 Windows 本地運行，os.execv 可能會報錯。
            # Windows 用戶建議改用 subprocess.Popen 啟動新進程，然後 os._exit(0)。
            os.execv(sys.executable, [sys.executable] + sys.argv)

        except Exception as e:
            logger.error(f"重啟術式施展失敗: {e}", exc_info=True)

            error_embed = discord.Embed(
                title="❌ 術式崩壞",
                description=(
                    f"哎呀，幽幽子在重生時絆倒了...\n"
                    f"重啟失敗，錯誤訊息:\n```{str(e)[:200]}```"
                ),
                color=discord.Color.dark_red()
            )
            error_embed.set_footer(text="請使用 /feedback 回報冥界主人 · 幽幽子")

            # [Debug 修復 #3] 防止 InteractionResponded 異常
            try:
                if ctx.response.is_done():
                    await ctx.followup.send(embed=error_embed, ephemeral=True)
                else:
                    await ctx.respond(embed=error_embed, ephemeral=True)
            except Exception:
                pass


def setup(bot: discord.Bot):
    bot.add_cog(RestartCog(bot))
    logger.info("重啟模組已於櫻花樹下甦醒")
