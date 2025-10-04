import os
import logging
import aiohttp
from discord import Webhook, Embed, Color
from discord.utils import utcnow

logger = logging.getLogger("SakuraBot.utils.alerts")

async def send_sakura_alert(message: str) -> None:
    """透過 Webhook 送出幽幽子的警訊，猶如櫻瓣飄向遠方"""
    # ✅ 每次呼叫時讀取環境變數（支援動態更新）
    webhook_url = os.getenv("WEBHOOK_URL")
    if not webhook_url:
        logger.error("未找到靈訊通道 WEBHOOK_URL，無法傳遞警訊")
        return

    try:
        async with aiohttp.ClientSession() as session:
            webhook = Webhook.from_url(webhook_url, session=session)
            embed = Embed(
                title="🌸 【冥界警報】幽幽子的低語 🌸",
                description=f"📢 {message}",
                color=Color.orange(),  # ✅ 修正：使用 discord.Color.orange()
                timestamp=utcnow()
            )
            embed.set_footer(text="⚠️ 來自冥界的櫻花警示")
            await webhook.send(embed=embed)
            logger.info("警訊已送出，櫻瓣隨風飄揚")
    except Exception as e:
        logger.error(f"靈訊傳送失敗：{e}")
