import discord
from discord.ext import commands
import logging
from typing import Dict, Any

class ChooseJob(commands.Cog):
    """
    ✿ 冥界職業祭典 ✿
    幽幽子邀你在櫻花樹下選擇屬於你的靈魂工作～
    """
    def __init__(self, bot: discord.Bot):
        self.bot = bot
        self.logger = logging.getLogger(__name__)

    @discord.slash_command(name="choose_job", description="幽幽子邀你選擇靈魂的工作～")
    async def choose_job(self, ctx: discord.ApplicationContext):
        guild_id = str(ctx.guild.id)
        user_id = str(ctx.user.id)

        # 載入資料
        user_data: Dict[str, Any] = self.bot.data_manager.load_yaml("config/config_user.yml", {})
        config_data: Dict[str, Any] = self.bot.data_manager.load_json("config/config.json", {})
        jobs_data: Dict[str, Any] = config_data.get("jobs", [{}])[0] if config_data.get("jobs") else {}

        # 檢查用戶是否已有職業
        if guild_id in user_data and user_id in user_data[guild_id]:
            current_job = user_data[guild_id][user_id].get("job")
            if current_job:
                embed = discord.Embed(
                    title="🌸 冥界職業已選定～",
                    description=f"你的靈魂已在冥界簽約，當前職業是 **{current_job}**。\n想要轉換靈魂工作嗎？請悄悄找幽幽子或管理員～",
                    color=discord.Color.blue()
                ).set_footer(text="幽幽子祝你工作順利，賞櫻愉快～")
                await ctx.respond(embed=embed, ephemeral=True)
                return

        # 檢查職業資料
        if not jobs_data or not isinstance(jobs_data, dict):
            embed = discord.Embed(
                title="🌸 冥界混沌～",
                description="職業數據尚未正確配置，幽幽子也迷糊了！請快去找管理員賞櫻解惑～",
                color=discord.Color.red()
            ).set_footer(text="櫻花落下時，請及時修復職業設定")
            await ctx.respond(embed=embed, ephemeral=True)
            return

        class JobSelect(discord.ui.Select):
            def __init__(self, parent_view):
                self.parent_view = parent_view
                # 計算 IT程序員已選人數
                it_count = sum(
                    1 for u_id, u_info in user_data.get(guild_id, {}).items()
                    if isinstance(u_info, dict) and u_info.get("job") == "IT程序員"
                )

                options = []
                for job, data in jobs_data.items():
                    if isinstance(data, dict) and "min" in data and "max" in data:
                        # IT程序員最多2人
                        if job == "IT程序員" and it_count >= 2:
                            options.append(discord.SelectOption(
                                label=f"   {job}   ",
                                description=f"{data['min']}-{data['max']}幽靈幣（已滿員，櫻花凋零）",
                                value=f"{job}_disabled",
                                emoji="❌"
                            ))
                        else:
                            options.append(discord.SelectOption(
                                label=f"   {job}   ",
                                description=f"{data['min']}-{data['max']}幽靈幣",
                                value=job,
                                emoji="🌸"
                            ))

                super().__init__(
                    placeholder="請選擇你的靈魂工作～",
                    options=options,
                    min_values=1,
                    max_values=1
                )

            async def callback(self, interaction: discord.Interaction):
                if interaction.user.id != ctx.user.id:
                    await interaction.response.send_message("這不是你的冥界工作選擇喲～", ephemeral=True)
                    return

                chosen_job = self.values[0]
                if "_disabled" in chosen_job:
                    await interaction.response.send_message("此職業已滿員，櫻花已謝～請選其他工作吧！", ephemeral=True)
                    return

                if guild_id not in user_data:
                    user_data[guild_id] = {}
                if user_id not in user_data[guild_id]:
                    user_data[guild_id][user_id] = {}

                user_info = user_data[guild_id][user_id]
                user_info["job"] = chosen_job
                user_info.setdefault("work_cooldown", None)

                try:
                    self.parent_view.cog.bot.data_manager.save_yaml("config/config_user.yml", user_data)
                except Exception as e:
                    self.parent_view.cog.logger.exception(f"Failed to save user data for {user_id}: {e}")
                    embed = discord.Embed(
                        title="🌸 櫻花飄散，資料儲存失敗～",
                        description="儲存職業資料時遇到靈魂迷宮，請找管理員或幽幽子！",
                        color=discord.Color.red()
                    ).set_footer(text="使用 /feedback 召喚幽幽子救援")
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                    return

                for child in self.parent_view.children:
                    child.disabled = True
                embed = discord.Embed(
                    title="🌸 靈魂簽約成功！～",
                    description=f"你已選擇 **{chosen_job}**，從今以後成為冥界櫻花園的 {chosen_job}！\n幽幽子祝你靈魂工作愉快，每天都有好吃的～",
                    color=discord.Color.green()
                ).set_footer(text="櫻花飄落，萬物皆美好～")
                await interaction.response.edit_message(embed=embed, view=self.parent_view)

        class JobView(discord.ui.View):
            def __init__(self, cog):
                super().__init__(timeout=60)
                self.cog = cog
                self.select = JobSelect(self)
                self.add_item(self.select)
                self.message = None  # for timeout

            async def on_timeout(self):
                for child in self.children:
                    child.disabled = True
                embed = discord.Embed(
                    title="🌸 選擇超時，櫻花落盡～",
                    description="冥界櫻花已謝，請重新使用指令再來選擇靈魂工作吧！",
                    color=discord.Color.orange()
                ).set_footer(text="幽幽子靜候你的再次選擇")
                try:
                    if self.message:
                        await self.message.edit(embed=embed, view=self)
                except Exception as e:
                    self.cog.logger.exception(f"Failed to handle timeout for {ctx.user.id}: {e}")

        try:
            view = JobView(self)
            embed = discord.Embed(
                title="🌸 冥界職業祭典開啟～",
                description="幽幽子在櫻花樹下等待你的靈魂選擇！\n請從下方選擇你的靈魂工作：",
                color=discord.Color.blurple()
            ).set_footer(text="每個職業收入不同，櫻花舞者各有命運")
            message = await ctx.respond(embed=embed, view=view)
            view.message = message
        except Exception as e:
            self.logger.exception(f"Failed to send job selection message for {user_id}: {e}")
            embed = discord.Embed(
                title="🌸 冥界混沌，無法開啟職業選擇～",
                description="無法發送職業選擇訊息，幽幽子也迷糊了！請稍後再試～",
                color=discord.Color.red()
            ).set_footer(text="使用 /feedback 召喚幽幽子救援")
            await ctx.respond(embed=embed, ephemeral=True)

def setup(bot: discord.Bot):
    bot.add_cog(ChooseJob(bot))
    logging.info("ChooseJob Cog loaded successfully")