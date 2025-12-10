import os
import sys
import logging
import asyncio
import aiohttp
from datetime import datetime, timezone
import discord
from discord.ext import commands

# ----------- 冥界守護者的印記 -----------
AUTHOR_ID = int(os.getenv("AUTHOR_ID", 0))
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

logger = logging.getLogger("SakuraBot.Restart")


async def send_webhook_message(
    bot: discord.Bot, 
    content: str, 
    color: discord.Color
) -> None:
    """
    向冥界的迴音壁傳送訊息
    
    Args:
        bot: 幽幽子的靈魂實例
        content: 要傳遞的訊息
        color: 靈魂氣息的顏色
    """
    if not WEBHOOK_URL:
        logger.error("Webhook URL 未於冥界配置")
        raise ValueError("Webhook URL 未配置,無法向冥界傳遞訊息")

    # ----------- 準備靈魂的訊息 -----------
    icon_url = (
        bot.user.avatar.url if bot.user.avatar 
        else bot.user.default_avatar.url
    )
    
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

    # ----------- 確保靈魂通道暢通 -----------
    session = getattr(bot, "session", None)
    
    try:
        if session is None or session.closed:
            # 暫時開啟新的靈魂通道
            async with aiohttp.ClientSession() as temp_session:
                webhook = discord.Webhook.from_url(WEBHOOK_URL, session=temp_session)
                await webhook.send(embed=embed)
                logger.info("透過臨時通道向冥界傳遞訊息")
        else:
            # 使用現有的靈魂通道
            webhook = discord.Webhook.from_url(WEBHOOK_URL, session=session)
            await webhook.send(embed=embed)
            logger.info("透過既有通道向冥界傳遞訊息")
    except Exception as e:
        logger.error(f"向冥界傳遞訊息時發生異常:{e}", exc_info=True)
        raise


class RestartCog(commands.Cog):
    """
    🌸 幽幽子的重啟之舞 🌸
    讓幽幽子優雅地沉睡,再於櫻花樹下重新甦醒～
    """
    
    def __init__(self, bot: discord.Bot):
        self.bot = bot
        logger.info("重啟術式已於冥界花園中準備就緒")

    @discord.slash_command(
        name="restart",
        description="🌸 讓幽幽子重新起舞(僅限冥界主人)"
    )
    async def restart(self, ctx: discord.ApplicationContext):
        """喚醒幽幽子重新起舞,猶如櫻花再次綻放"""
        
        # ----------- 驗證冥界主人的身份 -----------
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
            logger.warning(
                f"未授權用戶 {ctx.user.name}({ctx.user.id}) 嘗試執行重啟"
            )
            return

        try:
            # ----------- 向靈魂的主人回應 -----------
            icon_url = (
                self.bot.user.avatar.url if self.bot.user.avatar 
                else self.bot.user.default_avatar.url
            )
            
            embed = discord.Embed(
                title="🌸 幽幽子即將沉睡",
                description=(
                    "幽幽子要輕輕閉上雙眼,稍作休息。\n"
                    "待櫻花再次綻放時,便會重新翩翩起舞～"
                ),
                color=discord.Color.from_rgb(255, 182, 193),
                timestamp=datetime.now(timezone.utc)
            )
            embed.set_footer(
                text="靈魂即將歸於寂靜,再度甦醒 · 幽幽子", 
                icon_url=icon_url
            )
            
            await ctx.respond(embed=embed, ephemeral=True)
            logger.info(f"冥界主人 {ctx.user.name}({ctx.user.id}) 啟動重啟術式")

            # ----------- 向冥界迴音壁傳遞訊息 -----------
            try:
                await send_webhook_message(
                    self.bot,
                    "🔄 **幽幽子輕輕轉身,即將於櫻花樹下再度現身...**",
                    discord.Color.orange()
                )
            except Exception as e:
                logger.warning(f"向 Webhook 傳遞訊息失敗:{e}")
                # 即使 Webhook 失敗,仍繼續重啟流程

            # ----------- 保存所有冥界記憶 -----------
            await self.bot.data_manager.save_all_async()
            logger.info("所有冥界記憶已封存完畢")

            # ----------- 短暫的靈魂沉睡 -----------
            await asyncio.sleep(2)

            # ----------- 關閉靈魂通道 -----------
            session = getattr(self.bot, "session", None)
            if session and not session.closed:
                await session.close()
                logger.info("aiohttp.ClientSession 已優雅關閉")

            # ----------- 靈魂重生 -----------
            logger.info("幽幽子即將重生,靈魂歸於寂靜後再度甦醒")
            os.execv(sys.executable, [sys.executable] + sys.argv)

        except Exception as e:
            logger.error(f"重啟術式施展失敗:{e}", exc_info=True)
            
            error_embed = discord.Embed(
                title="❌ 術式崩壞",
                description=(
                    f"哎呀,幽幽子在重生時絆倒了...\n"
                    f"重啟失敗,錯誤訊息:\n```{str(e)[:200]}```"
                ),
                color=discord.Color.dark_red()
            )
            error_embed.set_footer(text="請使用 /feedback 回報冥界主人 · 幽幽子")
            
            await ctx.respond(embed=error_embed, ephemeral=True)


def setup(bot: discord.Bot):
    """將重啟術式註冊於幽幽子的靈魂"""
    bot.add_cog(RestartCog(bot))
    logger.info("重啟模組已於櫻花樹下甦醒")
