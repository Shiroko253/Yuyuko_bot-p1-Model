import discord
from discord.ext import commands

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

def get_tax_rate(balance):
    """根據資產金額動態給予稅率，低資產低稅，高資產高稅"""
    if balance < 1000:
        return 0.05
    elif balance < 10000:
        return 0.10
    elif balance < 100000:
        return 0.20
    elif balance < 1000000:
        return 0.30
    else:
        return 0.40

class Tax(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(name="tax", description="幽幽子對伺服器用戶動態徵稅，存入國庫～")
    async def tax(self, ctx: discord.ApplicationContext):
        guild_id = str(ctx.guild.id)
        user_id = str(ctx.author.id)

        # 僅管理員可用
        if not ctx.author.guild_permissions.administrator:
            await ctx.respond(
                embed=discord.Embed(
                    title="🌸 權限不足！🌸",
                    description="只有管理員才能徵稅哦～",
                    color=discord.Color.red()
                ),
                ephemeral=True
            )
            return

        await ctx.defer()

        # 使用 DataManager 統一管理
        balance = ctx.bot.data_manager.load_json("economy/balance.json")
        server_config = ctx.bot.data_manager.load_json("economy/server_config.json")

        if not balance.get(guild_id):
            await ctx.followup.send(embed=discord.Embed(
                title="🌸 無人可稅！🌸",
                description="這個伺服器還沒有人有幽靈幣哦～快去玩遊戲賺錢吧！",
                color=discord.Color.red()
            ))
            return

        total_tax = 0
        taxed_users = []
        contributions = {}

        for taxed_user_id, user_balance in list(balance[guild_id].items()):
            if taxed_user_id == user_id:
                continue
            if user_balance <= 0:
                continue

            tax_rate = get_tax_rate(user_balance)
            tax_amount = round(user_balance * tax_rate, 2)
            new_balance = round(user_balance - tax_amount, 2)
            balance[guild_id][taxed_user_id] = new_balance
            total_tax += tax_amount

            # 紀錄每個用戶的貢獻
            contributions[taxed_user_id] = tax_amount

            try:
                user = await self.bot.fetch_user(int(taxed_user_id))
                display_name = getattr(user, "display_name", user.name)
            except discord.errors.NotFound:
                display_name = f"用戶ID: {taxed_user_id}"
            taxed_users.append(
                f"**{display_name}**（{format_number(user_balance)}→{format_number(new_balance)}）課稅{tax_rate*100:.0f}%：{format_number(tax_amount)} 幽靈幣"
            )

        if not taxed_users:
            await ctx.followup.send(embed=discord.Embed(
                title="🌸 無人可稅！🌸",
                description="沒有人有足夠的幽靈幣可以徵稅哦～",
                color=discord.Color.red()
            ))
            return

        if guild_id not in server_config:
            server_config[guild_id] = {}
        if "server_bank" not in server_config[guild_id]:
            server_config[guild_id]["server_bank"] = {
                "total": 0,
                "contributions": {}
            }

        server_config[guild_id]["server_bank"]["total"] += total_tax

        # 累加各用戶貢獻
        for taxed_user_id, tax_amount in contributions.items():
            if tax_amount <= 0:
                continue
            if taxed_user_id not in server_config[guild_id]["server_bank"]["contributions"]:
                server_config[guild_id]["server_bank"]["contributions"][taxed_user_id] = 0
            server_config[guild_id]["server_bank"]["contributions"][taxed_user_id] += tax_amount

        ctx.bot.data_manager.save_json("economy/balance.json", balance)
        ctx.bot.data_manager.save_json("economy/server_config.json", server_config)

        executor = ctx.author.display_name
        embed = discord.Embed(
            title="🌸 幽幽子的動態稅金徵收！🌸",
            description=(
                f"幽幽子對伺服器內所有用戶徵收動態稅金，存入國庫～\n"
                f"徵稅執行者：**{executor}**\n\n"
                f"被徵稅者：\n" + "\n".join(taxed_users) + f"\n\n"
                f"總稅金：{format_number(total_tax)} 幽靈幣\n"
                f"國庫當前餘額：{format_number(server_config[guild_id]['server_bank']['total'])} 幽靈幣"
            ),
            color=discord.Color.from_rgb(255, 182, 193)
        )
        await ctx.followup.send(embed=embed)

def setup(bot):
    bot.add_cog(Tax(bot))
