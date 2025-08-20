import discord
from discord.ext import commands
import random

FEEDBACK_CHANNEL_ID = 1372560258228162560

class Feedback(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @discord.slash_command(name="feedback", description="幽幽子聆聽你的靈魂之聲～提交反饋吧！")
    async def feedback(self, ctx: discord.ApplicationContext, description: str = None):
        """Command to collect user feedback with category buttons."""

        class FeedbackView(discord.ui.View):
            def __init__(self, bot):
                super().__init__(timeout=300)
                self.bot = bot

            async def handle_feedback(self, interaction: discord.Interaction, category: str):
                feedback_channel = self.bot.get_channel(FEEDBACK_CHANNEL_ID)
                if feedback_channel is None:
                    await interaction.response.send_message(
                        "哎呀～靈魂的回音無法傳達，反饋之地尚未設置好呢…請聯繫作者哦～",
                        ephemeral=True
                    )
                    return

                embed = discord.Embed(
                    title="🌸 幽幽子收到的靈魂之聲 🌸",
                    description=(
                        f"**分類:** {category}\n"
                        f"**靈魂:** {interaction.user.mention}\n"
                        f"**回音:** {description if description else '未提供描述'}"
                    ),
                    color=discord.Color.from_rgb(255, 182, 193)
                )
                embed.timestamp = discord.utils.utcnow()

                await feedback_channel.send(embed=embed)
                yuyuko_thanks = [
                    "感謝你的靈魂之聲，我會好好聆聽的～",
                    "嘻嘻，你的回音已傳到我的耳邊，謝謝你哦～",
                    "靈魂的低語真美妙，感謝你的反饋！",
                    "幽幽子已收到你的心聲，願亡魂平安～"
                ]
                await interaction.response.send_message(
                    random.choice(yuyuko_thanks),
                    ephemeral=True
                )

            @discord.ui.button(label="指令錯誤或無回應", style=discord.ButtonStyle.primary)
            async def command_error_button(self, button, interaction):
                await self.handle_feedback(interaction, "指令錯誤或無回應")

            @discord.ui.button(label="機器人訊息問題", style=discord.ButtonStyle.primary)
            async def message_issue_button(self, button, interaction):
                await self.handle_feedback(interaction, "機器人訊息問題")

            @discord.ui.button(label="迷你遊戲系統錯誤", style=discord.ButtonStyle.primary)
            async def minigame_error_button(self, button, interaction):
                await self.handle_feedback(interaction, "迷你遊戲系統錯誤")

            @discord.ui.button(label="建議新增功能", style=discord.ButtonStyle.success)
            async def suggest_feature_button(self, button, interaction):
                await self.handle_feedback(interaction, "建議新增功能")

            @discord.ui.button(label="UI體驗問題", style=discord.ButtonStyle.secondary)
            async def ui_issue_button(self, button, interaction):
                await self.handle_feedback(interaction, "UI體驗問題")

            @discord.ui.button(label="性能或延遲", style=discord.ButtonStyle.danger)
            async def performance_issue_button(self, button, interaction):
                await self.handle_feedback(interaction, "性能或延遲")

            @discord.ui.button(label="資料遺失/異常", style=discord.ButtonStyle.danger)
            async def data_issue_button(self, button, interaction):
                await self.handle_feedback(interaction, "資料遺失/異常")

            @discord.ui.button(label="賭博系統問題", style=discord.ButtonStyle.secondary)
            async def channel_issue_button(self, button, interaction):
                await self.handle_feedback(interaction, "賭博系統問題")

            @discord.ui.button(label="其他問題", style=discord.ButtonStyle.primary)
            async def other_issue_button(self, button, interaction):
                await self.handle_feedback(interaction, "其他問題")

        view = FeedbackView(self.bot)
        if description:
            await ctx.respond(
                f"你的靈魂之聲我聽到了～「{description}」\n請選擇以下類別，讓我更好地理解你的心意吧：",
                view=view,
                ephemeral=True
            )
        else:
            await ctx.respond(
                "幽幽子在此聆聽你的心聲～請選擇以下類別，並補充具體描述哦：",
                view=view,
                ephemeral=True
            )

def setup(bot: discord.Bot):
    bot.add_cog(Feedback(bot))
