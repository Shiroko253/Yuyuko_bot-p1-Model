import os
import logging
from decimal import Decimal, ROUND_DOWN, InvalidOperation
import discord
from discord.ext import commands

# ----------- 冥界守護者的印記 -----------
AUTHOR_ID = int(os.getenv("AUTHOR_ID", 0))
logger = logging.getLogger("SakuraBot.RemoveMoney")


class RemoveMoney(commands.Cog):
    """
    🌸 收回幽靈幣的冥界之力 🌸
    只有幽幽子的主人可使用此術式,
    讓飄散的幽靈幣重新歸於冥界花園～
    """
    
    def __init__(self, bot: discord.Bot):
        self.bot = bot
        self.data_manager = bot.data_manager
        logger.info("🌸 幽靈幣收回術式已於櫻花樹下甦醒")

    @discord.slash_command(
        name="removemoney",
        description="🌸 收回用戶的幽靈幣(僅限冥界主人使用)"
    )
    async def removemoney(
        self, 
        ctx: discord.ApplicationContext, 
        member: discord.Member, 
        amount: str
    ):
        """
        從指定靈魂處收回幽靈幣,猶如櫻花瓣隨風而逝
        
        此術式將幽靈幣從凡間收回冥界,
        只有幽幽子的主人才能施展此等神力～
        """
        try:
            # ----------- 驗證冥界主人的身份 -----------
            if ctx.user.id != AUTHOR_ID:
                embed = discord.Embed(
                    title="❌ 冥界之力受阻",
                    description=(
                        "呀啦呀啦～只有幽幽子的主人才能使用此術式呢!\n"
                        "這可是能操控幽靈幣流動的神聖之力哦～"
                    ),
                    color=discord.Color.dark_purple()
                )
                embed.set_footer(
                    text="冥界之力不可輕易動用 · 幽幽子",
                    icon_url=self.bot.user.avatar.url if self.bot.user.avatar else None
                )
                await ctx.respond(embed=embed, ephemeral=True)
                return

            # ----------- 解析金額,如櫻瓣數量般精確 -----------
            try:
                amount_decimal = Decimal(amount)
                if amount_decimal <= 0:
                    raise ValueError("金額必須為正數")
                # 四捨五入至小數點後兩位
                amount_decimal = amount_decimal.quantize(
                    Decimal("0.01"), 
                    rounding=ROUND_DOWN
                )
            except (InvalidOperation, ValueError) as e:
                embed = discord.Embed(
                    title="❌ 術式施展失敗",
                    description=(
                        "哎呀,金額好像不太對呢～\n"
                        "請輸入正數金額,比如 `100` 或 `100.50` 這樣!"
                    ),
                    color=discord.Color.red()
                )
                embed.set_footer(text="請檢查金額格式 · 幽幽子")
                await ctx.respond(embed=embed, ephemeral=True)
                logger.warning(f"⚠️ 無效金額格式: {amount}, 錯誤: {e}")
                return

            # ----------- 防止對機器人施術 -----------
            if member.id == self.bot.user.id:
                embed = discord.Embed(
                    title="🌸 術式無效",
                    description=(
                        "呼呼～幽幽子可不能從自己身上收回幽靈幣呢!\n"
                        "這樣冥界的秩序就會亂掉了～"
                    ),
                    color=discord.Color.gold()
                )
                embed.set_thumbnail(url=self.bot.user.avatar.url if self.bot.user.avatar else None)
                await ctx.respond(embed=embed, ephemeral=True)
                return

            guild_id = str(ctx.guild.id)
            recipient_id = str(member.id)

            # ----------- 執行收回術式 -----------
            async with self.data_manager.balance_lock:
                # 讀取當前餘額
                if guild_id not in self.data_manager.balance:
                    self.data_manager.balance[guild_id] = {}
                if recipient_id not in self.data_manager.balance[guild_id]:
                    self.data_manager.balance[guild_id][recipient_id] = 0.0
                
                current_balance = Decimal(
                    str(self.data_manager.balance[guild_id][recipient_id])
                )
                
                # 計算新餘額(不能為負數)
                new_balance = max(current_balance - amount_decimal, Decimal("0.00"))
                
                # 更新餘額
                self.data_manager.balance[guild_id][recipient_id] = float(new_balance)
                
                # 保存到檔案
                await self.data_manager.save_all_async()

            # ----------- 計算實際收回的金額 -----------
            actual_removed = current_balance - new_balance

            # ----------- 靈魂回應 -----------
            embed = discord.Embed(
                title="🌸 幽靈幣已隨櫻花瓣飄散",
                description=(
                    f"呼呼～幽靈幣已從 {member.mention} 處收回了!\n"
                    f"它們將重新回到冥界花園,化作櫻花的養分～"
                ),
                color=discord.Color.from_rgb(255, 182, 193)
            )
            embed.add_field(
                name="💰 收回詳情",
                value=(
                    f"```yaml\n"
                    f"原有餘額: {current_balance:.2f} 幽靈幣\n"
                    f"收回金額: {actual_removed:.2f} 幽靈幣\n"
                    f"剩餘餘額: {new_balance:.2f} 幽靈幣\n"
                    f"```"
                ),
                inline=False
            )
            embed.set_footer(
                text="幽靈幣已歸於冥界 · 幽幽子",
                icon_url=self.bot.user.avatar.url if self.bot.user.avatar else None
            )
            embed.set_thumbnail(url=member.display_avatar.url)

            await ctx.respond(embed=embed)

            # ----------- 記錄於冥界卷軸 -----------
            logger.info(
                f"💸 冥界主人 {ctx.user.name}({ctx.user.id}) "
                f"從 {member.name}({member.id}) 收回 {actual_removed:.2f} 幽靈幣, "
                f"餘額: {current_balance:.2f} → {new_balance:.2f}"
            )

            # ----------- 若金額不足,額外提醒 -----------
            if actual_removed < amount_decimal:
                warning_embed = discord.Embed(
                    title="⚠️ 注意事項",
                    description=(
                        f"呀啦呀啦～這位靈魂的餘額不足 {amount_decimal:.2f} 幽靈幣呢!\n"
                        f"實際只收回了 **{actual_removed:.2f}** 幽靈幣,\n"
                        f"剩下的就當作是幽幽子的慈悲吧～"
                    ),
                    color=discord.Color.orange()
                )
                warning_embed.set_footer(text="櫻花飄落,慈悲為懷 · 幽幽子")
                await ctx.followup.send(embed=warning_embed, ephemeral=True)

        except Exception as e:
            logger.error(f"❌ 收回幽靈幣時發生異常: {e}", exc_info=True)
            embed = discord.Embed(
                title="❌ 冥界術式崩壞",
                description=(
                    "哎呀,執行術式時遭遇了不明之力...\n"
                    "請稍候再試,或使用 `/feedback` 告知幽幽子的主人～"
                ),
                color=discord.Color.dark_red()
            )
            embed.set_footer(text="術式受阻,請稍後重試 · 幽幽子")
            
            # 安全處理回應
            try:
                if not ctx.interaction.response.is_done():
                    await ctx.respond(embed=embed, ephemeral=True)
                else:
                    await ctx.followup.send(embed=embed, ephemeral=True)
            except Exception as follow_err:
                logger.error(f"❌ 無法發送錯誤訊息: {follow_err}")


def setup(bot: discord.Bot):
    """將收回術式註冊於幽幽子的靈魂"""
    bot.add_cog(RemoveMoney(bot))
    logger.info("🌸 幽靈幣收回模組已於櫻花樹下綻放完成")
