import discord
from discord.ext import commands
import asyncio
import random
import time
import logging

logger = logging.getLogger("SakuraBot.Ping")


class Ping(commands.Cog):
    """
    🌸 幽幽子的靈魂延遲測試 🌸
    測試與 Discord 冥界的通訊速度，如櫻花瓣飄落般輕盈
    """

    def __init__(self, bot):
        self.bot = bot
        logger.info("🌸 延遲測試指令已甦醒")

        self.testing_messages = [
            "靈魂的波動正在傳遞，稍等一下哦～",
            "嘻嘻，Discord 的回應有時會慢一點呢～",
            "櫻花飄落的速度，比這通訊還快吧？",
            "冥界的信號正在穿越時空～",
            "幽幽子正在感知靈魂的脈動～"
        ]

        self.iteration_messages = [
            "通訊完成，靈魂的回應真快呢～",
            "Discord 回應了，櫻花都忍不住飄落了～",
            "通訊完成，靈魂的波動真美妙～",
            "這次的靈魂共鳴很順暢呢～",
            "冥界的訊息已送達～"
        ]

        self.result_messages = {
            "excellent": [
                "通訊真順暢，靈魂的舞步都輕快起來了～",
                "這樣的延遲，連幽靈都會讚嘆哦～",
                "嘻嘻，Discord 與你的靈魂完美共鳴了～",
                "如櫻花瓣般輕盈的延遲，完美！"
            ],
            "good": [
                "通訊有點慢呢，靈魂的波動需要更多練習哦～",
                "這樣的延遲，櫻花都等得有點不耐煩了～",
                "Discord 的回應有點遲，可能是幽靈在偷懶吧？",
                "延遲稍高，但靈魂依然能感受到～"
            ],
            "poor": [
                "哎呀，通訊太慢了，靈魂都快睡著了～",
                "這樣的延遲，連櫻花都忍不住嘆息了～",
                "Discord 的回應太慢了，幽幽子都等得不耐煩了～",
                "冥界的連接似乎不太穩定呢～"
            ]
        }

    @discord.slash_command(
        name="ping",
        description="測試與 Discord 冥界的通訊延遲～幽幽子為你檢測靈魂波動"
    )
    async def ping(self, ctx: discord.ApplicationContext):
        await ctx.defer()

        embed = discord.Embed(
            title="🌸 幽幽子的靈魂延遲測試 🌸",
            description="幽幽子正在測試與冥界的通訊延遲…\n請稍候，櫻花瓣正在飄落中～",
            color=discord.Color.from_rgb(255, 182, 193),
            timestamp=discord.utils.utcnow()
        )
        embed.add_field(
            name="📡 WebSocket 延遲",
            value=f"`{self.bot.latency * 1000:.2f}` 毫秒" if self.bot.latency != float('inf') else "`計算中...`",
            inline=True
        )
        embed.set_footer(text=random.choice(self.testing_messages))

        message = await ctx.followup.send(embed=embed)

        iterations = 5
        delays = []

        for i in range(iterations):
            await asyncio.sleep(0.8)  # 間隔採樣
            
            # [Debug 修復 #1] 防止 bot.latency 為 float('inf') (Bot 剛啟動或斷線重連時)
            # 如果是 inf，則視為 0.0，避免顯示 "inf 毫秒" 或導致數學計算錯誤
            raw_ws_latency = self.bot.latency
            ws_latency = (raw_ws_latency * 1000) if raw_ws_latency != float('inf') else 0.0
            delays.append(ws_latency)

            delay_status = self._get_delay_status(ws_latency)

            update_embed = discord.Embed(
                title="🌸 幽幽子的靈魂延遲測試 🌸",
                description=f"正在採樣靈魂波動… **第 {i + 1}/{iterations} 次**",
                color=delay_status["color"],
                timestamp=discord.utils.utcnow()
            )
            update_embed.add_field(
                name="📊 本次採樣（WebSocket RTT）",
                value=f"{delay_status['emoji']} `{ws_latency:.2f}` 毫秒",
                inline=True
            )
            # [優化] 在 "次" 和隨機留言之間加個空格，排版更美觀
            update_embed.set_footer(
                text=f"第 {i + 1} 次 {random.choice(self.iteration_messages)}"
            )

            # [Debug 修復 #2] 增加 try-except 防止用戶在測試期間刪除訊息導致指令崩潰
            try:
                await message.edit(embed=update_embed)
            except discord.NotFound:
                logger.warning("🌸 Ping 測試訊息已被刪除，中止測試。")
                return
            except discord.HTTPException as e:
                logger.error(f"🌸 Ping 測試更新訊息失敗: {e}")

        avg_delay = sum(delays) / len(delays)
        min_delay = min(delays)
        max_delay = max(delays)

        logger.info(
            f"📊 延遲採樣完成 - 平均: {avg_delay:.2f} ms, "
            f"最小: {min_delay:.2f} ms, 最大: {max_delay:.2f} ms"
        )

        final_status = self._get_delay_status(avg_delay)

        result_embed = discord.Embed(
            title="🌸 幽幽子的靈魂延遲報告 🌸",
            description=(
                "採樣完成！以下是靈魂波動的詳細數據～\n"
                "-# 數值為 WebSocket Heartbeat RTT 的估算值"
            ),
            color=final_status["color"],
            timestamp=discord.utils.utcnow()
        )

        result_embed.add_field(
            name="📡 WebSocket 延遲",
            value=f"`{self.bot.latency * 1000:.2f}` 毫秒" if self.bot.latency != float('inf') else "`計算中...`",
            inline=True
        )
        result_embed.add_field(
            name="📊 平均延遲",
            value=f"{final_status['emoji']} `{avg_delay:.2f}` 毫秒",
            inline=True
        )
        result_embed.add_field(
            name="📈 延遲範圍",
            value=f"`{min_delay:.2f}` ~ `{max_delay:.2f}` 毫秒",
            inline=True
        )

        details = "\n".join([
            f"{self._get_delay_status(d)['emoji']} 第 {i+1} 次: `{d:.2f}` 毫秒"
            for i, d in enumerate(delays)
        ])
        result_embed.add_field(name="📋 詳細採樣記錄", value=details, inline=False)
        result_embed.add_field(
            name="⭐ 性能評級",
            value=self._get_performance_rating(avg_delay),
            inline=False
        )
        result_embed.set_footer(
            text=random.choice(self.result_messages[final_status["quality"]])
        )

        # [Debug 修復 #2] 最終報告也加上異常保護
        try:
            await message.edit(embed=result_embed)
        except discord.NotFound:
            logger.warning("🌸 Ping 最終報告發送前，訊息已被刪除。")
        except discord.HTTPException as e:
            logger.error(f"🌸 Ping 最終報告發送失敗: {e}")

    @staticmethod
    def _get_delay_status(delay_ms: float) -> dict:
        if delay_ms <= 100:
            return {"color": discord.Color.green(),  "emoji": "🟢", "quality": "excellent", "rating": "極速"}
        elif delay_ms <= 200:
            return {"color": discord.Color.teal(),   "emoji": "🔵", "quality": "excellent", "rating": "優秀"}
        elif delay_ms <= 500:
            return {"color": discord.Color.blue(),   "emoji": "🟡", "quality": "excellent", "rating": "良好"}
        elif delay_ms <= 1000:
            return {"color": discord.Color.gold(),   "emoji": "🟠", "quality": "good",      "rating": "普通"}
        else:
            return {"color": discord.Color.red(),    "emoji": "🔴", "quality": "poor",      "rating": "緩慢"}

    @staticmethod
    def _get_performance_rating(avg_delay: float) -> str:
        if avg_delay <= 100:
            return "█████████░ **SSS 級**\n*靈魂的極速共鳴！*"
        elif avg_delay <= 200:
            return "████████░░ **SS 級**\n*靈魂波動極為順暢*"
        elif avg_delay <= 500:
            return "██████░░░░ **S 級**\n*靈魂連接良好*"
        elif avg_delay <= 1000:
            return "████░░░░░░ **A 級**\n*靈魂連接尚可*"
        else:
            return "██░░░░░░░░ **B 級**\n*靈魂連接不穩定*"


def setup(bot):
    bot.add_cog(Ping(bot))
    logger.info("✨ 延遲測試 Cog 已載入完成")
