import discord
from discord.ext import commands
import random
import logging
from datetime import datetime, timedelta
from typing import Dict, Any

WORK_COOLDOWN_SECONDS = 3600  # 1 小時

GAMBLER_QUOTES = [
    "賭博才是王道 工作？ 額哈哈哈 有什麽用呢！",
    "賭博才是我該踏上的路程 誰也別想阻攔我！",
    "要是沒有輸光的覺悟，就別坐上賭桌！",
    "工作？哈哈哈——那是浪費我下注時間的牢籠！"
]

class Work(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot
        self.logger = logging.getLogger(__name__)

    @commands.slash_command(
        name="work",
        description="執行你的工作並賺取幽靈幣！"
    )
    async def work(self, ctx: discord.ApplicationContext):
        try:
            await ctx.defer(ephemeral=True)

            # 防止在 DM 使用
            if ctx.guild is None:
                await ctx.respond(
                    embed=discord.Embed(
                        title="🌸 無法工作 🌸",
                        description="幽幽子的工作只能在伺服器頻道執行哦～",
                        color=discord.Color.red()
                    ).set_footer(text="請到伺服器頻道使用指令"),
                    ephemeral=True
                )
                return

            guild_id = str(ctx.guild.id)
            user_id = str(ctx.user.id)

            user_data: Dict[str, Any] = self.bot.data_manager.load_yaml("config/config_user.yml", {})
            user_balance: Dict[str, Any] = self.bot.data_manager.load_json("economy/balance.json", {})
            config_data: Dict[str, Any] = self.bot.data_manager.load_json("config/config.json", {})
            jobs_data: Dict[str, Any] = config_data.get("jobs", [{}])[0] if config_data.get("jobs") else {}

            user_balance.setdefault(guild_id, {})
            user_info = user_data.setdefault(guild_id, {}).setdefault(user_id, {})

            # 沒選職業
            if not user_info.get("job"):
                await ctx.respond(
                    "你尚未選擇職業，請先使用 `/choose_jobs` 選擇你的職業！", ephemeral=True
                )
                return

            job_name = user_info["job"]

            # 賭徒職業：隨機語錄
            if job_name == "賭徒":
                embed = discord.Embed(
                    title="工作系統",
                    description=random.choice(GAMBLER_QUOTES),
                    color=discord.Color.from_rgb(255, 0, 0)
                ).set_footer(text="賭徒無法透過工作賺取幽靈幣")
                await ctx.respond(embed=embed, ephemeral=True)
                return

            job_rewards = jobs_data.get(job_name)
            if not job_rewards or not isinstance(job_rewards, dict) or "min" not in job_rewards or "max" not in job_rewards:
                await ctx.respond(
                    f"無效的職業: {job_name}，請重新選擇！", ephemeral=True
                )
                return

            # 防呆：MP
            user_info.setdefault("MP", 0)
            if user_info["MP"] >= 200:
                await ctx.respond(
                    "你的心理壓力已達到最大值！請休息一下再繼續工作。", ephemeral=True
                )
                return

            # 冷卻判斷
            last_cooldown = user_info.get("work_cooldown")
            now = datetime.now()
            if last_cooldown:
                try:
                    cooldown_time = datetime.fromisoformat(last_cooldown)
                except Exception:
                    cooldown_time = None
                if cooldown_time and cooldown_time > now:
                    remaining = cooldown_time - now
                    minutes, seconds = divmod(remaining.total_seconds(), 60)
                    embed = discord.Embed(
                        title="冷卻中",
                        description=f"你正在冷卻中，還需等待 {int(minutes)} 分鐘 {int(seconds)} 秒！",
                        color=discord.Color.red()
                    ).set_footer(text=f"職業: {job_name}")
                    await ctx.respond(embed=embed, ephemeral=True)
                    return

            # 工作獎勵
            reward = random.randint(job_rewards["min"], job_rewards["max"])
            user_balance[guild_id].setdefault(user_id, 0)
            user_balance[guild_id][user_id] += reward

            # 更新冷卻、壓力
            user_info["work_cooldown"] = (now + timedelta(seconds=WORK_COOLDOWN_SECONDS)).isoformat()
            user_info["MP"] += 10

            # 資料保存
            self.bot.data_manager.save_json("economy/balance.json", user_balance)
            self.bot.data_manager.save_yaml("config/config_user.yml", user_data)

            embed = discord.Embed(
                title="工作成功！",
                description=(
                    f"{ctx.user.mention} 作為 **{job_name}** "
                    f"賺取了 **{reward} 幽靈幣**！🎉\n"
                    f"當前心理壓力（MP）：{user_info['MP']}/200"
                ),
                color=discord.Color.green()
            ).set_footer(text=f"職業: {job_name}")
            await ctx.respond(embed=embed, ephemeral=True)

        except Exception as e:
            self.logger.exception(f"work 指令錯誤: {e}")
            try:
                await ctx.respond(
                    "執行工作時發生錯誤，請稍後再試或用 /feedback 回報作者。", ephemeral=True
                )
            except Exception:
                pass

def setup(bot: discord.Bot):
    bot.add_cog(Work(bot))
    logging.info("Work Cog loaded successfully")