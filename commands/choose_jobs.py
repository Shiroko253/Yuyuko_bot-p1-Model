import discord
from discord.ext import commands
import logging
import asyncio
import os
from typing import Dict, Any

logger = logging.getLogger("SakuraBot.commands.choose_jobs")


class ChooseJob(commands.Cog):
    """
    ✿ 冥界職業祭典 ✿
    幽幽子邀你在櫻花樹下選擇屬於你的靈魂工作～
    """
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @discord.slash_command(name="choose_job", description="幽幽子邀你選擇靈魂的工作～")
    async def choose_job(self, ctx: discord.ApplicationContext):
        guild_id = str(ctx.guild.id)
        user_id = str(ctx.user.id)
        data_manager = self.bot.data_manager

        # [Debug 修復 #3] 加入在線備份攔截
        if not await data_manager.check_backup_status(ctx, "choose_job"):
            return

        # [Debug 修復 #1] 直接讀取記憶體中的 user_config，不再讀取硬碟 YAML
        user_config = data_manager.user_config

        # [Debug 修復 #2] 使用 asyncio.to_thread 讀取靜態設定檔，避免阻塞 Event Loop
        config_path = os.path.join(data_manager.config_dir, "config.json")
        config_data = await asyncio.to_thread(data_manager._load_json, config_path, {})

        jobs_list = config_data.get("jobs", [])
        if isinstance(jobs_list, list) and len(jobs_list) > 0:
            jobs_data = jobs_list[0]
        elif isinstance(jobs_list, dict):
            jobs_data = jobs_list
        else:
            jobs_data = {}

        # 檢查是否已有職業 (直接讀取記憶體)
        if guild_id in user_config and user_id in user_config[guild_id]:
            current_job = user_config[guild_id][user_id].get("job")
            if current_job:
                await ctx.respond(embed=discord.Embed(
                    title="🌸 冥界職業已選定～",
                    description=(
                        f"你的靈魂已在冥界簽約，當前職業是 **{current_job}**。\n"
                        "想要轉換靈魂工作嗎？請悄悄找幽幽子或管理員～"
                    ),
                    color=discord.Color.blue()
                ).set_footer(text="幽幽子祝你工作順利，賞櫻愉快～"), ephemeral=True)
                return

        if not isinstance(jobs_data, dict) or not jobs_data:
            await ctx.respond(embed=discord.Embed(
                title="🌸 冥界混沌～",
                description="職業數據尚未正確配置，幽幽子也迷糊了！請快去找管理員賞櫻解惑～",
                color=discord.Color.red()
            ), ephemeral=True)
            return

        class JobSelect(discord.ui.Select):
            def __init__(self_inner, parent_view):
                self_inner.parent_view = parent_view

                # 計算當前 IT 程序員人數 (直接讀取記憶體)
                it_count = sum(
                    1 for u_info in user_config.get(guild_id, {}).values()
                    if isinstance(u_info, dict) and u_info.get("job") == "IT程序員"
                )
                
                options = []
                for job, data in jobs_data.items():
                    if not isinstance(data, dict) or "min" not in data or "max" not in data:
                        continue
                    if job == "IT程序員" and it_count >= 2:
                        options.append(discord.SelectOption(
                            label=f"   {job}   ",
                            description=f"{data['min']}-{data['max']}幽靈幣（已滿員）",
                            value=f"{job}_disabled", emoji="❌"
                        ))
                    else:
                        options.append(discord.SelectOption(
                            label=f"   {job}   ",
                            description=f"{data['min']}-{data['max']}幽靈幣",
                            value=job, emoji="🌸"
                        ))
                super().__init__(
                    placeholder="請選擇你的靈魂工作～",
                    options=options[:25], min_values=1, max_values=1
                )

            async def callback(self_inner, interaction: discord.Interaction):
                if interaction.user.id != ctx.user.id:
                    await interaction.response.send_message("這不是你的冥界工作選擇喲～", ephemeral=True)
                    return

                chosen_job = self_inner.values[0]
                if "_disabled" in chosen_job:
                    await interaction.response.send_message("此職業已滿員，請選其他工作吧！", ephemeral=True)
                    return

                # [Debug 修復 #1] 直接修改記憶體中的 user_config
                if guild_id not in user_config:
                    user_config[guild_id] = {}
                
                # [Debug 修復 #1] IT程序員人數限制：在修改前再次驗證記憶體中的數據，防止併發超員
                if chosen_job == "IT程序員":
                    it_count_now = sum(
                        1 for u_info in user_config.get(guild_id, {}).values()
                        if isinstance(u_info, dict) and u_info.get("job") == "IT程序員"
                    )
                    if it_count_now >= 2:
                        await interaction.response.send_message(
                            "很遺憾，IT程序員已在你選擇的瞬間被搶先一步，請選擇其他職業！", 
                            ephemeral=True
                        )
                        return

                # 寫入記憶體
                user_config[guild_id][user_id] = {"job": chosen_job, "work_cooldown": None}

                # [Debug 修復 #1] 使用統一的 save_all_async 保存，受 save_lock 保護
                try:
                    await data_manager.save_all_async()
                except Exception as e:
                    logger.exception(f"儲存職業資料失敗 {user_id}: {e}")
                    await interaction.response.send_message(embed=discord.Embed(
                        title="🌸 櫻花飄散，資料儲存失敗～",
                        description="儲存職業資料時遇到靈魂迷宮，請找管理員或幽幽子！",
                        color=discord.Color.red()
                    ), ephemeral=True)
                    return

                # 成功後的 UI 更新
                if chosen_job == "賭徒":
                    embed = discord.Embed(
                        title="🃏 靈魂簽約成功！賭徒之契約～",
                        description=(
                            "你已選擇 **賭徒**，從今以後與幽幽子共舞於生死邊緣！\n"
                            "在 21 點遊戲中，你的賠率將提升至 **3 倍**！\n"
                            "但記住：賭博有風險，櫻花亦無常～"
                        ),
                        color=discord.Color.dark_red()
                    ).set_footer(text="命運之輪，由你轉動...")
                else:
                    embed = discord.Embed(
                        title="🌸 靈魂簽約成功！～",
                        description=(
                            f"你已選擇 **{chosen_job}**，"
                            f"從今以後成為冥界櫻花園的 {chosen_job}！\n"
                            "幽幽子祝你靈魂工作愉快，每天都有好吃的～"
                        ),
                        color=discord.Color.green()
                    ).set_footer(text="櫻花飄落，萬物皆美好～")

                for child in self_inner.parent_view.children:
                    child.disabled = True
                self_inner.parent_view.stop()
                await interaction.response.edit_message(embed=embed, view=self_inner.parent_view)

        class JobView(discord.ui.View):
            def __init__(self_inner, cog):
                super().__init__(timeout=60)
                self_inner.cog = cog
                self_inner.message = None
                self_inner.add_item(JobSelect(self_inner))

            async def on_timeout(self_inner):
                for child in self_inner.children:
                    child.disabled = True
                embed = discord.Embed(
                    title="🌸 選擇超時，櫻花落盡～",
                    description="冥界櫻花已謝，請重新使用指令再來選擇靈魂工作吧！",
                    color=discord.Color.orange()
                ).set_footer(text="幽幽子靜候你的再次選擇")
                try:
                    # [Debug 修復 #2] 現在 self_inner.message 是真正的 Message 物件，edit 可以正常運作
                    if self_inner.message:
                        await self_inner.message.edit(embed=embed, view=self_inner)
                except Exception as e:
                    logger.exception(f"Timeout 訊息更新失敗 {ctx.user.id}: {e}")

        try:
            view = JobView(self)
            embed = discord.Embed(
                title="🌸 冥界職業祭典開啟～",
                description="幽幽子在櫻花樹下等待你的靈魂選擇！\n請從下方選擇你的靈魂工作：",
                color=discord.Color.blurple()
            ).set_footer(text="每個職業收入不同，櫻花舞者各有命運")
            
            response = await ctx.respond(embed=embed, view=view)
            # [Debug 修復 #2] 必須使用 original_response() 獲取真正的 Message 物件
            view.message = await response.original_response()
        except Exception as e:
            logger.exception(f"發送職業選擇訊息失敗 {user_id}: {e}")
            await ctx.respond(embed=discord.Embed(
                title="🌸 冥界混沌，無法開啟職業選擇～",
                description="無法發送職業選擇訊息，幽幽子也迷糊了！請稍後再試～",
                color=discord.Color.red()
            ), ephemeral=True)


def setup(bot: discord.Bot):
    bot.add_cog(ChooseJob(bot))
    logger.info("ChooseJob Cog loaded successfully")
