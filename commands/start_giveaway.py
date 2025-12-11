import discord
from discord.ext import commands
from discord.ui import View, Button
import random
import logging
from datetime import datetime
from zoneinfo import ZoneInfo

logger = logging.getLogger("SakuraBot.Giveaway")

# 全局字典存儲活動中的抽獎
active_giveaways = {}


class GiveawayView(View):
    """
    🌸 幽幽子的冥界抽獎視圖 🌸
    櫻花樹下的幸運抽獎,讓靈魂們期待奇蹟的降臨
    """
    
    def __init__(self, bot: discord.Bot, guild_id: int, prize: str, duration: int, host_id: int, timeout: int = None):
        super().__init__(timeout=timeout)
        self.bot = bot
        self.guild_id = guild_id
        self.prize = prize
        self.duration = duration
        self.host_id = host_id
        self.participants = set()
        self.start_time = datetime.now(ZoneInfo('Asia/Taipei'))
        logger.info(f"🎁 抽獎活動已創建: {prize} (持續 {duration}秒)")

    async def on_timeout(self):
        """抽獎時間結束,自動開獎"""
        await self.end_giveaway()

    async def end_giveaway(self, forced_by: discord.Member = None):
        """結束抽獎並公布結果"""
        if self.guild_id not in active_giveaways:
            return

        giveaway_data = active_giveaways.pop(self.guild_id)
        channel = self.bot.get_channel(giveaway_data["channel_id"])
        
        if not channel:
            logger.warning(f"⚠️ 找不到抽獎頻道: {giveaway_data['channel_id']}")
            return

        # 沒有參加者
        if not self.participants:
            embed = discord.Embed(
                title="🌸 抽獎活動結束 🌸",
                description=(
                    f"**獎品**: {self.prize}\n"
                    f"**參加人數**: 0 人\n\n"
                    "哎呀～冥界今天沒有靈魂參與抽獎呢...\n"
                    "幽幽子有點寂寞,櫻花都黯然失色了～\n"
                    "下次一定要來參加哦!"
                ),
                color=discord.Color.from_rgb(169, 169, 169)  # 灰色
            )
            embed.set_footer(
                text="幽幽子：好想吃點心...",
                icon_url=self.bot.user.avatar.url if self.bot.user and self.bot.user.avatar else None
            )
            embed.timestamp = discord.utils.utcnow()
            
            await channel.send(embed=embed)
            logger.info(f"🎁 抽獎結束: {self.prize} - 無人參加")
            return

        # 隨機抽取幸運兒
        winner_id = random.choice(list(self.participants))
        winner = channel.guild.get_member(winner_id)
        winner_mention = winner.mention if winner else f"<@{winner_id}>"
        
        # 計算抽獎持續時間
        end_time = datetime.now(ZoneInfo('Asia/Taipei'))
        duration_actual = (end_time - self.start_time).total_seconds()

        # 結束原因
        end_reason = ""
        if forced_by:
            end_reason = f"\n*提前結束 by {forced_by.mention}*"
        
        # 中獎公告
        embed = discord.Embed(
            title="🎉 冥界抽獎結果公布 🎉",
            description=(
                f"**獎品**: {self.prize}\n"
                f"**參加人數**: {len(self.participants)} 人\n"
                f"**抽獎持續**: {int(duration_actual)} 秒\n\n"
                f"🌸 **幸運靈魂**: {winner_mention}\n\n"
                "恭喜你被櫻花選中!\n"
                "賞花、吃點心,亡魂也會幸福～{end_reason}"
            ),
            color=discord.Color.from_rgb(255, 215, 0)  # 金色
        )
        
        # 顯示所有參與者
        if len(self.participants) <= 10:
            participants_list = []
            for uid in self.participants:
                member = channel.guild.get_member(uid)
                if member:
                    participants_list.append(member.mention)
                else:
                    participants_list.append(f"<@{uid}>")
            
            embed.add_field(
                name="👥 參加者名單",
                value="\n".join(participants_list) if participants_list else "無",
                inline=False
            )
        else:
            embed.add_field(
                name="👥 參加者名單",
                value=f"共 {len(self.participants)} 人參加 (人數過多不顯示名單)",
                inline=False
            )
        
        embed.set_footer(
            text="幽幽子：感謝所有亡魂的參與～",
            icon_url=self.bot.user.avatar.url if self.bot.user and self.bot.user.avatar else None
        )
        embed.timestamp = discord.utils.utcnow()
        
        # 特別標記中獎者
        if winner:
            embed.set_thumbnail(url=winner.display_avatar.url)
        
        await channel.send(content=winner_mention, embed=embed)
        logger.info(f"🎁 抽獎結束: {self.prize} - 中獎者: {winner_id} - 參加人數: {len(self.participants)}")

    @discord.ui.button(
        label="參加抽獎", 
        style=discord.ButtonStyle.primary, 
        emoji="🌸",
        row=0
    )
    async def participate(self, button: Button, interaction: discord.Interaction):
        """參加抽獎按鈕"""
        user_id = interaction.user.id
        
        # 檢查是否已參加
        if user_id in self.participants:
            embed = discord.Embed(
                title="🌸 你已經參加了",
                description="你已經是冥界抽獎的參加者了!\n幽幽子都記得呢～耐心等待開獎吧!",
                color=discord.Color.orange()
            )
            embed.set_footer(text="每人只能參加一次哦 · 幽幽子")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # 添加參加者
        self.participants.add(user_id)
        
        embed = discord.Embed(
            title="✅ 參加成功!",
            description=(
                f"你已成為冥界抽獎的第 **{len(self.participants)}** 位參加者!\n\n"
                f"**獎品**: {self.prize}\n"
                f"**目前參加人數**: {len(self.participants)} 人\n\n"
                "祝你櫻花降臨,好運連連～"
            ),
            color=discord.Color.from_rgb(144, 238, 144)  # 淺綠色
        )
        embed.set_footer(
            text="幽幽子會公平抽獎的 · 幽幽子",
            icon_url=self.bot.user.avatar.url if self.bot.user and self.bot.user.avatar else None
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
        logger.info(f"👤 {interaction.user.name} 參加了抽獎 ({len(self.participants)} 人)")

    @discord.ui.button(
        label="查看參加者", 
        style=discord.ButtonStyle.secondary, 
        emoji="👥",
        row=0
    )
    async def view_participants(self, button: Button, interaction: discord.Interaction):
        """查看參加者列表"""
        if not self.participants:
            embed = discord.Embed(
                title="👥 參加者名單",
                description="目前還沒有人參加抽獎呢...\n快來成為第一個參加者吧!",
                color=discord.Color.light_gray()
            )
            embed.set_footer(text="空無一人的冥界 · 幽幽子")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        embed = discord.Embed(
            title="👥 冥界抽獎參加者名單",
            description=f"**獎品**: {self.prize}\n**參加人數**: {len(self.participants)} 人",
            color=discord.Color.from_rgb(205, 133, 232)
        )
        
        # 顯示參加者 (最多20人)
        participants_list = []
        for i, uid in enumerate(list(self.participants)[:20], 1):
            member = interaction.guild.get_member(uid)
            if member:
                participants_list.append(f"{i}. {member.mention} - `{member.name}`")
            else:
                participants_list.append(f"{i}. <@{uid}> - `未知用戶`")
        
        if participants_list:
            embed.add_field(
                name="📋 參加者",
                value="\n".join(participants_list),
                inline=False
            )
        
        if len(self.participants) > 20:
            embed.add_field(
                name="ℹ️ 提示",
                value=f"還有 {len(self.participants) - 20} 位參加者未顯示",
                inline=False
            )
        
        embed.set_footer(
            text="幽幽子會公平抽獎的 · 幽幽子",
            icon_url=self.bot.user.avatar.url if self.bot.user and self.bot.user.avatar else None
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(
        label="提前結束抽獎", 
        style=discord.ButtonStyle.danger, 
        emoji="🔚",
        row=1
    )
    async def end_giveaway_button(self, button: Button, interaction: discord.Interaction):
        """管理員提前結束抽獎"""
        # 檢查權限: 管理員或抽獎發起者
        if not (
            interaction.user.guild_permissions.administrator or 
            interaction.user.id == self.host_id
        ):
            embed = discord.Embed(
                title="❌ 權限不足",
                description="只有抽獎發起者或管理員才能提前結束抽獎哦～",
                color=discord.Color.red()
            )
            embed.set_footer(text="權限不足 · 幽幽子")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        # 確認結束
        embed = discord.Embed(
            title="🔔 抽獎活動已提前結束",
            description="幽幽子正在準備開獎結果...",
            color=discord.Color.orange()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
        # 結束抽獎
        await self.end_giveaway(forced_by=interaction.user)
        self.stop()  # 停止 View
        
        logger.info(f"🔔 {interaction.user.name} 提前結束了抽獎: {self.prize}")


class Giveaway(commands.Cog):
    """
    🌸 幽幽子的冥界抽獎系統 🌸
    在櫻花樹下舉辦抽獎活動,讓靈魂們共同期待幸運的降臨
    """
    
    def __init__(self, bot: discord.Bot):
        self.bot = bot
        logger.info("🎁 抽獎系統已於櫻花樹下甦醒")

    @discord.slash_command(
        name="start_giveaway",
        description="🌸 開啟幽幽子的冥界抽獎活動"
    )
    async def start_giveaway(
        self,
        ctx: discord.ApplicationContext,
        duration: int = discord.Option(
            int,
            description="抽獎持續時間（秒）",
            min_value=10,
            max_value=86400  # 最長24小時
        ),
        prize: str = discord.Option(
            str,
            description="獎品名稱",
            max_length=100
        )
    ):
        """
        開啟冥界抽獎活動
        
        參數:
        - duration: 抽獎持續時間 (10秒 ~ 24小時)
        - prize: 獎品名稱
        
        權限: 需要管理員權限
        """
        
        # 檢查權限
        if not ctx.user.guild_permissions.administrator:
            embed = discord.Embed(
                title="❌ 權限不足",
                description="你需要管理員權限才能開啟冥界抽獎哦～",
                color=discord.Color.red()
            )
            embed.set_footer(text="權限不足 · 幽幽子")
            await ctx.respond(embed=embed, ephemeral=True)
            return

        # 檢查是否已有活動進行中
        if ctx.guild.id in active_giveaways:
            existing = active_giveaways[ctx.guild.id]
            embed = discord.Embed(
                title="⚠️ 抽獎進行中",
                description=(
                    f"冥界已經有一場抽獎正在進行!\n\n"
                    f"**獎品**: {existing['prize']}\n"
                    f"**頻道**: <#{existing['channel_id']}>\n\n"
                    "請等待當前抽獎結束後再開啟新的抽獎～"
                ),
                color=discord.Color.orange()
            )
            embed.set_footer(text="一次只能進行一場抽獎 · 幽幽子")
            await ctx.respond(embed=embed, ephemeral=True)
            return

        # 格式化時間顯示
        if duration >= 3600:
            time_display = f"{duration // 3600} 小時 {(duration % 3600) // 60} 分鐘"
        elif duration >= 60:
            time_display = f"{duration // 60} 分鐘 {duration % 60} 秒"
        else:
            time_display = f"{duration} 秒"

        # 創建抽獎公告
        embed = discord.Embed(
            title="🎁 幽幽子的冥界抽獎開始啦! 🎁",
            description=(
                f"**獎品**: {prize}\n"
                f"**持續時間**: {time_display}\n"
                f"**發起者**: {ctx.user.mention}\n\n"
                "🌸 快來參加吧!\n"
                "幽幽子正在賞花等待幸運亡魂降臨～\n\n"
                "點擊下方「參加抽獎」按鈕即可參與!"
            ),
            color=discord.Color.from_rgb(205, 133, 232)
        )
        embed.add_field(
            name="📋 抽獎規則",
            value=(
                "• 每人只能參加一次\n"
                "• 時間結束後自動開獎\n"
                "• 隨機抽取一位幸運兒\n"
                "• 管理員可提前結束"
            ),
            inline=False
        )
        embed.set_footer(
            text="幽幽子：賞花、吃點心、抽獎三連發!祝大家好運～",
            icon_url=self.bot.user.avatar.url if self.bot.user and self.bot.user.avatar else None
        )
        embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else None)
        embed.timestamp = discord.utils.utcnow()

        # 創建抽獎視圖
        view = GiveawayView(
            self.bot, 
            ctx.guild.id, 
            prize, 
            duration,
            ctx.user.id,
            timeout=duration
        )

        # 發送抽獎訊息
        await ctx.respond(embed=embed, view=view)
        message = await ctx.interaction.original_response()

        # 記錄活動中的抽獎
        active_giveaways[ctx.guild.id] = {
            "message_id": message.id,
            "channel_id": ctx.channel_id,
            "prize": prize,
            "view": view,
            "host_id": ctx.user.id,
            "start_time": datetime.now(ZoneInfo('Asia/Taipei')).isoformat()
        }
        
        logger.info(
            f"🎁 {ctx.user.name} 開啟了抽獎: {prize} "
            f"(持續 {duration}秒, 頻道: {ctx.channel.name})"
        )

    @discord.slash_command(
        name="end_giveaway",
        description="🔚 強制結束當前進行中的抽獎活動"
    )
    async def force_end_giveaway(self, ctx: discord.ApplicationContext):
        """
        管理員強制結束抽獎
        
        權限: 需要管理員權限
        """
        
        # 檢查權限
        if not ctx.user.guild_permissions.administrator:
            embed = discord.Embed(
                title="❌ 權限不足",
                description="你需要管理員權限才能強制結束抽獎哦～",
                color=discord.Color.red()
            )
            await ctx.respond(embed=embed, ephemeral=True)
            return

        # 檢查是否有進行中的抽獎
        if ctx.guild.id not in active_giveaways:
            embed = discord.Embed(
                title="⚠️ 沒有進行中的抽獎",
                description="目前冥界沒有任何抽獎活動在進行呢～",
                color=discord.Color.orange()
            )
            await ctx.respond(embed=embed, ephemeral=True)
            return

        # 獲取並結束抽獎
        giveaway_data = active_giveaways[ctx.guild.id]
        view = giveaway_data["view"]
        
        embed = discord.Embed(
            title="🔔 正在結束抽獎...",
            description=f"幽幽子正在為 **{giveaway_data['prize']}** 的抽獎開獎...",
            color=discord.Color.gold()
        )
        await ctx.respond(embed=embed, ephemeral=True)
        
        # 結束抽獎
        await view.end_giveaway(forced_by=ctx.user)
        view.stop()
        
        logger.info(f"🔔 {ctx.user.name} 強制結束了抽獎: {giveaway_data['prize']}")


def setup(bot: discord.Bot):
    """將抽獎系統註冊於幽幽子的靈魂"""
    bot.add_cog(Giveaway(bot))
    logger.info("🎁 抽獎模組已於櫻花樹下綻放完成")
