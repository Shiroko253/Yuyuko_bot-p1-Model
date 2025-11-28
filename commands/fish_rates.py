import discord
from discord.ext import commands
from discord import ApplicationContext
import asyncio
import logging
from datetime import datetime, timezone
import io
import matplotlib
matplotlib.use('Agg')  # 使用非圖形化後端
import matplotlib.pyplot as plt
from matplotlib import font_manager
import platform

logger = logging.getLogger("SakuraBot.FishRates")


class FishRates(commands.Cog):
    """幽幽子的櫻花湖機率展示系統,揭開冥界的奧秘"""
    
    def __init__(self, bot):
        self.bot = bot
        logger.info("櫻花湖機率展示系統已初始化～")
    
    def get_rarity_weights(self) -> dict:
        """
        獲取稀有度權重,從 Fish Cog 讀取實際計算的權重
        這樣可以確保顯示的機率與實際釣魚機率一致
        """
        try:
            # 嘗試從 Fish Cog 獲取權重
            fish_cog = self.bot.get_cog("Fish")
            if fish_cog:
                # 獲取魚種資料
                fish_data = fish_cog.get_fish_data()
                if fish_data:
                    # 使用 Fish Cog 的方法計算實際權重
                    return fish_cog.calculate_rarity_weights(fish_data)
        except Exception as e:
            logger.warning(f"無法從 Fish Cog 計算權重: {e}")
        
        # 如果無法從 Fish Cog 獲取,使用預設權重
        logger.warning("使用預設稀有度權重")
        return {
            "common": 50.0,
            "uncommon": 30.0,
            "rare": 15.0,
            "legendary": 4.0,
            "deify": 1.0
        }
    
    def get_rarity_display_info(self) -> dict:
        """獲取稀有度的顯示資訊 (中文名稱、顏色等)"""
        return {
            "common": {
                "name": "普通",
                "color": "#57F287",  # 綠色
                "emoji": "🟢"
            },
            "uncommon": {
                "name": "罕見",
                "color": "#3498DB",  # 藍色
                "emoji": "🔵"
            },
            "rare": {
                "name": "稀有",
                "color": "#9B59B6",  # 紫色
                "emoji": "🟣"
            },
            "legendary": {
                "name": "傳說",
                "color": "#E67E22",  # 橙色
                "emoji": "🟠"
            },
            "deify": {
                "name": "神格",
                "color": "#F1C40F",  # 金色
                "emoji": "⭐"
            },
            "unknown": {
                "name": "未知",
                "color": "#95A5A6",  # 灰色
                "emoji": "❓"
            }
        }
    
    def create_rarity_pie_chart(self) -> io.BytesIO:
        """創建稀有度機率餅圖,展示幽幽子的櫻花湖奧秘"""
        
        rarity_weights = self.get_rarity_weights()
        display_info = self.get_rarity_display_info()
        
        # 稀有度資料 - 按機率從大到小排序
        sorted_items = sorted(rarity_weights.items(), key=lambda x: x[1], reverse=True)
        rarities = [item[0] for item in sorted_items]
        probabilities = [item[1] for item in sorted_items]
        
        # 構建標籤和顏色 (使用英文)
        labels = []
        colors = []
        for r in rarities:
            info = display_info.get(r, {"name": r.capitalize(), "color": "#95A5A6"})
            labels.append(f"{r.capitalize()}\n{rarity_weights[r]}%")
            colors.append(info["color"])
        
        # 創建圖表
        plt.figure(figsize=(10, 8))
        
        plt.rcParams['axes.unicode_minus'] = False  # 解決負號顯示問題
        
        # 計算突出效果 (稀有度越低越突出)
        explode = []
        for prob in probabilities:
            if prob <= 1.0:
                explode.append(0.15)  # 非常稀有
            elif prob <= 5.0:
                explode.append(0.1)   # 稀有
            elif prob <= 20.0:
                explode.append(0.05)  # 中等
            else:
                explode.append(0.02)  # 常見
        
        # 繪製餅圖
        wedges, texts, autotexts = plt.pie(
            probabilities,
            labels=labels,
            colors=colors,
            autopct='%1.1f%%',
            startangle=90,
            textprops={'fontsize': 12, 'weight': 'bold'},
            explode=explode
        )
        
        # 設置百分比文字顏色為白色
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(14)
            autotext.set_weight('bold')
        
        # 圖例 (使用英文)
        legend_labels = []
        for r in rarities:
            legend_labels.append(f"{r.capitalize()} ({rarity_weights[r]}%)")
        
        plt.legend(
            wedges,
            legend_labels,
            title="Rarity Rates",
            loc="center left",
            bbox_to_anchor=(1, 0, 0.5, 1),
            fontsize=11
        )
        
        plt.tight_layout()
        
        # 保存到記憶體
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
        buffer.seek(0)
        plt.close()
        
        return buffer

    @discord.slash_command(
        name="fish_rates",
        description="🌸 查看櫻花湖的釣魚機率～幽幽子為你揭開冥界的奧秘"
    )
    async def fish_rates(self, ctx: ApplicationContext):
        """顯示各稀有度的釣魚機率餅圖"""
        
        await ctx.defer()
        
        try:
            rarity_weights = self.get_rarity_weights()
            display_info = self.get_rarity_display_info()
            
            # 生成餅圖
            chart_buffer = await asyncio.to_thread(self.create_rarity_pie_chart)
            
            # 創建 Discord 文件
            file = discord.File(chart_buffer, filename="sakura_fishing_rates.png")
            
            # 構建機率列表 - 按機率從大到小排序
            sorted_items = sorted(rarity_weights.items(), key=lambda x: x[1], reverse=True)
            prob_lines = []
            for rarity, weight in sorted_items:
                info = display_info.get(rarity, {"name": rarity.capitalize(), "emoji": "⚪"})
                prob_lines.append(
                    f"{info['emoji']} {info['name']} ({rarity.capitalize()}): **{weight}%**"
                )
            
            # 創建 Embed
            embed = discord.Embed(
                title="🌸 櫻花湖釣魚機率統計 🌸",
                description=(
                    "幽幽子為你展示櫻花湖中各種魚的出現機率～\n"
                    "櫻花隨風飄落,魚兒隨緣而來,祝你釣魚順利！\n\n"
                    "**機率分布：**\n" + "\n".join(prob_lines)
                ),
                color=discord.Color.from_rgb(255, 182, 193),  # 櫻花粉紅色
                timestamp=datetime.now(timezone.utc)
            )
            
            embed.set_image(url="attachment://sakura_fishing_rates.png")
            embed.set_footer(text="幽幽子祝你釣到心儀的魚～記得多釣幾次增加機會哦！")
            
            await ctx.followup.send(embed=embed, file=file)
            logger.info(f"用戶 {ctx.user} ({ctx.user.id}) 查看了釣魚機率")
            
        except Exception as e:
            logger.error(f"生成釣魚機率圖表時發生錯誤: {e}", exc_info=True)
            await ctx.followup.send(
                "幽幽子在繪製櫻花圖表時迷糊了～請稍後再試！🌸",
                ephemeral=True
            )


def setup(bot):
    """將櫻花湖機率展示系統加入幽幽子的靈魂"""
    bot.add_cog(FishRates(bot))
    logger.info("FishRates Cog 已載入,機率餅圖等待展示～")
