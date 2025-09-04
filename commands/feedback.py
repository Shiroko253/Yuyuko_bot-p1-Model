import discord
from discord.ext import commands
import random

FEEDBACK_CHANNEL_ID = 1372560258228162560  # 冥界反饋之地

class Feedback(commands.Cog):
    """
    ✿ 冥界靈魂回音 ✿
    幽幽子溫柔地聆聽每一位亡魂的心聲，將你的反饋化作櫻花回音～
    """
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @discord.slash_command(name="feedback", description="幽幽子聆聽你的靈魂之聲～提交反饋吧！")
    async def feedback(self, ctx: discord.ApplicationContext, description: str = None):
        """讓幽幽子收到你的心聲～選擇反饋分類，櫻花會為你傳遞祝福。"""

        class FeedbackView(discord.ui.View):
            def __init__(self, bot):
                super().__init__(timeout=300)
                self.bot = bot

            async def handle_feedback(self, interaction: discord.Interaction, category: str):
                feedback_channel = self.bot.get_channel(FEEDBACK_CHANNEL_ID)
                if feedback_channel is None:
                    await interaction.response.send_message(
                        "哎呀～冥界回音無法傳達，櫻花小徑還沒鋪好呢…請聯繫幽幽子或管理員喲～",
                        ephemeral=True
                    )
                    return

                embed = discord.Embed(
                    title="🌸 幽幽子收到的冥界靈魂回音 🌸",
                    description=(
                        f"**分類:** {category}\n"
                        f"**靈魂使者:** {interaction.user.mention}\n"
                        f"**回音內容:** {description if description else '未提供描述'}"
                    ),
                    color=discord.Color.from_rgb(255, 182, 193)
                )
                embed.timestamp = discord.utils.utcnow()

                await feedback_channel.send(embed=embed)
                yuyuko_thanks = [
                    "感謝你的靈魂之聲～幽幽子會輕輕地把它收進櫻花瓣裡！",
                    "嘻嘻，你的回音已飄進冥界櫻花林，謝謝你喲～",
                    "亡魂的低語真美妙，幽幽子會細細聆聽！",
                    "幽幽子已收到你的心聲，願亡魂平安、櫻花常在～",
                    "靈魂的反饋已流入櫻花河，幽幽子很開心喔！"
                ]
                await interaction.response.send_message(
                    random.choice(yuyuko_thanks),
                    ephemeral=True
                )

            @discord.ui.button(label="指令錯誤或無回應", style=discord.ButtonStyle.primary, emoji="💬")
            async def command_error_button(self, button, interaction):
                await self.handle_feedback(interaction, "指令錯誤或無回應")

            @discord.ui.button(label="機器人訊息問題", style=discord.ButtonStyle.primary, emoji="🤖")
            async def message_issue_button(self, button, interaction):
                await self.handle_feedback(interaction, "機器人訊息問題")

            @discord.ui.button(label="迷你遊戲系統錯誤", style=discord.ButtonStyle.primary, emoji="🎮")
            async def minigame_error_button(self, button, interaction):
                await self.handle_feedback(interaction, "迷你遊戲系統錯誤")

            @discord.ui.button(label="建議新增功能", style=discord.ButtonStyle.success, emoji="✨")
            async def suggest_feature_button(self, button, interaction):
                await self.handle_feedback(interaction, "建議新增功能")

            @discord.ui.button(label="UI體驗問題", style=discord.ButtonStyle.secondary, emoji="🎨")
            async def ui_issue_button(self, button, interaction):
                await self.handle_feedback(interaction, "UI體驗問題")

            @discord.ui.button(label="性能或延遲", style=discord.ButtonStyle.danger, emoji="🐢")
            async def performance_issue_button(self, button, interaction):
                await self.handle_feedback(interaction, "性能或延遲")

            @discord.ui.button(label="資料遺失/異常", style=discord.ButtonStyle.danger, emoji="📦")
            async def data_issue_button(self, button, interaction):
                await self.handle_feedback(interaction, "資料遺失/異常")

            @discord.ui.button(label="賭博系統問題", style=discord.ButtonStyle.secondary, emoji="🎲")
            async def channel_issue_button(self, button, interaction):
                await self.handle_feedback(interaction, "賭博系統問題")

            @discord.ui.button(label="其他問題", style=discord.ButtonStyle.primary, emoji="❔")
            async def other_issue_button(self, button, interaction):
                await self.handle_feedback(interaction, "其他問題")

        view = FeedbackView(self.bot)
        if description:
            await ctx.respond(
                f"你的靈魂之聲幽幽子聽到了～「{description}」\n請選擇下方櫻花分類，讓幽幽子更好地理解你的心意：",
                view=view,
                ephemeral=True
            )
        else:
            await ctx.respond(
                "幽幽子在冥界櫻花樹下靜靜聆聽你的心聲～請選擇下方分類，並記得補充具體描述喲：",
                view=view,
                ephemeral=True
            )

def setup(bot: discord.Bot):
    """
    ✿ 幽幽子優雅地將冥界回音功能裝進 bot 裡 ✿
    """
    bot.add_cog(Feedback(bot))