import discord
from discord.ext import commands
import random
import logging
import os
import aiohttp
from datetime import datetime, timezone

logger = logging.getLogger("SakuraBot.Feedback")

# Discord embed field value 上限
_EMBED_FIELD_LIMIT = 1024


class FeedbackView(discord.ui.View):
    """幽幽子的反饋選擇器，如櫻花般優雅地綻放"""

    def __init__(self, bot: discord.Bot, description: str = None):
        super().__init__(timeout=300)
        self.bot = bot
        # [Debug 修復] 移除了 session 參數，不再需要傳遞長駐 session
        
        if description and len(description) > _EMBED_FIELD_LIMIT:
            description = description[:_EMBED_FIELD_LIMIT - 3] + "..."
        self.description = description
        
        self.yuyuko_thanks = [
            "感謝你的靈魂之聲～幽幽子會輕輕地把它收進櫻花瓣裡！",
            "嘻嘻，你的回音已飄進冥界櫻花林，謝謝你喲～",
            "亡魂的低語真美妙，幽幽子會細細聆聽！",
            "幽幽子已收到你的心聲，願亡魂平安、櫻花常在～",
            "靈魂的反饋已流入櫻花河，幽幽子很開心喔！",
            "你的心意已隨櫻花瓣飄至冥界深處，幽幽子收到囉～",
            "這份回音好溫暖呢，幽幽子會好好珍惜的！"
        ]

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
        self.stop()

    async def handle_feedback(self, interaction: discord.Interaction, category: str):
        """將靈魂的回音透過 Webhook 傳遞至冥界櫻花園"""
        
        # 立刻 defer 買時間，防止 Webhook 延遲導致 Interaction 超時報錯
        await interaction.response.defer(ephemeral=True)

        webhook_url = os.getenv("FEEDBACK_WEBHOOK_URL")

        if not webhook_url:
            logger.error("未設置 FEEDBACK_WEBHOOK_URL 環境變數")
            await interaction.followup.send(
                "哎呀～冥界回音無法傳達，櫻花小徑還沒鋪好呢…\n"
                "請聯繫幽幽子或管理員設置 FEEDBACK_WEBHOOK_URL！💐",
                ephemeral=True
            )
            return

        embed = discord.Embed(
            title="🌸 幽幽子收到的冥界靈魂回音 🌸",
            color=discord.Color.from_rgb(255, 182, 193),
            timestamp=datetime.now(timezone.utc)
        )
        embed.add_field(name="📋 分類", value=f"```{category}```", inline=False)
        embed.add_field(
            name="👤 靈魂使者",
            value=f"{interaction.user.mention} (`{interaction.user.name}`)",
            inline=True
        )
        embed.add_field(name="🆔 使用者 ID", value=f"`{interaction.user.id}`", inline=True)
        embed.add_field(
            name="🏰 來自伺服器",
            value=(
                f"**{interaction.guild.name}**\n`{interaction.guild.id}`"
                if interaction.guild else "**私訊**"
            ),
            inline=False
        )
        embed.add_field(
            name="💬 回音內容",
            value=self.description if self.description else "*未提供具體描述*",
            inline=False
        )
        embed.set_footer(
            text=f"靈魂 ID: {interaction.user.id}",
            icon_url=interaction.user.display_avatar.url
        )

        try:
            webhook_data = {
                "embeds": [embed.to_dict()],
                "username": "幽幽子的櫻花回音",
                "avatar_url": self.bot.user.display_avatar.url if self.bot.user else None
            }

            # [Debug 修復] 每次發送時建立臨時 Session，避免在 Cog 初始化時因沒有 Event Loop 而崩潰
            async with aiohttp.ClientSession() as session:
                async with session.post(webhook_url, json=webhook_data) as response:
                    if response.status in [200, 204]:
                        logger.info(
                            f"收到來自 {interaction.user} ({interaction.user.id}) 的反饋: {category}"
                        )
                        await interaction.followup.send(
                            f"✨ {random.choice(self.yuyuko_thanks)}",
                            ephemeral=True
                        )
                    else:
                        error_text = await response.text()
                        logger.error(f"Webhook 發送失敗（狀態碼 {response.status}）: {error_text}")
                        await interaction.followup.send(
                            "啊呀…櫻花瓣在半空中散落了，請稍後再試一次吧～",
                            ephemeral=True
                        )

        except aiohttp.ClientError as e:
            logger.error(f"Webhook 發送時發生網路錯誤: {e}")
            await interaction.followup.send(
                "櫻花小徑暫時被雲霧遮蔽了…請稍後再試～",
                ephemeral=True
            )
        except Exception as e:
            logger.error(f"發送反饋時發生未預期錯誤: {e}", exc_info=True)
            await interaction.followup.send(
                "幽幽子在傳遞回音時遇到了小問題…請稍後再試吧～",
                ephemeral=True
            )

    @discord.ui.button(label="指令錯誤或無回應", style=discord.ButtonStyle.primary, emoji="💬", row=0)
    async def command_error_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        await self.handle_feedback(interaction, "指令錯誤或無回應")

    @discord.ui.button(label="機器人訊息問題", style=discord.ButtonStyle.primary, emoji="🤖", row=0)
    async def message_issue_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        await self.handle_feedback(interaction, "機器人訊息問題")

    @discord.ui.button(label="迷你遊戲系統錯誤", style=discord.ButtonStyle.primary, emoji="🎮", row=0)
    async def minigame_error_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        await self.handle_feedback(interaction, "迷你遊戲系統錯誤")

    @discord.ui.button(label="建議新增功能", style=discord.ButtonStyle.success, emoji="✨", row=1)
    async def suggest_feature_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        await self.handle_feedback(interaction, "建議新增功能")

    @discord.ui.button(label="UI 體驗問題", style=discord.ButtonStyle.secondary, emoji="🎨", row=1)
    async def ui_issue_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        await self.handle_feedback(interaction, "UI 體驗問題")

    @discord.ui.button(label="性能或延遲", style=discord.ButtonStyle.danger, emoji="🐢", row=1)
    async def performance_issue_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        await self.handle_feedback(interaction, "性能或延遲")

    @discord.ui.button(label="資料遺失/異常", style=discord.ButtonStyle.danger, emoji="📦", row=2)
    async def data_issue_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        await self.handle_feedback(interaction, "資料遺失/異常")

    @discord.ui.button(label="賭博系統問題", style=discord.ButtonStyle.secondary, emoji="🎲", row=2)
    async def gambling_issue_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        await self.handle_feedback(interaction, "賭博系統問題")

    @discord.ui.button(label="其他問題", style=discord.ButtonStyle.primary, emoji="❔", row=2)
    async def other_issue_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        await self.handle_feedback(interaction, "其他問題")


class Feedback(commands.Cog):
    """
    ✿ 冥界靈魂回音 ✿
    幽幽子溫柔地聆聽每一位亡魂的心聲，將你的反饋化作櫻花回音～
    """

    def __init__(self, bot: discord.Bot):
        self.bot = bot
        # [Debug 修復] 徹底移除了 self.session = aiohttp.ClientSession()
        # 避免在 Cog 載入階段因沒有 Event Loop 而引發 RuntimeError

        webhook_url = os.getenv("FEEDBACK_WEBHOOK_URL")
        if webhook_url:
            logger.info("冥界回音系統已啟動，幽幽子開始聆聽靈魂之聲（使用 Webhook）")
        else:
            logger.warning("未設置 FEEDBACK_WEBHOOK_URL，反饋功能將無法正常運作")

    @discord.slash_command(
        name="feedback",
        description="🌸 幽幽子聆聽你的靈魂之聲～提交反饋吧！"
    )
    async def feedback(
        self,
        ctx: discord.ApplicationContext,
        # [Debug 修復] 明確傳入 str 作為第一個參數，確保 Pycord 正確解析型別
        description: str = discord.Option(
            str,
            description="反饋的詳細描述（選填）",
            required=False,
            default=None
        )
    ):
        """讓幽幽子收到你的心聲～選擇反饋分類，櫻花會為你傳遞祝福"""
        
        # [Debug 修復] 不再傳遞 session 給 View
        view = FeedbackView(self.bot, description)

        if description:
            response_text = (
                f"🌸 你的靈魂之聲幽幽子聽到了～\n"
                f"**回音內容:** {description}\n\n"
                f"請選擇下方櫻花分類，讓幽幽子更好地理解你的心意："
            )
        else:
            response_text = (
                "🌸 幽幽子在冥界櫻花樹下靜靜聆聽你的心聲～\n\n"
                "請選擇下方分類提交反饋。\n"
                "💡 **小提示:** 下次可以在指令中加上 `description` 參數，"
                "這樣幽幽子就能更清楚地了解你的問題囉！"
            )

        await ctx.respond(response_text, view=view, ephemeral=True)
        logger.info(f"{ctx.author} ({ctx.author.id}) 開啟了反饋選單")


def setup(bot: discord.Bot):
    bot.add_cog(Feedback(bot))
    logger.info("Feedback Cog 已載入～櫻花回音等待靈魂之聲")
