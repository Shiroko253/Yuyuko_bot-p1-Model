import discord
from discord.ext import commands
import logging

logger = logging.getLogger("SakuraBot.Tax")


def format_number(num):
    """將數字格式化為易讀形式,猶如櫻花瓣層層疊疊"""
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
    """
    根據資產金額動態給予稅率,低資產低稅,高資產高稅
    
    幽幽子的累進稅制:
    - 貧窮的靈魂只需繳納少許供品
    - 富有的靈魂需要多貢獻一些給冥界花園
    """
    if balance < 1000:
        return 0.05  # 5% - 新手保護
    elif balance < 10000:
        return 0.10  # 10% - 小康階級
    elif balance < 100000:
        return 0.20  # 20% - 中產階級
    elif balance < 1000000:
        return 0.30  # 30% - 富裕階級
    else:
        return 0.40  # 40% - 頂級富豪


class Tax(commands.Cog):
    """
    🌸 幽幽子的稅金徵收術式 🌸
    依照靈魂的財富多寡徵收稅金,
    讓國庫充盈,櫻花綻放～
    """
    
    def __init__(self, bot: discord.Bot):
        self.bot = bot
        self.data_manager = bot.data_manager
        logger.info("🌸 稅金徵收術式已於冥界花園中甦醒")

    @discord.slash_command(
        name="tax", 
        description="🌸 對伺服器用戶動態徵稅,存入國庫(僅管理員)"
    )
    async def tax(self, ctx: discord.ApplicationContext):
        """
        幽幽子的稅金徵收～
        
        依照每位靈魂的財富徵收不同比例的稅金,
        貧窮的靈魂稅率低,富有的靈魂稅率高,
        這就是冥界的公平正義!
        """
        try:
            guild_id = str(ctx.guild.id)
            user_id = str(ctx.author.id)

            # ----------- 僅管理員可用 -----------
            if not ctx.author.guild_permissions.administrator:
                embed = discord.Embed(
                    title="🌸 權限不足!",
                    description=(
                        "呼呼～只有管理員才能徵稅哦!\n"
                        "幽幽子可不想被亂收稅呢～"
                    ),
                    color=discord.Color.red()
                )
                embed.set_footer(
                    text="稅金由管理員統一徵收 · 幽幽子",
                    icon_url=self.bot.user.avatar.url if self.bot.user.avatar else None
                )
                await ctx.respond(embed=embed, ephemeral=True)
                return

            await ctx.defer()

            # ----------- 載入冥界記憶 -----------
            balance = self.data_manager._load_json("economy/balance.json", {})
            server_vault = self.data_manager._load_json("economy/server_vault.json", {})

            # 檢查是否有人有幽靈幣
            if guild_id not in balance or not balance[guild_id]:
                embed = discord.Embed(
                    title="🌸 無人可稅!",
                    description=(
                        "呼呼～這個伺服器還沒有人有幽靈幣哦!\n"
                        "快去玩遊戲賺錢吧,幽幽子在等美味的供品～"
                    ),
                    color=discord.Color.gold()
                )
                embed.set_footer(text="國庫空空如也 · 幽幽子")
                await ctx.followup.send(embed=embed)
                return

            # ----------- 執行徵稅術式 -----------
            total_tax = 0.0
            taxed_users = []
            contributions = {}

            async with self.data_manager.balance_lock:
                for taxed_user_id, user_balance in list(balance[guild_id].items()):
                    # 跳過執行者和無餘額用戶
                    if taxed_user_id == user_id:
                        continue
                    if user_balance <= 0:
                        continue

                    # 計算稅率和稅額
                    tax_rate = get_tax_rate(user_balance)
                    tax_amount = round(user_balance * tax_rate, 2)
                    new_balance = round(user_balance - tax_amount, 2)
                    
                    # 更新餘額
                    balance[guild_id][taxed_user_id] = new_balance
                    total_tax += tax_amount

                    # 記錄貢獻
                    contributions[taxed_user_id] = tax_amount

                    # 獲取用戶顯示名稱
                    try:
                        user = await self.bot.fetch_user(int(taxed_user_id))
                        display_name = getattr(user, "display_name", user.name)
                    except (discord.errors.NotFound, discord.errors.HTTPException):
                        display_name = f"用戶ID: {taxed_user_id}"
                    
                    taxed_users.append(
                        f"**{display_name}** "
                        f"({format_number(user_balance)} → {format_number(new_balance)}) "
                        f"課稅 {tax_rate*100:.0f}%：{format_number(tax_amount)} 幽靈幣"
                    )

            # ----------- 檢查是否有徵稅對象 -----------
            if not taxed_users:
                embed = discord.Embed(
                    title="🌸 無人可稅!",
                    description=(
                        "呼呼～沒有人有足夠的幽靈幣可以徵稅哦!\n"
                        "幽幽子只好餓肚子啦～"
                    ),
                    color=discord.Color.gold()
                )
                embed.set_footer(text="國庫依然空虛 · 幽幽子")
                await ctx.followup.send(embed=embed)
                return

            # ----------- 更新國庫 -----------
            if guild_id not in server_vault:
                server_vault[guild_id] = {}
            if "vault" not in server_vault[guild_id]:
                server_vault[guild_id]["vault"] = {
                    "total": 0.0,
                    "contributions": {}
                }

            server_vault[guild_id]["vault"]["total"] = round(
                server_vault[guild_id]["vault"]["total"] + total_tax, 2
            )

            # 累加各用戶貢獻
            for taxed_user_id, tax_amount in contributions.items():
                if tax_amount <= 0:
                    continue
                if taxed_user_id not in server_vault[guild_id]["vault"]["contributions"]:
                    server_vault[guild_id]["vault"]["contributions"][taxed_user_id] = 0.0
                
                server_vault[guild_id]["vault"]["contributions"][taxed_user_id] = round(
                    server_vault[guild_id]["vault"]["contributions"][taxed_user_id] + tax_amount, 2
                )

            # ----------- 保存數據 -----------
            self.data_manager._save_json("economy/balance.json", balance)
            self.data_manager._save_json("economy/server_vault.json", server_vault)

            # ----------- 靈魂回應 -----------
            executor = ctx.author.display_name
            current_vault = server_vault[guild_id]["vault"]["total"]

            # 分頁顯示徵稅對象(避免訊息過長)
            taxed_list = "\n".join(taxed_users[:10])  # 最多顯示前10個
            if len(taxed_users) > 10:
                taxed_list += f"\n...以及其他 {len(taxed_users) - 10} 位靈魂"

            embed = discord.Embed(
                title="🌸 幽幽子的動態稅金徵收!",
                description=(
                    f"呼呼～幽幽子在櫻花樹下對伺服器內所有亡魂徵收美味稅金!\n"
                    f"國庫又豐盈啦～\n\n"
                    f"📋 **徵稅執行者:** {executor}\n"
                    f"👥 **徵稅人數:** {len(taxed_users)} 位靈魂"
                ),
                color=discord.Color.from_rgb(205, 133, 232)  # 幽幽子主題紫櫻色
            )
            
            embed.add_field(
                name="💸 被徵稅者",
                value=taxed_list,
                inline=False
            )
            
            embed.add_field(
                name="📊 徵稅統計",
                value=(
                    f"```yaml\n"
                    f"本次稅金: {format_number(total_tax)} 幽靈幣\n"
                    f"國庫餘額: {format_number(current_vault)} 幽靈幣\n"
                    f"```"
                ),
                inline=False
            )
            
            embed.set_footer(
                text="幽幽子：賞花、吃點心、收稅金三連發! · 幽幽子",
                icon_url=self.bot.user.avatar.url if self.bot.user.avatar else None
            )
            
            await ctx.followup.send(embed=embed)

            logger.info(
                f"💰 {executor}({user_id}) 徵收稅金 {total_tax:.2f} 幽靈幣, "
                f"共 {len(taxed_users)} 位用戶, 國庫餘額: {current_vault:.2f}"
            )

        except Exception as e:
            logger.error(f"❌ 稅金徵收失敗: {e}", exc_info=True)
            embed = discord.Embed(
                title="❌ 徵稅術式崩壞",
                description=(
                    "哎呀,徵稅時發生了不明之力...\n"
                    "請稍後再試或使用 `/feedback` 回報給幽幽子的主人～"
                ),
                color=discord.Color.dark_red()
            )
            embed.set_footer(text="術式受阻,請稍後重試 · 幽幽子")
            
            try:
                if not ctx.interaction.response.is_done():
                    await ctx.respond(embed=embed, ephemeral=True)
                else:
                    await ctx.followup.send(embed=embed, ephemeral=True)
            except Exception:
                logger.exception("❌ 無法發送徵稅錯誤訊息")


def setup(bot: discord.Bot):
    """將稅金徵收術式註冊於幽幽子的靈魂"""
    bot.add_cog(Tax(bot))
    logger.info("🌸 稅金徵收模組已於櫻花樹下綻放完成")
