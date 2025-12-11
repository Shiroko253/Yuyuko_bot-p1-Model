import discord
from discord.ext import commands
import logging

logger = logging.getLogger("SakuraBot.Leaderboard")


class LeaderboardCog(commands.Cog):
    """
    🌸 幽幽子的靈魂排行榜 🌸
    櫻花樹下的財富與貢獻榜單,見證每個靈魂的努力與奉獻
    """
    
    def __init__(self, bot: discord.Bot):
        self.bot = bot
        self.data_manager = bot.data_manager
        logger.info("🌸 排行榜指令已於櫻花樹下甦醒")

    @discord.slash_command(
        name="leaderboard",
        description="🌸 查看幽靈幣餘額與金庫貢獻排行榜～櫻花下的榮耀時刻"
    )
    async def leaderboard(self, ctx: discord.ApplicationContext):
        """幽幽子展開櫻花卷軸,揭曉冥界的財富榜單"""
        
        # ----------- 頻道檢查 -----------
        if not ctx.guild:
            embed = discord.Embed(
                title="🌸 無法在此顯現榜單",
                description=(
                    "呼呼～排行榜只能在伺服器的櫻花樹下觀看哦!\n"
                    "請在伺服器頻道中使用此指令～"
                ),
                color=discord.Color.from_rgb(255, 182, 193)
            )
            embed.set_footer(text="請在伺服器中使用 · 幽幽子")
            await ctx.respond(embed=embed, ephemeral=True)
            return

        await ctx.defer()

        try:
            guild_id = str(ctx.guild.id)

            # ----------- 載入冥界記憶 -----------
            balance_data = self.data_manager._load_json("economy/balance.json", {})
            server_vault = self.data_manager._load_json("economy/server_vault.json", {})

            # ----------- 構建主 Embed -----------
            embed = discord.Embed(
                title="🌸 幽幽子的櫻花榜單 🌸",
                description=(
                    "在這櫻花飄落的冥界,讓我們見證靈魂們的財富與貢獻～\n"
                    "呼呼,誰會是今天的榜首呢?"
                ),
                color=discord.Color.from_rgb(255, 182, 193),
                timestamp=discord.utils.utcnow()
            )
            embed.set_thumbnail(
                url=self.bot.user.avatar.url if self.bot.user.avatar else None
            )

            # ----------- 幽靈幣餘額排行榜 -----------
            balance_field = await self._build_balance_leaderboard(guild_id, balance_data, ctx.guild)
            embed.add_field(
                name="💰 幽靈幣餘額排行榜",
                value=balance_field,
                inline=False
            )

            # ----------- 金庫貢獻排行榜 -----------
            contribution_field = await self._build_contribution_leaderboard(guild_id, server_vault, ctx.guild)
            embed.add_field(
                name="🏦 金庫貢獻排行榜",
                value=contribution_field,
                inline=False
            )

            embed.set_footer(
                text="✨ 排行榜僅顯示前 10 名 · 幽幽子在櫻花樹下守望著你們",
                icon_url=self.bot.user.avatar.url if self.bot.user.avatar else None
            )
            
            await ctx.followup.send(embed=embed)
            logger.info(f"📊 排行榜已為伺服器 {ctx.guild.name} ({guild_id}) 顯示")

        except Exception as e:
            logger.error(f"❌ 排行榜顯示失敗: {e}", exc_info=True)
            error_embed = discord.Embed(
                title="❌ 榜單顯現失敗",
                description=(
                    "哎呀,櫻花卷軸好像被風吹亂了...\n"
                    "請稍後再試或使用 `/feedback` 回報給幽幽子的主人～"
                ),
                color=discord.Color.dark_red()
            )
            error_embed.set_footer(text="術式受阻,請稍後重試 · 幽幽子")
            
            try:
                if not ctx.interaction.response.is_done():
                    await ctx.respond(embed=error_embed, ephemeral=True)
                else:
                    await ctx.followup.send(embed=error_embed, ephemeral=True)
            except Exception:
                logger.exception("❌ 無法發送排行榜錯誤訊息")

    async def _build_balance_leaderboard(
        self, 
        guild_id: str, 
        balance_data: dict, 
        guild: discord.Guild
    ) -> str:
        """構建幽靈幣餘額排行榜"""
        guild_balances = balance_data.get(guild_id, {})
        
        if not guild_balances:
            return (
                "```yaml\n"
                "🌸 榜單空無一物\n"
                "───────────────────\n"
                "目前還沒有任何靈魂擁有幽靈幣～\n"
                "快來賺取幽靈幣,和幽幽子一起賞櫻吧!\n"
                "```"
            )

        # 排序並取前10名
        sorted_balances = sorted(
            guild_balances.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:10]
        
        leaderboard_lines = []
        medals = ["🥇", "🥈", "🥉"]
        
        for index, (user_id, balance) in enumerate(sorted_balances, start=1):
            username = await self._get_username(user_id, guild)
            medal = medals[index - 1] if index <= 3 else f"**#{index}**"
            formatted_balance = self._format_number(balance)
            leaderboard_lines.append(
                f"{medal} {username}: `{formatted_balance}` 幽靈幣"
            )

        return "\n".join(leaderboard_lines) if leaderboard_lines else (
            "```\n榜單數據異常,請稍後再試。\n```"
        )

    async def _build_contribution_leaderboard(
        self, 
        guild_id: str, 
        server_vault: dict, 
        guild: discord.Guild
    ) -> str:
        """構建金庫貢獻排行榜"""
        guild_vault = server_vault.get(guild_id, {})
        contributions = guild_vault.get("vault", {}).get("contributions", {})
        
        if not contributions:
            return (
                "```yaml\n"
                "🌸 金庫尚未開放\n"
                "───────────────────\n"
                "金庫還沒有任何貢獻記錄～\n"
                "快去存錢或等待徵稅時刻吧!\n"
                "```"
            )

        # 排序並取前10名
        sorted_contributions = sorted(
            contributions.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:10]
        
        leaderboard_lines = []
        medals = ["🏆", "🎖️", "🎗️"]
        
        for index, (user_id, amount) in enumerate(sorted_contributions, start=1):
            username = await self._get_username(user_id, guild)
            medal = medals[index - 1] if index <= 3 else f"**#{index}**"
            formatted_amount = self._format_number(amount)
            leaderboard_lines.append(
                f"{medal} {username}: `{formatted_amount}` 幽靈幣"
            )

        return "\n".join(leaderboard_lines) if leaderboard_lines else (
            "```\n榜單數據異常,請稍後再試。\n```"
        )

    async def _get_username(self, user_id: str, guild: discord.Guild) -> str:
        """獲取用戶名稱,若失敗則返回靈魂代號"""
        try:
            # 優先從伺服器獲取成員
            member = guild.get_member(int(user_id))
            if member:
                return member.display_name
            
            # 嘗試從 Discord API 獲取用戶
            user = await self.bot.fetch_user(int(user_id))
            if user:
                return user.display_name
                
        except (discord.errors.NotFound, discord.errors.HTTPException, ValueError) as e:
            logger.debug(f"⚠️ 無法獲取用戶名 {user_id}: {e}")
        
        # 返回靈魂代號(後4碼ID)
        return f"靈魂_{user_id[-4:]}"

    @staticmethod
    def _format_number(num: float) -> str:
        """格式化大數字,如櫻花數量般清晰"""
        if num >= 1e20:
            return f"{num / 1e20:.2f} 兆京"
        elif num >= 1e16:
            return f"{num / 1e16:.2f} 京"
        elif num >= 1e12:
            return f"{num / 1e12:.2f} 兆"
        elif num >= 1e8:
            return f"{num / 1e8:.2f} 億"
        elif num >= 1e4:
            return f"{num / 1e4:.2f} 萬"
        else:
            return f"{num:,.0f}"  # 千位分隔符


def setup(bot: discord.Bot):
    """將排行榜術式註冊於幽幽子的靈魂"""
    bot.add_cog(LeaderboardCog(bot))
    logger.info("🌸 排行榜模組已於櫻花樹下綻放完成")
