from decimal import Decimal, ROUND_DOWN
import discord
from discord.ext import commands
import logging
import os
import traceback
from typing import Dict, Any, Union
from datetime import datetime  # 添加這個 import

AUTHOR_ID = int(os.getenv("AUTHOR_ID", 0))

def convert_decimal_to_float(data: Any) -> Any:
    """
    將 Decimal 轉換為 float（保留2位小數）
    """
    if isinstance(data, Decimal):
        return float(data.quantize(Decimal("0.01"), rounding=ROUND_DOWN))
    elif isinstance(data, dict):
        return {k: convert_decimal_to_float(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_decimal_to_float(i) for i in data]
    return data

def convert_float_to_decimal(data: Any) -> Any:
    """
    將 float 轉換為 Decimal
    """
    if isinstance(data, (float, int)) or isinstance(data, str):
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
    """幽靈幣管理系統 - 只有特定管理員可以使用"""
    
    def __init__(self, bot: discord.Bot):
        self.bot = bot
        self.logger = logging.getLogger("SakuraBot.commands.addmoney")

    def _validate_amount(self, amount_str: str) -> Union[Decimal, str]:
        """
        驗證金額格式
        返回 Decimal 或錯誤訊息
        """
        try:
            amount_decimal = Decimal(amount_str)
            if amount_decimal <= 0:
                return "金額必須大於0"
            if amount_decimal > Decimal("999999999999"):  # 防止過大數值
                return "金額過大，請輸入合理範圍內的數值"
            return amount_decimal.quantize(Decimal("0.01"), rounding=ROUND_DOWN)
        except Exception:
            return "金額格式不正確"

    def _get_balance_data(self) -> Dict[str, Dict[str, Decimal]]:
        """獲取餘額資料"""
        data_manager = getattr(self.bot, "data_manager", None)
        if not data_manager:
            raise Exception("資料管理器未初始化")
        
        # 使用 data_manager._load_json 靜態方法
        user_balance = data_manager._load_json(f"{data_manager.economy_dir}/balance.json")
        return convert_float_to_decimal(user_balance)

    def _save_balance_data(self, balance_data: Dict[str, Dict[str, Decimal]]) -> None:
        """保存餘額資料"""
        data_manager = getattr(self.bot, "data_manager", None)
        if not data_manager:
            raise Exception("資料管理器未初始化")
        
        data_to_save = convert_decimal_to_float(balance_data)
        # 使用 data_manager._save_json 靜態方法
        data_manager._save_json(f"{data_manager.economy_dir}/balance.json", data_to_save)

    @discord.slash_command(
        name="addmoney",
        description="給用戶增加幽靈幣（只有幽幽子的特定朋友可以用～）",
        guild_ids=None  # 全伺服器可用
    )
    async def addmoney(
        self, 
        ctx: discord.ApplicationContext, 
        member: discord.Member, 
        amount: float  # 修正：直接使用 float 參數
    ) -> None:
        """給用戶增加幽靈幣的管理指令"""
        try:
            # 權限檢查
            if ctx.user.id != AUTHOR_ID:
                embed = discord.Embed(
                    title="🔒 權限不足",
                    description="❌ 嗯？這個命令只有幽幽子特別信任的人才能用唷～",
                    color=discord.Color.red()
                )
                await ctx.respond(embed=embed, ephemeral=True)
                return

            # 驗證金額
            amount_decimal = self._validate_amount(str(amount))
            if isinstance(amount_decimal, str):  # 錯誤訊息
                embed = discord.Embed(
                    title="⚠️ 格式錯誤",
                    description=f"❌ {amount_decimal}，請輸入正數（像 100 或 100.00 這樣）",
                    color=discord.Color.red()
                )
                await ctx.respond(embed=embed, ephemeral=True)
                return

            # 檢查資料管理器
            data_manager = getattr(self.bot, "data_manager", None)
            if not data_manager:
                embed = discord.Embed(
                    title="🔧 系統錯誤",
                    description="❌ 幽幽子的錢包暫時找不到了，請稍後再試～",
                    color=discord.Color.red()
                )
                await ctx.respond(embed=embed, ephemeral=True)
                return

            # 檢查伺服器環境
            if not ctx.guild:
                embed = discord.Embed(
                    title="🏢 伺服器限制",
                    description="❌ 這個命令只能在伺服器裡用唷～",
                    color=discord.Color.orange()
                )
                await ctx.respond(embed=embed, ephemeral=True)
                return

            # 獲取並更新餘額
            try:
                user_balance = self._get_balance_data()
            except Exception as e:
                self.logger.error(f"讀取餘額資料失敗：{e}")
                embed = discord.Embed(
                    title="💾 讀取錯誤",
                    description="❌ 幽靈幣增加失敗，請稍後再試～",
                    color=discord.Color.red()
                )
                await ctx.respond(embed=embed, ephemeral=True)
                return

            guild_id = str(ctx.guild.id)
            recipient_id = str(member.id)

            # 初始化伺服器資料
            if guild_id not in user_balance:
                user_balance[guild_id] = {}

            # 防止給自己加幣
            if recipient_id == str(self.bot.user.id):
                embed = discord.Embed(
                    title="👻 自己人",
                    description="❌ 幽幽子自己可不需要幽靈幣呢～",
                    color=discord.Color.orange()
                )
                await ctx.respond(embed=embed, ephemeral=True)
                return

            # 更新餘額
            old_balance = Decimal(user_balance[guild_id].get(recipient_id, 0))
            new_balance = old_balance + amount_decimal
            user_balance[guild_id][recipient_id] = new_balance

            # 保存資料
            try:
                self._save_balance_data(user_balance)
            except Exception as e:
                self.logger.error(f"保存餘額資料失敗：{e}")
                embed = discord.Embed(
                    title="💾 保存錯誤",
                    description="❌ 幽靈幣增加成功，但資料保存失敗，請聯繫管理員～",
                    color=discord.Color.orange()
                )
                await ctx.respond(embed=embed, ephemeral=True)
                return

            # 發送成功訊息
            embed = discord.Embed(
                title="🍡 幽靈幣成功增加！",
                description=(
                    f"🎯 **目標用戶：** {member.mention}\n"
                    f"💰 **增加金額：** `+{amount_decimal:.2f}` 幽靈幣\n"
                    f"💳 **新餘額：** `{new_balance:.2f}` 幽靈幣\n\n"
                    f"✨ 由 **{ctx.user.display_name}** 操作完成"
                ),
                color=discord.Color.green()
            )
            embed.set_thumbnail(url=member.display_avatar.url if member.display_avatar else self.bot.user.display_avatar.url)
            embed.set_footer(
                text=f"幽幽子的幽靈幣系統 | 操作時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",  # 修復：使用 datetime.now()
                icon_url=self.bot.user.display_avatar.url
            )

            await ctx.respond(embed=embed)
            
            # 記錄日誌
            self.logger.info(
                f"管理員 {ctx.user} ({ctx.user.id}) 給 {member} ({member.id}) "
                f"增加 {amount_decimal:.2f} 幽靈幣，新餘額：{new_balance:.2f}"
            )

        except commands.CommandOnCooldown:
            embed = discord.Embed(
                title="⏱️ 冷卻中",
                description="❌ 這個命令正在冷卻中，請稍後再試～",
                color=discord.Color.orange()
            )
            await ctx.respond(embed=embed, ephemeral=True)
            
        except commands.CommandError as e:
            embed = discord.Embed(
                title="❌ 指令錯誤",
                description=f"指令執行發生錯誤：{str(e)}",
                color=discord.Color.red()
            )
            await ctx.respond(embed=embed, ephemeral=True)
            
        except Exception as e:
            self.logger.error(f"addmoney 指令執行錯誤：{e}\n{traceback.format_exc()}")
            
            embed = discord.Embed(
                title="🔧 系統錯誤",
                description="❌ 哎呀，幽幽子的系統有點小狀況，請稍後再來～",
                color=discord.Color.red()
            )
            await ctx.respond(embed=embed, ephemeral=True)

            # 通知開發者
            if AUTHOR_ID and ctx.user.id != AUTHOR_ID:
                owner = self.bot.get_user(AUTHOR_ID)
                if owner:
                    try:
                        error_embed = discord.Embed(
                            title="🐛 錯誤報告",
                            description=f"```py\n{traceback.format_exc()}\n```",
                            color=discord.Color.red()
                        )
                        error_embed.add_field(
                            name="錯誤時間",
                            value=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # 修復：使用 datetime.now()
                            inline=False
                        )
                        await owner.send(embed=error_embed)
                    except Exception as dm_error:
                        self.logger.error(f"發送錯誤通知失敗：{dm_error}")

def setup(bot: discord.Bot) -> None:
    """註冊 AddMoney 模組"""
    bot.add_cog(AddMoney(bot))
    logging.getLogger("SakuraBot.commands.addmoney").info("幽靈幣管理模組已載入")
