from decimal import Decimal, ROUND_DOWN
import discord
from discord.ext import commands
import logging
import os
import traceback

logger = logging.getLogger("SakuraBot.commands.addmoney")
AUTHOR_ID = int(os.getenv("AUTHOR_ID", 0))


def convert_decimal_to_float(data):
    """將 Decimal 轉換為 float 以便 JSON 序列化"""
    if isinstance(data, Decimal):
        return float(data.quantize(Decimal("0.01"), rounding=ROUND_DOWN))
    elif isinstance(data, dict):
        return {k: convert_decimal_to_float(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_decimal_to_float(i) for i in data]
    return data


def convert_float_to_decimal(data):
    """將 float/str 轉換為 Decimal 進行精確計算"""
    if isinstance(data, (float, str)):
        try:
            return Decimal(str(data))
        except Exception:
            return data
    elif isinstance(data, dict):
        return {k: convert_float_to_decimal(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_float_to_decimal(i) for i in data]
    return data


class EconomyAdmin(commands.Cog):
    """幽幽子的經濟系統管理指令"""
    
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @discord.slash_command(
        name="addmoney",
        description="給用戶增加幽靈幣（只有幽幽子的特定朋友可以用～）"
    )
    async def addmoney(
        self, 
        ctx: discord.ApplicationContext, 
        member: discord.Member, 
        amount: str
    ):
        """管理員添加金錢指令"""
        try:
            # 權限檢查
            if ctx.user.id != AUTHOR_ID:
                await ctx.respond(
                    "❌ 嗯？這個命令只有幽幽子特別信任的人才能用唷～", 
                    ephemeral=True
                )
                return

            # 檢查是否在伺服器中
            if not ctx.guild:
                await ctx.respond(
                    "❌ 這個命令只能在伺服器裡用唷～", 
                    ephemeral=True
                )
                return

            # 驗證金額格式
            try:
                amount_decimal = Decimal(amount)
                if amount_decimal <= 0:
                    raise ValueError("金額必須大於 0")
                amount_decimal = amount_decimal.quantize(Decimal("0.01"), rounding=ROUND_DOWN)
            except Exception:
                await ctx.respond(
                    "❌ 金額格式不對哦～請輸入正數（像 100 或 100.00 這樣）", 
                    ephemeral=True
                )
                return

            # 檢查 data_manager
            if not hasattr(self.bot, "data_manager"):
                await ctx.respond(
                    "❌ 幽幽子的錢包暫時找不到了，請稍後再試～", 
                    ephemeral=True
                )
                logger.error("data_manager 不存在")
                return

            data_manager = self.bot.data_manager
            
            # 防止給 Bot 自己加錢
            if member.id == self.bot.user.id:
                await ctx.respond(
                    "❌ 幽幽子自己可不需要幽靈幣呢～", 
                    ephemeral=True
                )
                return

            # 防止給 Bot 加錢
            if member.bot:
                await ctx.respond(
                    "❌ 機器人不需要幽靈幣啦～", 
                    ephemeral=True
                )
                return

            guild_id = str(ctx.guild.id)
            recipient_id = str(member.id)

            # 載入餘額數據
            user_balance = convert_float_to_decimal(data_manager.balance)

            # 確保伺服器數據存在
            if guild_id not in user_balance:
                user_balance[guild_id] = {}

            # 計算新餘額
            old_balance = user_balance[guild_id].get(recipient_id, Decimal("0"))
            new_balance = old_balance + amount_decimal
            user_balance[guild_id][recipient_id] = new_balance

            # 保存數據
            data_manager.balance = convert_decimal_to_float(user_balance)
            data_manager.save_all()

            # 構建回應 Embed
            embed = discord.Embed(
                title="💰 幽靈幣悄悄增加啦",
                description=(
                    f"{member.mention} 的錢包裡悄悄多了 **{amount_decimal:.2f} 幽靈幣**～\n\n"
                    f"**舊餘額:** {old_balance:.2f}\n"
                    f"**新餘額:** {new_balance:.2f}\n"
                    f"**增加:** +{amount_decimal:.2f}\n\n"
                    "幽幽子祝你使用愉快♪"
                ),
                color=discord.Color.purple()
            )
            embed.set_thumbnail(url=member.display_avatar.url)
            embed.set_footer(
                text="幽幽子的幽靈幣系統 · 美味又放心",
                icon_url=self.bot.user.avatar.url if self.bot.user.avatar else None
            )

            await ctx.respond(embed=embed)
            
            logger.info(
                f"管理員 {ctx.user} ({ctx.user.id}) 給 {member} ({member.id}) "
                f"增加了 {amount_decimal:.2f} 幽靈幣，新餘額: {new_balance:.2f}"
            )

        except Exception as e:
            logger.error(f"addmoney 指令執行錯誤: {e}\n{traceback.format_exc()}")
            await ctx.respond(
                "❌ 哎呀，幽幽子的系統有點小狀況，請稍後再來～", 
                ephemeral=True
            )

            # 發送錯誤報告給管理員
            if AUTHOR_ID and ctx.user.id != AUTHOR_ID:
                owner = self.bot.get_user(AUTHOR_ID)
                if owner:
                    try:
                        error_embed = discord.Embed(
                            title="🚨 AddMoney 錯誤報告",
                            description=f"```python\n{traceback.format_exc()[:1900]}\n```",
                            color=discord.Color.red()
                        )
                        error_embed.add_field(
                            name="觸發者",
                            value=f"{ctx.user.mention} ({ctx.user.id})"
                        )
                        error_embed.add_field(
                            name="目標",
                            value=f"{member.mention} ({member.id})"
                        )
                        error_embed.add_field(
                            name="金額",
                            value=amount
                        )
                        await owner.send(embed=error_embed)
                    except Exception:
                        pass

    @discord.slash_command(
        name="setmoney",
        description="設置用戶的幽靈幣數量（管理員專用）"
    )
    async def setmoney(
        self,
        ctx: discord.ApplicationContext,
        member: discord.Member,
        amount: str
    ):
        """設置用戶金錢（而非增加）"""
        try:
            # 權限檢查
            if ctx.user.id != AUTHOR_ID:
                await ctx.respond(
                    "❌ 此指令需要最高權限～", 
                    ephemeral=True
                )
                return

            if not ctx.guild:
                await ctx.respond(
                    "❌ 這個命令只能在伺服器裡用唷～", 
                    ephemeral=True
                )
                return

            # 驗證金額
            try:
                amount_decimal = Decimal(amount)
                if amount_decimal < 0:
                    raise ValueError("金額不能為負數")
                amount_decimal = amount_decimal.quantize(Decimal("0.01"), rounding=ROUND_DOWN)
            except Exception:
                await ctx.respond(
                    "❌ 金額格式錯誤，請輸入非負數", 
                    ephemeral=True
                )
                return

            if not hasattr(self.bot, "data_manager"):
                await ctx.respond("❌ 數據管理器不存在", ephemeral=True)
                return

            if member.bot:
                await ctx.respond("❌ 機器人不需要幽靈幣", ephemeral=True)
                return

            data_manager = self.bot.data_manager
            guild_id = str(ctx.guild.id)
            recipient_id = str(member.id)

            user_balance = convert_float_to_decimal(data_manager.balance)

            if guild_id not in user_balance:
                user_balance[guild_id] = {}

            old_balance = user_balance[guild_id].get(recipient_id, Decimal("0"))
            user_balance[guild_id][recipient_id] = amount_decimal

            data_manager.balance = convert_decimal_to_float(user_balance)
            data_manager.save_all()

            embed = discord.Embed(
                title="⚙️ 幽靈幣已設置",
                description=(
                    f"{member.mention} 的餘額已設置為 **{amount_decimal:.2f} 幽靈幣**\n\n"
                    f"**舊餘額:** {old_balance:.2f}\n"
                    f"**新餘額:** {amount_decimal:.2f}"
                ),
                color=discord.Color.blue()
            )
            embed.set_thumbnail(url=member.display_avatar.url)

            await ctx.respond(embed=embed)
            logger.info(
                f"管理員 {ctx.user} 將 {member} 的餘額設置為 {amount_decimal:.2f}"
            )

        except Exception as e:
            logger.error(f"setmoney 錯誤: {e}\n{traceback.format_exc()}")
            await ctx.respond("❌ 執行失敗", ephemeral=True)


def setup(bot: discord.Bot):
    bot.add_cog(EconomyAdmin(bot))
    logger.info("經濟系統管理模組已載入")
