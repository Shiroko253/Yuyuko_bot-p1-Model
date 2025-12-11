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

YUYUKO_WORK_QUOTES = [
    "幽幽子：在冥界賞花之餘，也要努力工作賺幽靈幣喲～",
    "幽幽子：工作結束後要記得吃點心、減壓，亡魂也需要休息～",
    "幽幽子：職業的命運由你自己選擇，賞花、工作、吃點心三連發！"
]

class Work(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot
        self.logger = logging.getLogger(__name__)

    @discord.slash_command(
        name="work",
        description="幽幽子冥界工作：執行你的職業，賺取幽靈幣！"
    )
    async def work(self, ctx: discord.ApplicationContext):
        try:
            await ctx.defer(ephemeral=True)

            if ctx.guild is None:
                embed = discord.Embed(
                    title="🌸 無法工作 🌸",
                    description="幽幽子的工作只能在伺服器頻道執行哦～",
                    color=discord.Color.from_rgb(205, 133, 232)
                ).set_footer(text="幽幽子：請到伺服器賞花、工作吧！")
                await ctx.respond(embed=embed, ephemeral=True)
                return

            guild_id = str(ctx.guild.id)
            user_id = str(ctx.user.id)

            # 使用內存數據並加鎖
            async with self.bot.data_manager.balance_lock:
                # 從內存讀取 balance
                user_balance: Dict[str, Any] = self.bot.data_manager.balance
                
                # 從文件讀取用戶配置和職業配置
                user_data: Dict[str, Any] = self.bot.data_manager._load_yaml("config/config_user.yml") or {}
                config_data: Dict[str, Any] = self.bot.data_manager._load_json("config/config.json") or {}
                jobs_data: Dict[str, Any] = config_data.get("jobs", [{}])[0] if config_data.get("jobs") else {}

                user_balance.setdefault(guild_id, {})
                user_info = user_data.setdefault(guild_id, {}).setdefault(user_id, {})

                if not user_info.get("job"):
                    embed = discord.Embed(
                        title="🌸 尚未選擇職業",
                        description="幽幽子：你還沒有職業，快用 `/choose_jobs` 選擇命運吧！",
                        color=discord.Color.red()
                    ).set_footer(text="幽幽子：冥界賞花要有身份～")
                    await ctx.respond(embed=embed, ephemeral=True)
                    return

                job_name = user_info["job"]

                # 賭徒特殊語錄
                if job_name == "賭徒":
                    embed = discord.Embed(
                        title="🎲 賭徒的命運",
                        description=random.choice(GAMBLER_QUOTES),
                        color=discord.Color.red()
                    ).set_footer(text="幽幽子：賭徒無法透過工作賺取幽靈幣，只能靠命運！")
                    await ctx.respond(embed=embed, ephemeral=True)
                    return

                job_rewards = jobs_data.get(job_name)
                if not job_rewards or not isinstance(job_rewards, dict) or "min" not in job_rewards or "max" not in job_rewards:
                    embed = discord.Embed(
                        title="🌸 無效職業",
                        description=f"幽幽子：職業「{job_name}」無效，請重新選擇！",
                        color=discord.Color.red()
                    )
                    await ctx.respond(embed=embed, ephemeral=True)
                    return

                user_info.setdefault("MP", 0)
                if user_info["MP"] >= 200:
                    embed = discord.Embed(
                        title="🌸 壓力過高！",
                        description="幽幽子：你的心理壓力已達巔峰，快休息、賞花、吃點心吧！",
                        color=discord.Color.red()
                    ).set_footer(text="幽幽子：亡魂要適時減壓～")
                    await ctx.respond(embed=embed, ephemeral=True)
                    return

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
                            title="🌸 工作冷卻中",
                            description=f"幽幽子：你還需等待 {int(minutes)} 分鐘 {int(seconds)} 秒才能再次工作！",
                            color=discord.Color.orange()
                        ).set_footer(text=f"職業：{job_name}")
                        await ctx.respond(embed=embed, ephemeral=True)
                        return

                reward = random.randint(job_rewards["min"], job_rewards["max"])
                user_balance[guild_id].setdefault(user_id, 0)
                
                # 記錄舊餘額用於日誌
                old_balance = user_balance[guild_id][user_id]
                user_balance[guild_id][user_id] += reward
                new_balance = user_balance[guild_id][user_id]

                user_info["work_cooldown"] = (now + timedelta(seconds=WORK_COOLDOWN_SECONDS)).isoformat()
                user_info["MP"] += 10

                # 保存數據 - 使用 save_all() 保存內存中的 balance
                try:
                    self.bot.data_manager.save_all()  # 保存內存中的 balance
                    self.bot.data_manager._save_yaml("config/config_user.yml", user_data)
                    self.logger.info(f"💼 用戶 {user_id} 工作獲得 {reward} 幽靈幣 (餘額: {old_balance:.2f} -> {new_balance:.2f})")
                except Exception as e:
                    self.logger.error(f"❌ 保存工作數據失敗: {e}", exc_info=True)

                embed = discord.Embed(
                    title="🌸 工作成功！🌸",
                    description=(
                        f"{ctx.user.mention} 作為 **{job_name}** "
                        f"賺取了 **{reward:,} 幽靈幣**！🎉\n"
                        f"當前餘額：**{new_balance:,.2f}** 幽靈幣\n"
                        f"當前心理壓力（MP）：{user_info['MP']}/200\n\n"
                        f"{random.choice(YUYUKO_WORK_QUOTES)}"
                    ),
                    color=discord.Color.from_rgb(205, 133, 232)
                ).set_footer(text=f"幽幽子：賞花、工作、吃點心三連發！")
                await ctx.respond(embed=embed, ephemeral=True)

        except Exception as e:
            self.logger.exception(f"work 指令錯誤: {e}")
            try:
                embed = discord.Embed(
                    title="🌸 工作系統錯誤",
                    description="執行工作時發生錯誤，請稍後再試或用 /feedback 回報幽幽子。",
                    color=discord.Color.red()
                ).set_footer(text="幽幽子：冥界也會有小故障哦～")
                await ctx.respond(embed=embed, ephemeral=True)
            except Exception:
                pass

def setup(bot: discord.Bot):
    bot.add_cog(Work(bot))
    logging.info("Work Cog loaded successfully")
