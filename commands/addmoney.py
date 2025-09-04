from decimal import Decimal, ROUND_DOWN
import discord
from discord.ext import commands
import logging
import os
import traceback

# ～幽幽子溫柔提醒～：請在環境變數中設置 AUTHOR_ID，才不會讓可愛的幽靈幣亂飛哦
AUTHOR_ID = int(os.getenv("AUTHOR_ID", 0))

def convert_decimal_to_float(data):
    """
    將 Decimal 優雅地轉換為 float（幽幽子想讓數字看起來更可口～）
    """
    if isinstance(data, Decimal):
        return float(data.quantize(Decimal("0.01"), rounding=ROUND_DOWN))
    elif isinstance(data, dict):
        return {k: convert_decimal_to_float(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_decimal_to_float(i) for i in data]
    return data

def convert_float_to_decimal(data):
    """
    將 float 或 str 優雅地轉換為 Decimal（幽幽子要精確地數幽靈幣喔～）
    """
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
    """
    ✿ 幽幽子的撒幣指令 ✿
    您可以優雅地為伺服器的成員增加幽靈幣，只有特定人士能用哦～
    """

    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @discord.slash_command(
        name="addmoney",
        description="給用戶增加幽靈幣（只有幽幽子的特定朋友可以用～）"
    )
    async def addmoney(self, ctx: discord.ApplicationContext, member: discord.Member, amount: str):
        """
        又到發幽靈幣的美好時刻了～（只限特定用戶）
        """
        try:
            # 身份驗證：幽幽子只信任特別的人哦
            if ctx.user.id != AUTHOR_ID:
                await ctx.respond("❌ 嗯？這個命令只有幽幽子特別信任的人才能用唷～", ephemeral=True)
                return

            # 金額驗證：幽幽子不想看到奇怪的數字呢
            try:
                amount_decimal = Decimal(amount)
                if amount_decimal <= 0:
                    raise ValueError
                amount_decimal = amount_decimal.quantize(Decimal("0.01"), rounding=ROUND_DOWN)
            except Exception:
                await ctx.respond("❌ 金額格式不對哦～請輸入正數（像 100 或 100.00 這樣）", ephemeral=True)
                return

            # 上限控制：幽幽子覺得太多錢會膩
            MAX_AMOUNT = Decimal("100000000000")
            if amount_decimal > MAX_AMOUNT:
                await ctx.respond("❌ 喔喔，單次幽靈幣最多只能加 **100,000,000,000** 哦～再多幽幽子就吃不下啦。", ephemeral=True)
                return

            data_manager = getattr(self.bot, "data_manager", None)
            if not data_manager:
                await ctx.respond("❌ 幽幽子的錢包暫時找不到了，請稍後再試～", ephemeral=True)
                return

            user_balance = data_manager.load_json(f"{data_manager.economy_dir}/balance.json")
            user_balance = convert_float_to_decimal(user_balance)

            # 只允許在伺服器裡面使用
            if not ctx.guild:
                await ctx.respond("❌ 這個命令只能在伺服器裡用唷～", ephemeral=True)
                return

            guild_id = str(ctx.guild.id)
            recipient_id = str(member.id)

            # 初始化該伺服器的餘額資料
            if guild_id not in user_balance:
                user_balance[guild_id] = {}

            # 不可給機器人加錢
            if recipient_id == str(self.bot.user.id):
                await ctx.respond("❌ 幽幽子自己可不需要幽靈幣呢～", ephemeral=True)
                return

            # 計算新餘額
            old_balance = Decimal(user_balance[guild_id].get(recipient_id, 0))
            new_balance = old_balance + amount_decimal
            user_balance[guild_id][recipient_id] = new_balance

            # 儲存最新餘額
            data_to_save = convert_decimal_to_float(user_balance)
            data_manager.save_json(f"{data_manager.economy_dir}/balance.json", data_to_save)

            # 幽幽子風格 embed
            embed = discord.Embed(
                title="🍡 幽靈幣悄悄增加啦",
                description=(
                    f"{member.mention} 的錢包裡悄悄多了 **{amount_decimal:.2f} 幽靈幣**～\n"
                    f"現在總餘額是：**{new_balance:.2f}**\n"
                    "幽幽子祝你使用愉快♪"
                ),
                color=discord.Color.purple()
            )
            embed.set_footer(text="幽幽子的幽靈幣系統・美味又放心")

            await ctx.respond(embed=embed)
            logging.info(
                f"幽幽子管理員 {ctx.user.id} 給 {member.id} 增加了 {amount_decimal:.2f} 幽靈幣，"
                f"現在餘額：{new_balance:.2f}"
            )

        except Exception as e:
            # 錯誤處理：幽幽子貼心地記錄錯誤，並悄悄通知主人
            logging.error(f"addmoney 指令執行錯誤：{e}\n{traceback.format_exc()}")
            await ctx.respond("❌ 哎呀，幽幽子的系統有點小狀況，請稍後再來～", ephemeral=True)

            # 如果是作者本人，幽幽子會貼心地發送詳細訊息
            if AUTHOR_ID and ctx.user.id != AUTHOR_ID:
                owner = self.bot.get_user(AUTHOR_ID)
                if owner:
                    try:
                        await owner.send(
                            f"幽幽子的 addmoney debug error：\n```\n{traceback.format_exc()}\n```"
                        )
                    except Exception:
                        pass

def setup(bot: discord.Bot):
    """
    ✿ 幽幽子優雅地將撒幣功能裝進 bot 裡 ✿
    """
    bot.add_cog(AddMoney(bot))