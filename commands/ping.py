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
    測試與 Discord 冥界的通訊速度,如櫻花瓣飄落般輕盈
    """
    
    def __init__(self, bot):
        self.bot = bot
        logger.info("🌸 延遲測試指令已甦醒")
        
        # 幽幽子的詩意回應語錄
        self.testing_messages = [
            "靈魂的波動正在傳遞,稍等一下哦～",
            "嘻嘻,Discord 的回應有時會慢一點呢～",
            "櫻花飄落的速度,比這通訊還快吧？",
            "冥界的信號正在穿越時空～",
            "幽幽子正在感知靈魂的脈動～"
        ]
        
        self.iteration_messages = [
            "通訊完成,靈魂的回應真快呢～",
            "Discord 回應了,櫻花都忍不住飄落了～",
            "通訊完成,靈魂的波動真美妙～",
            "這次的靈魂共鳴很順暢呢～",
            "冥界的訊息已送達～"
        ]
        
        self.result_messages = {
            "excellent": [
                "通訊真順暢,靈魂的舞步都輕快起來了～",
                "這樣的延遲,連幽靈都會讚嘆哦～",
                "嘻嘻,Discord 與你的靈魂完美共鳴了～",
                "如櫻花瓣般輕盈的延遲,完美！"
            ],
            "good": [
                "通訊有點慢呢,靈魂的波動需要更多練習哦～",
                "這樣的延遲,櫻花都等得有點不耐煩了～",
                "Discord 的回應有點遲,可能是幽靈在偷懶吧？",
                "延遲稍高,但靈魂依然能感受到～"
            ],
            "poor": [
                "哎呀,通訊太慢了,靈魂都快睡著了～",
                "這樣的延遲,連櫻花都忍不住嘆息了～",
                "Discord 的回應太慢了,幽幽子都等得不耐煩了～",
                "冥界的連接似乎不太穩定呢～"
            ]
        }

    @discord.slash_command(
        name="ping",
        description="測試與 Discord 冥界的通訊延遲～幽幽子為你檢測靈魂波動"
    )
    async def ping(self, ctx: discord.ApplicationContext):
        """幽幽子測試與 Discord 的靈魂連接速度"""
        await ctx.defer()
        
        # === 初始測試 Embed ===
        embed = discord.Embed(
            title="🌸 幽幽子的靈魂延遲測試 🌸",
            description="幽幽子正在測試與冥界的通訊延遲…\n請稍候,櫻花瓣正在飄落中～",
            color=discord.Color.from_rgb(255, 182, 193),
            timestamp=discord.utils.utcnow()
        )
        embed.add_field(
            name="📡 WebSocket 延遲",
            value=f"`{self.bot.latency * 1000:.2f}` 毫秒",
            inline=True
        )
        embed.set_footer(text=random.choice(self.testing_messages))
        
        message = await ctx.followup.send(embed=embed)
        
        # === 執行多次測試 ===
        iterations = 5
        delays = []
        
        for i in range(iterations):
            # 測量 API 延遲
            start_time = time.perf_counter()
            await asyncio.sleep(0)  # 最小延遲
            api_delay = (time.perf_counter() - start_time) * 1000
            
            # 結合 WebSocket 延遲
            total_delay = api_delay + (self.bot.latency * 1000)
            delays.append(total_delay)
            
            logger.debug(f"第 {i+1} 次測試: {total_delay:.2f} ms")
            
            # === 動態更新 Embed ===
            delay_status = self._get_delay_status(total_delay)
            
            update_embed = discord.Embed(
                title="🌸 幽幽子的靈魂延遲測試 🌸",
                description=f"正在測試靈魂波動… **第 {i + 1}/{iterations} 次**",
                color=delay_status["color"],
                timestamp=discord.utils.utcnow()
            )
            
            update_embed.add_field(
                name="📊 本次測試結果",
                value=f"{delay_status['emoji']} `{total_delay:.2f}` 毫秒",
                inline=True
            )
            update_embed.add_field(
                name="📡 WebSocket 延遲",
                value=f"`{self.bot.latency * 1000:.2f}` 毫秒",
                inline=True
            )
            
            update_embed.set_footer(
                text=f"第 {i + 1} 次{random.choice(self.iteration_messages)}"
            )
            
            await message.edit(embed=update_embed)
            await asyncio.sleep(0.8)  # 稍微延遲讓用戶看清楚
        
        # === 計算統計數據 ===
        avg_delay = sum(delays) / len(delays)
        min_delay = min(delays)
        max_delay = max(delays)
        
        logger.info(f"📊 延遲測試完成 - 平均: {avg_delay:.2f} ms, 最小: {min_delay:.2f} ms, 最大: {max_delay:.2f} ms")
        
        # === 最終結果 Embed ===
        final_status = self._get_delay_status(avg_delay)
        
        result_embed = discord.Embed(
            title="🌸 幽幽子的靈魂延遲報告 🌸",
            description="測試完成！以下是靈魂波動的詳細數據～",
            color=final_status["color"],
            timestamp=discord.utils.utcnow()
        )
        
        # 統計數據
        result_embed.add_field(
            name="📡 WebSocket 延遲",
            value=f"`{self.bot.latency * 1000:.2f}` 毫秒",
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
        
        # 詳細測試結果
        details = "\n".join([
            f"{self._get_delay_status(d)['emoji']} 第 {i+1} 次: `{d:.2f}` 毫秒"
            for i, d in enumerate(delays)
        ])
        result_embed.add_field(
            name="📋 詳細測試記錄",
            value=details,
            inline=False
        )
        
        # 性能評級
        result_embed.add_field(
            name="⭐ 性能評級",
            value=self._get_performance_rating(avg_delay),
            inline=False
        )
        
        result_embed.set_footer(
            text=random.choice(self.result_messages[final_status["quality"]])
        )
        
        await message.edit(embed=result_embed)

    @staticmethod
    def _get_delay_status(delay_ms: float) -> dict:
        """根據延遲返回狀態資訊"""
        if delay_ms <= 100:
            return {
                "color": discord.Color.green(),
                "emoji": "🟢",
                "quality": "excellent",
                "rating": "極速"
            }
        elif delay_ms <= 200:
            return {
                "color": discord.Color.teal(),
                "emoji": "🔵",
                "quality": "excellent",
                "rating": "優秀"
            }
        elif delay_ms <= 500:
            return {
                "color": discord.Color.blue(),
                "emoji": "🟡",
                "quality": "excellent",
                "rating": "良好"
            }
        elif delay_ms <= 1000:
            return {
                "color": discord.Color.gold(),
                "emoji": "🟠",
                "quality": "good",
                "rating": "普通"
            }
        else:
            return {
                "color": discord.Color.red(),
                "emoji": "🔴",
                "quality": "poor",
                "rating": "緩慢"
            }

    @staticmethod
    def _get_performance_rating(avg_delay: float) -> str:
        """生成性能評級圖表"""
        if avg_delay <= 100:
            bars = "█████████░"
            rating = "SSS 級"
            desc = "靈魂的極速共鳴！"
        elif avg_delay <= 200:
            bars = "████████░░"
            rating = "SS 級"
            desc = "靈魂波動極為順暢"
        elif avg_delay <= 500:
            bars = "██████░░░░"
            rating = "S 級"
            desc = "靈魂連接良好"
        elif avg_delay <= 1000:
            bars = "████░░░░░░"
            rating = "A 級"
            desc = "靈魂連接尚可"
        else:
            bars = "██░░░░░░░░"
            rating = "B 級"
            desc = "靈魂連接不穩定"
        
        return f"{bars} **{rating}**\n*{desc}*"


def setup(bot):
    bot.add_cog(Ping(bot))
    logger.info("✨ 延遲測試 Cog 已載入完成")
