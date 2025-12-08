import discord
from discord.ext import commands
import logging

logger = logging.getLogger("SakuraBot.Leaderboard")


class LeaderboardCog(commands.Cog):
    """
    🌸 幽幽子的靈魂排行榜 🌸
    櫻花樹下的財富與貢獻榜單,見證每個靈魂的努力與奉獻
    """
    
    def __init__(self, bot):
        self.bot = bot
        logger.info("🌸 排行榜指令已甦醒")

    @discord.slash_command(
        name="leaderboard",
        description="查看幽靈幣餘額與金庫貢獻排行榜～櫻花下的榮耀時刻"
    )
    async def leaderboard(self, ctx: discord.ApplicationContext):
        """幽幽子展開櫻花卷軸,揭曉冥界的財富榜單"""
        
        # === 頻道檢查 ===
        if not ctx.guild:
            await ctx.respond(
                embed=self._create_embed(
                    title="🌸 無法在此顯現榜單",
                    description="排行榜只能在伺服器的櫻花樹下觀看哦～\n請在伺服器頻道中使用此指令。",
                    color=discord.Color.pink()
                ),
                ephemeral=True
            )
            return

        await ctx.defer()

        guild_id = str(ctx.guild.id)
        data_manager = getattr(self.bot, "data_manager", None)

        # === 載入數據 ===
        if data_manager:
            balance_data = data_manager.balance or {}
            server_config = data_manager._load_json("config/server_config.json", default={})
        else:
            logger.warning("⚠️ 未找到 data_manager,使用備用載入方式")
            balance_data = self._fallback_load_json("economy/balance.json")
            server_config = self._fallback_load_json("config/server_config.json")

        # === 構建主 Embed ===
        embed = discord.Embed(
            title="🌸 幽幽子的櫻花榜單 🌸",
            description="在這櫻花飄落的冥界,讓我們見證靈魂們的財富與貢獻～",
            color=discord.Color.from_rgb(255, 182, 193),
            timestamp=discord.utils.utcnow()
        )
        embed.set_thumbnail(url=self.bot.user.avatar.url if self.bot.user.avatar else None)

        # === 幽靈幣餘額排行榜 ===
        balance_field = await self._build_balance_leaderboard(guild_id, balance_data, ctx.guild)
        embed.add_field(
            name="💰 幽靈幣餘額排行榜",
            value=balance_field,
            inline=False
        )

        # === 金庫貢獻排行榜 ===
        contribution_field = await self._build_contribution_leaderboard(guild_id, server_config, ctx.guild)
        embed.add_field(
            name="🏦 金庫貢獻排行榜",
            value=contribution_field,
            inline=False
        )

        embed.set_footer(text="✨ 排行榜僅顯示前 10 名 · 幽幽子在櫻花樹下守望著你們")
        
        await ctx.followup.send(embed=embed)
        logger.info(f"📊 排行榜已為伺服器 {ctx.guild.name} 顯示")

    async def _build_balance_leaderboard(self, guild_id: str, balance_data: dict, guild: discord.Guild) -> str:
        """構建幽靈幣餘額排行榜"""
        guild_balances = balance_data.get(guild_id, {})
        
        if not guild_balances:
            return (
                "```\n"
                "🌸 榜單空無一物\n"
                "───────────────────\n"
                "目前還沒有任何靈魂擁有幽靈幣～\n"
                "快來賺取幽靈幣,和幽幽子一起賞櫻吧！\n"
                "```"
            )

        sorted_balances = sorted(guild_balances.items(), key=lambda x: x[1], reverse=True)[:10]
        leaderboard_lines = []
        
        medals = ["🥇", "🥈", "🥉"]
        
        for index, (user_id, balance) in enumerate(sorted_balances, start=1):
            username = await self._get_username(user_id, guild)
            medal = medals[index - 1] if index <= 3 else f"**#{index}**"
            formatted_balance = self._format_number(balance)
            leaderboard_lines.append(f"{medal} {username}: `{formatted_balance}` 幽靈幣")

        return "\n".join(leaderboard_lines) if leaderboard_lines else "榜單數據異常,請稍後再試。"

    async def _build_contribution_leaderboard(self, guild_id: str, server_config: dict, guild: discord.Guild) -> str:
        """構建金庫貢獻排行榜"""
        server_info = server_config.get(guild_id, {})
        contributions = server_info.get("server_bank", {}).get("contributions", {})
        
        if not contributions:
            return (
                "```\n"
                "🌸 金庫尚未開放\n"
                "───────────────────\n"
                "金庫還沒有任何貢獻記錄～\n"
                "快去存錢或等待徵稅時刻吧！\n"
                "```"
            )

        sorted_contributions = sorted(contributions.items(), key=lambda x: x[1], reverse=True)[:10]
        leaderboard_lines = []
        
        medals = ["🏆", "🎖️", "🎗️"]
        
        for index, (user_id, amount) in enumerate(sorted_contributions, start=1):
            username = await self._get_username(user_id, guild)
            medal = medals[index - 1] if index <= 3 else f"**#{index}**"
            formatted_amount = self._format_number(amount)
            leaderboard_lines.append(f"{medal} {username}: `{formatted_amount}` 幽靈幣")

        return "\n".join(leaderboard_lines) if leaderboard_lines else "榜單數據異常,請稍後再試。"

    async def _get_username(self, user_id: str, guild: discord.Guild) -> str:
        """獲取用戶名稱,若失敗則返回 ID"""
        try:
            # 優先從伺服器獲取
            member = guild.get_member(int(user_id))
            if member:
                return member.display_name
            
            # 嘗試從 Discord API 獲取
            user = await self.bot.fetch_user(int(user_id))
            if user:
                return user.display_name
                
        except Exception as e:
            logger.debug(f"無法獲取用戶名 {user_id}: {e}")
        
        return f"靈魂_{user_id[-4:]}"  # 顯示後4碼ID

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

    @staticmethod
    def _fallback_load_json(file_path: str) -> dict:
        """備用的 JSON 載入方法"""
        try:
            import json
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f) or {}
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.warning(f"⚠️ 備用載入失敗 {file_path}: {e}")
            return {}

    @staticmethod
    def _create_embed(title: str, description: str, color: discord.Color) -> discord.Embed:
        """創建統一風格的 Embed"""
        return discord.Embed(
            title=title,
            description=description,
            color=color,
            timestamp=discord.utils.utcnow()
        )


def setup(bot):
    bot.add_cog(LeaderboardCog(bot))
    logger.info("✨ 排行榜 Cog 已載入完成")
