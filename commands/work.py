import discord
from discord.ext import commands
import asyncio
import random
import logging
import os
# [Debug 修復 #1] 補上遺漏的 datetime，否則 fromisoformat 會拋出 NameError 崩潰！
from datetime import datetime, timedelta 

logger = logging.getLogger("SakuraBot.Work")

WORK_COOLDOWN_SECONDS = 3600  # 1 小時

GAMBLER_QUOTES = [
    "賭博才是王道 工作？ 額哈哈哈 有什麽用呢！",
    "賭博才是我該踏上的路程 誰也別想阻攔我！",
    "要是沒有輸光的覺悟，就別坐上賭桌！",
    "工作？哈哈哈——那是浪費我下注時間的牢籠！"
]

YUYUKO_WORK_QUOTES = [
    "幽幽子：在冥界賞花之餘，也要努力工作賺幽靈幣喲～",
    "幽幽子：工作結束後要記得吃點心、恢復體力，亡魂也需要休息～",
    "幽幽子：職業的命運由你自己選擇，賞花、工作、吃點心三連發！"
]


class Work(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot
        self.data_manager = bot.data_manager
        self.logger = logging.getLogger(__name__)

    @discord.slash_command(
        name="work",
        description="幽幽子冥界工作：執行你的職業，賺取幽靈幣！"
    )
    async def work(self, ctx: discord.ApplicationContext):
        try:
            # [Debug 修復] 加入在線備份攔截
            if not await self.data_manager.check_backup_status(ctx, "work"):
                return

            await ctx.defer(ephemeral=True)

            if ctx.guild is None:
                await ctx.respond(
                    embed=discord.Embed(
                        title="🌸 無法工作 🌸",
                        description="幽幽子的工作只能在伺服器頻道執行哦～",
                        color=discord.Color.from_rgb(205, 133, 232)
                    ).set_footer(text="幽幽子：請到伺服器賞花、工作吧！"),
                    ephemeral=True
                )
                return

            guild_id = str(ctx.guild.id)
            user_id = str(ctx.user.id)

            # [Debug 修復] 徹底移除硬碟讀寫！直接引用記憶體中的 user_config
            user_config = self.data_manager.user_config
            
            # [Debug 修復] 使用 to_thread 讀取靜態設定檔，確保路徑正確
            config_path = os.path.join(self.data_manager.config_dir, "config.json")
            config_data = await asyncio.to_thread(
                self.data_manager._load_json, config_path, {}
            )
            jobs_data = config_data.get("jobs", {})

            user_info = user_config.setdefault(guild_id, {}).setdefault(user_id, {})

            if not user_info.get("job"):
                await ctx.respond(
                    embed=discord.Embed(
                        title="🌸 尚未選擇職業",
                        description="幽幽子：你還沒有職業，快用 `/choose_job` 選擇命運吧！",
                        color=discord.Color.red()
                    ).set_footer(text="幽幽子：冥界賞花要有身份～"),
                    ephemeral=True
                )
                return

            job_name = user_info["job"]

            if job_name == "賭徒":
                await ctx.respond(
                    embed=discord.Embed(
                        title="🎲 賭徒的命運",
                        description=random.choice(GAMBLER_QUOTES),
                        color=discord.Color.red()
                    ).set_footer(text="幽幽子：賭徒無法透過工作賺取幽靈幣，只能靠命運！"),
                    ephemeral=True
                )
                return

            job_data = jobs_data.get(job_name)
            if not job_data or not isinstance(job_data, dict) or "min" not in job_data or "max" not in job_data:
                await ctx.respond(
                    embed=discord.Embed(
                        title="🌸 無效職業",
                        description=f"幽幽子：職業「{job_name}」的數據無效，請重新選擇！",
                        color=discord.Color.red()
                    ),
                    ephemeral=True
                )
                return

            # [Debug 修復] 將 MP (壓力) 邏輯徹底替換為 Stamina (體力) 系統
            # 向下相容：如果沒有 stamina 欄位，預設為 20
            if "stamina" not in user_info:
                user_info["stamina"] = 20
            if "max_stamina" not in user_info:
                user_info["max_stamina"] = 20
                
            current_stamina = user_info["stamina"]
            max_stamina = user_info["max_stamina"]
            stamina_cost = job_data.get("stamina_cost", 2) # 預設消耗 2 點體力

            if current_stamina < stamina_cost:
                await ctx.respond(
                    embed=discord.Embed(
                        title="🌸 體力不足！",
                        description=(
                            f"幽幽子：你的體力只剩下 **{current_stamina}/{max_stamina}**，\n"
                            f"但從事「{job_name}」需要消耗 **{stamina_cost}** 點體力！\n\n"
                            "快去 `/shop` 買點好吃的，或者從 `/backpack` 吃點東西恢復體力吧～"
                        ),
                        color=discord.Color.red()
                    ).set_footer(text="幽幽子：亡魂要適時補充體力～"),
                    ephemeral=True
                )
                return

            # [Debug 修復] 使用 discord.utils.utcnow()，最安全且無時區問題
            now = discord.utils.utcnow()
            last_cooldown_str = user_info.get("work_cooldown")
            
            if last_cooldown_str:
                try:
                    cooldown_time = datetime.fromisoformat(last_cooldown_str)
                    # [Debug 修復 #2] 移除冗餘的 tzinfo 檢查
                    # 因為 discord.utils.utcnow() 是 Naive UTC，isoformat() 存檔的也是 Naive UTC
                    # 兩者直接比較即可，不需要替換 tzinfo (utcnow().tzinfo 本身就是 None)
                except Exception:
                    cooldown_time = None

                if cooldown_time and cooldown_time > now:
                    remaining = cooldown_time - now
                    minutes, seconds = divmod(int(remaining.total_seconds()), 60)
                    await ctx.respond(
                        embed=discord.Embed(
                            title="🌸 工作冷卻中",
                            description=f"幽幽子：你還需等待 {minutes} 分鐘 {seconds} 秒才能再次工作！",
                            color=discord.Color.orange()
                        ).set_footer(text=f"職業：{job_name}"),
                        ephemeral=True
                    )
                    return

            # 計算報酬
            reward = random.randint(job_data["min"], job_data["max"])

            # [Debug 修復] balance_lock 內只做記憶體操作
            async with self.data_manager.balance_lock:
                balance = self.data_manager.balance
                balance.setdefault(guild_id, {}).setdefault(user_id, 0.0)
                old_balance = balance[guild_id][user_id]
                balance[guild_id][user_id] += reward
                new_balance = balance[guild_id][user_id]

                # 扣除體力、更新冷卻時間 (全部在同一個鎖內，確保原子性)
                user_info["stamina"] -= stamina_cost
                user_info["work_cooldown"] = (now + timedelta(seconds=WORK_COOLDOWN_SECONDS)).isoformat()
                
                final_stamina = user_info["stamina"]

            # [Debug 修復] 鎖釋放後，統一呼叫 save_all_async 保存所有數據
            await self.data_manager.save_all_async()
            
            self.logger.info(
                f"💼 用戶 {user_id} 工作獲得 {reward} 幽靈幣，消耗 {stamina_cost} 體力"
                f"（餘額: {old_balance:.2f} → {new_balance:.2f}，體力: {current_stamina} → {final_stamina}）"
            )

            # 工作完成後嘗試信譽恢復
            credit_note = ""
            credit_cog = self.bot.get_cog("Credit")
            if credit_cog:
                try:
                    old_c, new_c, recovered = await credit_cog.recover_on_work(guild_id, user_id, job_name)
                    if recovered:
                        credit_note = f"\n💳 工作努力有回報！信譽 **+1** → **{new_c}/10**"
                except Exception as e:
                    self.logger.warning(f"⚠️ 信譽恢復失敗: {e}")

            embed = discord.Embed(
                title="🌸 工作成功！🌸",
                description=(
                    f"{ctx.user.mention} 作為 **{job_name}** "
                    f"賺取了 **{reward:,} 幽靈幣**！🎉\n"
                    f"當前餘額：**{new_balance:,.2f}** 幽靈幣\n"
                    f"當前體力：**{final_stamina}/{max_stamina}** (消耗 {stamina_cost})\n\n"
                    f"{random.choice(YUYUKO_WORK_QUOTES)}"
                    f"{credit_note}"
                ),
                color=discord.Color.from_rgb(205, 133, 232)
            ).set_footer(text="幽幽子：賞花、工作、吃點心三連發！")

            await ctx.respond(embed=embed, ephemeral=True)

        except Exception as e:
            self.logger.exception(f"work 指令錯誤: {e}")
            try:
                # [Debug 修復] 使用 Pycord 標準的 ctx.response.is_done()
                if not ctx.response.is_done():
                    await ctx.respond(
                        embed=discord.Embed(
                            title="🌸 工作系統錯誤",
                            description="執行工作時發生錯誤，請稍後再試或用 /feedback 回報幽幽子。",
                            color=discord.Color.red()
                        ).set_footer(text="幽幽子：冥界也會有小故障哦～"),
                        ephemeral=True
                    )
                else:
                    await ctx.followup.send("❌ 工作系統發生錯誤！", ephemeral=True)
            except Exception:
                pass


def setup(bot: discord.Bot):
    bot.add_cog(Work(bot))
    logger.info("Work Cog loaded successfully")
