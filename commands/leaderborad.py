import discord
from discord.ext import commands
import json

class LeaderboardCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(name="leaderboard", description="查看幽靈幣餘額和金庫貢獻排行榜～")
    async def leaderboard(self, ctx: discord.ApplicationContext):
        guild_id = str(ctx.guild.id)

        # 讀取正確資料路徑
        data_manager = getattr(ctx.bot, "data_manager", None)
        if data_manager:
            balance_data = data_manager.load_json("economy/balance.json", default={})
            server_config = data_manager.load_json("config/server_config.json", default={})
        else:
            def load_json(file):
                try:
                    with open(file, "r", encoding="utf-8") as f:
                        return json.load(f)
                except (FileNotFoundError, json.JSONDecodeError):
                    return {}
            balance_data = load_json("economy/balance.json")
            server_config = load_json("config/server_config.json")

        def format_number(num):
            if num >= 1e20:
                return f"{num / 1e20:.2f} 兆京"
            elif num >= 1e16:
                return f"{num / 1e16:.2f} 京"
            elif num >= 1e12:
                return f"{num / 1e12:.2f} 兆"
            elif num >= 1e8:
                return f"{num / 1e8:.2f} 億"
            else:
                return f"{num:.2f}"

        if not ctx.guild:
            await ctx.respond("此命令只能在伺服器中使用。", ephemeral=True)
            return

        await ctx.defer()

        embed = discord.Embed(
            title="🏆 幽幽子的排行榜 🏆",
            color=discord.Color.from_rgb(255, 182, 193)
        )

        # --- 幽靈幣餘額排行榜 ---
        guild_balances = balance_data.get(guild_id, {})
        if not guild_balances:
            embed.add_field(
                name="🌸 幽靈幣餘額排行榜 🌸",
                value="目前沒有餘額排行榜數據哦～快去賺取幽靈幣吧！",
                inline=False
            )
        else:
            sorted_balances = sorted(guild_balances.items(), key=lambda x: x[1], reverse=True)
            balance_leaderboard = []
            for index, (user_id, balance) in enumerate(sorted_balances[:10], start=1):
                username = f"用戶ID: {user_id}"
                member = ctx.guild.get_member(int(user_id))
                if member:
                    username = member.display_name
                else:
                    try:
                        user = await self.bot.fetch_user(int(user_id))
                        if user:
                            username = user.display_name
                    except Exception:
                        pass
                balance_leaderboard.append(f"**#{index}** - {username}: {format_number(balance)} 幽靈幣")
            balance_message = "\n".join(balance_leaderboard) if balance_leaderboard else "排行榜數據為空。"
            embed.add_field(
                name="🌸 幽靈幣餘額排行榜 🌸",
                value=balance_message,
                inline=False
            )

        # --- 金庫貢獻排行榜 ---
        server_info = server_config.get(guild_id, {})
        contributions = server_info.get("server_bank", {}).get("contributions", {})
        if not contributions:
            embed.add_field(
                name="🌸 金庫貢獻排行榜 🌸",
                value="金庫還沒有任何貢獻哦～快去存錢或被徵稅吧！",
                inline=False
            )
        else:
            sorted_contributions = sorted(contributions.items(), key=lambda x: x[1], reverse=True)
            contribution_leaderboard = []
            for index, (user_id, amount) in enumerate(sorted_contributions[:10], start=1):
                username = f"用戶ID: {user_id}"
                member = ctx.guild.get_member(int(user_id))
                if member:
                    username = member.display_name
                else:
                    try:
                        user = await self.bot.fetch_user(int(user_id))
                        if user:
                            username = user.display_name
                    except Exception:
                        pass
                contribution_leaderboard.append(f"**#{index}** - {username}: {format_number(amount)} 幽靈幣")
            contribution_message = "\n".join(contribution_leaderboard) if contribution_leaderboard else "排行榜數據為空。"
            embed.add_field(
                name="🌸 金庫貢獻排行榜 🌸",
                value=contribution_message,
                inline=False
            )

        embed.set_footer(text="排行榜僅顯示前 10 名")
        await ctx.followup.send(embed=embed)

def setup(bot):
    bot.add_cog(LeaderboardCog(bot))
