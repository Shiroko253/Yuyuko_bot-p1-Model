from decimal import Decimal, ROUND_DOWN
import discord
from discord.ext import commands
import logging
import os

AUTHOR_ID = int(os.getenv("AUTHOR_ID", 0))

def convert_decimal_to_float(data):
    if isinstance(data, Decimal):
        return float(data.quantize(Decimal("0.01"), rounding=ROUND_DOWN))
    elif isinstance(data, dict):
        return {k: convert_decimal_to_float(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_decimal_to_float(i) for i in data]
    return data

def convert_float_to_decimal(data):
    if isinstance(data, float) or isinstance(data, str):
        try:
            return Decimal(str(data))
        except Exception:
            return data
    elif isinstance(data, dict):
        return {k: convert_float_to_decimal(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_float_to_decimal(i) for i in data]
    return data

class AddMoney(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @commands.slash_command(name="addmoney", description="给用户增加幽靈幣（特定用户专用）")
    async def addmoney(self, ctx: discord.ApplicationContext, member: discord.Member, amount: str):
        try:
            if ctx.user.id != AUTHOR_ID:
                await ctx.respond("❌ 您没有权限执行此操作。", ephemeral=True)
                return

            try:
                amount_decimal = Decimal(amount)
                if amount_decimal <= 0:
                    raise ValueError
                amount_decimal = amount_decimal.quantize(Decimal("0.01"), rounding=ROUND_DOWN)
            except Exception:
                await ctx.respond("❌ 金额格式无效，请输入正数金额（如 100 或 100.00）。", ephemeral=True)
                return

            if amount_decimal > Decimal("100000000000"):
                await ctx.respond("❌ 单次添加金额不能超过 **100,000,000,000 幽靈幣**。", ephemeral=True)
                return

            data_manager = self.bot.data_manager
            user_balance = data_manager.load_json(f"{data_manager.economy_dir}/balance.json")
            user_balance = convert_float_to_decimal(user_balance)

            guild_id = str(ctx.guild.id)
            recipient_id = str(member.id)

            if guild_id not in user_balance:
                user_balance[guild_id] = {}

            if recipient_id == str(self.bot.user.id):
                await ctx.respond("❌ 不能给机器人增加幽靈幣。", ephemeral=True)
                return

            old_balance = Decimal(user_balance[guild_id].get(recipient_id, 0))
            user_balance[guild_id][recipient_id] = old_balance + amount_decimal

            data_to_save = convert_decimal_to_float(user_balance)
            data_manager.save_json(f"{data_manager.economy_dir}/balance.json", data_to_save)

            embed = discord.Embed(
                title="✨ 幽靈幣增加成功",
                description=f"{member.mention} 已成功增加了 **{amount_decimal:.2f} 幽靈幣**。\n目前餘額：**{user_balance[guild_id][recipient_id]:.2f}**",
                color=discord.Color.green()
            )
            embed.set_footer(text="感谢使用幽靈幣系统")

            await ctx.respond(embed=embed)
            logging.info(f"管理员 {ctx.user.id} 给 {member.id} 增加了 {amount_decimal:.2f} 幽靈幣，当前余额：{user_balance[guild_id][recipient_id]:.2f}")

        except Exception as e:
            logging.error(f"addmoney 指令執行錯誤：{e}")
            await ctx.respond("❌ 执行命令时发生错误，请稍后再试。", ephemeral=True)

def setup(bot: discord.Bot):
    bot.add_cog(AddMoney(bot))