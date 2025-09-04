import discord
from discord.ext import commands
import logging
from typing import Any, Dict

class ResetJob(commands.Cog):
    """
    ✿ 幽幽子的職業重置 ✿
    幫助靈魂放下舊身份，準備迎接新生～
    """
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @discord.slash_command(
        name="reset_job",
        description="重置自己的職業"
    )
    async def reset_job(self, ctx: discord.ApplicationContext):
        guild_id = str(ctx.guild.id)
        user_id = str(ctx.author.id)

        # 資料讀取
        user_data: Dict[str, Any] = self.bot.data_manager.load_yaml("config/config_user.yml", {})
        group_data = user_data.get(guild_id, {})
        user_info = group_data.get(user_id, {})
        current_job = user_info.get("job", "無職業")

        embed = discord.Embed(
            title="職業重置確認",
            description=f"你當前的職業是：`{current_job}`\n\n確定要放棄現有職業嗎？",
            color=discord.Color.orange()
        ).set_footer(text="請選擇 Yes 或 No")

        class ConfirmReset(discord.ui.View):
            def __init__(self, parent_cog):
                super().__init__(timeout=60)
                self.parent_cog = parent_cog
                self.message = None

            @discord.ui.button(label="Yes", style=discord.ButtonStyle.green)
            async def confirm(self, button: discord.ui.Button, interaction: discord.Interaction):
                if interaction.user.id != ctx.author.id:
                    await interaction.response.send_message("這不是你的選擇！", ephemeral=True)
                    return

                try:
                    if guild_id in user_data and user_id in user_data[guild_id]:
                        user_data[guild_id][user_id]["job"] = None
                        user_data[guild_id][user_id]["work_cooldown"] = None
                        self.parent_cog.bot.data_manager.save_yaml("config/config_user.yml", user_data)
                    success_embed = discord.Embed(
                        title="成功",
                        description="你的職業已被清除！",
                        color=discord.Color.green()
                    ).set_footer(text="如需重新選擇可使用 /choose_jobs")
                    await interaction.response.edit_message(embed=success_embed, view=None)
                except Exception as e:
                    logging.exception(f"職業重置失敗: {e}")
                    await interaction.response.send_message("職業重置失敗，請稍後再試或使用 /feedback 回報作者。", ephemeral=True)

            @discord.ui.button(label="No", style=discord.ButtonStyle.red)
            async def cancel(self, button: discord.ui.Button, interaction: discord.Interaction):
                if interaction.user.id != ctx.author.id:
                    await interaction.response.send_message("這不是你的選擇！", ephemeral=True)
                    return

                cancel_embed = discord.Embed(
                    title="操作取消",
                    description="你的職業未被清除。",
                    color=discord.Color.red()
                ).set_footer(text="如需操作請重新執行指令")
                await interaction.response.edit_message(embed=cancel_embed, view=None)

            async def on_timeout(self):
                for child in self.children:
                    child.disabled = True
                try:
                    if self.message:
                        timeout_embed = discord.Embed(
                            title="操作超時",
                            description="職業重置操作已超時，請重新執行指令！",
                            color=discord.Color.orange()
                        ).set_footer(text="如需操作請重新執行指令")
                        await self.message.edit(embed=timeout_embed, view=self)
                except Exception as e:
                    logging.exception(f"reset_job timeout fail: {e}")

        try:
            view = ConfirmReset(self)
            response_msg = await ctx.respond(embed=embed, view=view, ephemeral=True)
            view.message = response_msg  # 直接設為 response_msg，不用 original_response()
        except Exception as e:
            logging.exception(f"Failed to send reset_job view for {user_id}: {e}")
            await ctx.respond("職業重置互動建立失敗，請稍後再試或使用 /feedback 回報作者。", ephemeral=True)

def setup(bot: discord.Bot):
    bot.add_cog(ResetJob(bot))
    logging.info("ResetJob Cog loaded successfully")