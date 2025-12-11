import logging
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
from zoneinfo import ZoneInfo
import discord
from discord.ext import commands, tasks
from discord.ui import View, Modal, InputText

logger = logging.getLogger("SakuraBot.ServerBank")


class ServerBank(commands.Cog):
    """
    🌸 幽幽子的櫻花金庫 🌸
    冥界國庫、個人金庫、借貸、存取款──
    幽幽子陪你守護每一枚幽靈幣,如同守護櫻花的綻放～
    """
    
    def __init__(self, bot: discord.Bot):
        self.bot = bot
        self.data_manager = bot.data_manager
        self.tz = ZoneInfo('Asia/Taipei')
        self.check_overdue_loans.start()  # 啟動逾期檢查任務
        logger.info("🌸 櫻花金庫已於冥界花園中開啟")

    def cog_unload(self):
        """卸載時停止定時任務"""
        self.check_overdue_loans.cancel()

    # ----------- 定時檢查逾期借貸 -----------
    @tasks.loop(hours=6)
    async def check_overdue_loans(self):
        """檢查逾期借貸並發送DM提醒,每7天翻4倍懲罰"""
        try:
            personal_bank = self.data_manager._load_json("economy/personal_bank.json", {})
            current_time = datetime.now(self.tz)
            
            for guild_id, users in personal_bank.items():
                guild = self.bot.get_guild(int(guild_id))
                if not guild:
                    continue
                
                for user_id, user_data in users.items():
                    if not isinstance(user_data, dict) or "loan" not in user_data:
                        continue
                    
                    loan = user_data["loan"]
                    if loan.get("repaid"):
                        continue
                    
                    try:
                        due_date = datetime.fromisoformat(loan["due_date"])
                        if due_date.tzinfo is None:
                            due_date = due_date.replace(tzinfo=self.tz)
                    except Exception as e:
                        logger.warning(f"⚠️ 無法解析到期日期: {e}")
                        continue
                    
                    days_overdue = (current_time - due_date).days
                    
                    # 1-6天逾期: 利息提升至20%
                    if 0 < days_overdue < 7:
                        if loan.get("interest_rate") == 0.1:
                            loan["interest_rate"] = 0.2
                            personal_bank[guild_id][user_id]["loan"] = loan
                            self.data_manager._save_json("economy/personal_bank.json", personal_bank)
                            logger.info(f"⚠️ 用戶 {user_id} 的利息已提升至 20%")
                    
                    # 7天以上: 每7天翻4倍懲罰
                    elif days_overdue >= 7:
                        penalty_cycles = days_overdue // 7
                        last_penalty_cycle = loan.get("last_penalty_cycle", 0)
                        
                        if penalty_cycles > last_penalty_cycle:
                            new_penalties = penalty_cycles - last_penalty_cycle
                            
                            for _ in range(new_penalties):
                                loan["amount"] *= 4
                            
                            loan["interest_rate"] = 0.1
                            loan["last_penalty_cycle"] = penalty_cycles
                            personal_bank[guild_id][user_id]["loan"] = loan
                            self.data_manager._save_json("economy/personal_bank.json", personal_bank)
                            
                            total_multiplier = 4 ** penalty_cycles
                            
                            try:
                                user = await self.bot.fetch_user(int(user_id))
                                
                                if penalty_cycles == 1:
                                    title = "⚠️ 櫻花債逾期警告"
                                    color = discord.Color.red()
                                    emoji = "⚠️"
                                elif penalty_cycles == 2:
                                    title = "🔥 櫻花債嚴重逾期!"
                                    color = discord.Color.from_rgb(255, 69, 0)
                                    emoji = "🔥"
                                else:
                                    title = "💀 櫻花債已失控!"
                                    color = discord.Color.from_rgb(139, 0, 0)
                                    emoji = "💀"
                                
                                embed = discord.Embed(
                                    title=title,
                                    description=(
                                        f"{emoji} 你在 **{guild.name}** 的借貸已經逾期 **{days_overdue}** 天了!\n\n"
                                        f"由於長期未歸還,幽幽子不得不應用懲罰措施...\n"
                                        f"你的借貸金額已經提升至 **{total_multiplier}倍**!"
                                    ),
                                    color=color
                                )
                                embed.add_field(
                                    name="📋 債務詳情",
                                    value=(
                                        f"```yaml\n"
                                        f"借貸金額: {self.format_number(loan['amount'])} 幽靈幣\n"
                                        f"利息率: {loan['interest_rate'] * 100:.0f}%\n"
                                        f"需還款: {self.format_number(loan['amount'] * 1.1)} 幽靈幣\n"
                                        f"逾期天數: {days_overdue} 天\n"
                                        f"懲罰倍數: {total_multiplier}x\n"
                                        f"懲罰次數: 第 {penalty_cycles} 次\n"
                                        f"```"
                                    ),
                                    inline=False
                                )
                                
                                if penalty_cycles == 1:
                                    advice = "• 請**立即還款**,避免債務繼續翻倍!\n• 每逾期7天,債務會再 ×4!"
                                elif penalty_cycles == 2:
                                    advice = "• 債務已經 **16倍**!\n• 再7天將變成 **64倍**!\n• **務必盡快還款**!"
                                else:
                                    advice = f"• 債務已達 **{total_multiplier}倍**,幾乎無法償還!\n• 請聯繫伺服器管理員尋求幫助!"
                                
                                embed.add_field(
                                    name="💡 建議",
                                    value=advice,
                                    inline=False
                                )
                                embed.set_footer(text="櫻花債不可輕視 · 幽幽子")
                                
                                await user.send(embed=embed)
                                logger.info(f"✉️ 已向用戶 {user_id} 發送第 {penalty_cycles} 次逾期提醒")
                            except Exception as e:
                                logger.error(f"❌ 無法向用戶 {user_id} 發送DM: {e}")
        
        except Exception as e:
            logger.error(f"❌ 逾期檢查失敗: {e}", exc_info=True)

    @check_overdue_loans.before_loop
    async def before_check_overdue_loans(self):
        """等待bot準備完成"""
        await self.bot.wait_until_ready()

    # ----------- 金額格式化 -----------
    def format_number(self, num: float) -> str:
        """將數字格式化為易讀形式"""
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

    # ----------- 記錄交易 -----------
    def log_transaction(self, guild_id: str, user_id: str, amount: float, transaction_type: str):
        """記錄交易"""
        try:
            transactions = self.data_manager._load_json("economy/transactions.json", {})
            
            if guild_id not in transactions:
                transactions[guild_id] = []
            
            transactions[guild_id].append({
                "user_id": user_id,
                "amount": float(amount),
                "type": transaction_type,
                "timestamp": datetime.now(self.tz).isoformat()
            })
            
            self.data_manager._save_json("economy/transactions.json", transactions)
            logger.info(f"📝 交易已記錄: {transaction_type} | 用戶: {user_id} | 金額: {amount:.2f}")
        except Exception as e:
            logger.error(f"❌ 交易記錄失敗: {e}", exc_info=True)

    # ----------- 初始化用戶數據 -----------
    def initialize_user_data(self, balance: dict, personal_bank: dict, guild_id: str, user_id: str):
        """初始化用戶數據結構"""
        if guild_id not in balance:
            balance[guild_id] = {}
        if user_id not in balance[guild_id]:
            balance[guild_id][user_id] = 0.0
        elif not isinstance(balance[guild_id][user_id], (int, float)):
            balance[guild_id][user_id] = 0.0

        if guild_id not in personal_bank:
            personal_bank[guild_id] = {}
        if user_id not in personal_bank[guild_id]:
            personal_bank[guild_id][user_id] = {
                "balance": 0.0,
                "loan": None
            }
        elif not isinstance(personal_bank[guild_id][user_id], dict):
            personal_bank[guild_id][user_id] = {
                "balance": 0.0,
                "loan": None
            }

        return balance, personal_bank

    # ----------- 檢查借貸狀態 -----------
    def check_loan_status(self, personal_bank: dict, guild_id: str, user_id: str):
        """檢查用戶借貸狀態"""
        if guild_id not in personal_bank or user_id not in personal_bank[guild_id]:
            return None
        
        user_data = personal_bank[guild_id][user_id]
        if not isinstance(user_data, dict) or "loan" not in user_data:
            return None
        
        loan = user_data["loan"]
        if loan is None or loan.get("repaid"):
            return None
        
        return loan

    # ----------- 主金庫互動介面 -----------
    @discord.slash_command(
        name="server_bank",
        description="🌸 與幽幽子的櫻花金庫互動,存錢、取錢或借貸～"
    )
    async def server_bank(self, ctx: discord.ApplicationContext):
        """開啟櫻花金庫"""
        guild_id = str(ctx.guild.id)
        user_id = str(ctx.author.id)

        # 使用內存數據而不是直接從文件讀取
        balance = self.data_manager.balance
        personal_bank = self.data_manager._load_json("economy/personal_bank.json", {})
        server_vault = self.data_manager._load_json("economy/server_vault.json", {})

        # 初始化用戶數據
        if guild_id not in balance:
            balance[guild_id] = {}
        if user_id not in balance[guild_id]:
            balance[guild_id][user_id] = 0.0

        if guild_id not in personal_bank:
            personal_bank[guild_id] = {}
        if user_id not in personal_bank[guild_id]:
            personal_bank[guild_id][user_id] = {
                "balance": 0.0,
                "loan": None
            }
        elif not isinstance(personal_bank[guild_id][user_id], dict):
            personal_bank[guild_id][user_id] = {
                "balance": 0.0,
                "loan": None
            }

        user_balance = balance[guild_id][user_id]
        personal_bank_balance = personal_bank[guild_id][user_id]["balance"]
        
        # 從 server_vault 獲取國庫總額
        vault_total = server_vault.get(guild_id, {}).get("vault", {}).get("total", 0.0)

        loan = self.check_loan_status(personal_bank, guild_id, user_id)
        loan_info = ""
        
        # 計算可借貸額度（國庫餘額的50%或固定額度，取較小值）
        max_borrow_amount = min(vault_total * 0.5, 1000000.0)  # 最多借100萬或國庫的50%
        
        if loan:
            try:
                due_date = datetime.fromisoformat(loan["due_date"])
                if due_date.tzinfo is None:
                    due_date = due_date.replace(tzinfo=self.tz)
            except Exception:
                due_date = datetime.now(self.tz) + timedelta(days=5)

            amount_with_interest = round(loan["amount"] * (1 + loan["interest_rate"]), 2)
            
            current_time = datetime.now(self.tz)
            is_overdue = current_time > due_date
            days_overdue = (current_time - due_date).days if is_overdue else 0
            
            overdue_emoji = "⚠️" if is_overdue else "💸"
            overdue_text = ""
            if days_overdue >= 7:
                overdue_text = " **已逾期超過一週!金額已4倍懲罰!**"
            elif is_overdue:
                overdue_text = f" **已逾期 {days_overdue} 天!利息已加倍!**"
            
            loan_info = (
                f"\n\n{overdue_emoji} **未還款的櫻花債**{overdue_text}\n"
                f"```yaml\n"
                f"借貸金額: {self.format_number(loan['amount'])} 幽靈幣\n"
                f"利息率: {loan['interest_rate'] * 100:.0f}%\n"
                f"需還款: {self.format_number(amount_with_interest)} 幽靈幣\n"
                f"截止日期: {due_date.strftime('%Y-%m-%d %H:%M')}\n"
                f"```"
            )

        embed = discord.Embed(
            title="🌸 幽幽子的櫻花金庫 🌸",
            description=(
                f"呼呼～歡迎來到 **{ctx.guild.name}** 的金庫!\n"
                f"你是要存錢、取錢還是借貸呢?\n"
                f"幽幽子會好好保管你的幽靈幣哦～"
            ),
            color=discord.Color.from_rgb(255, 182, 193)
        )
        
        # 冥界國庫資訊
        embed.add_field(
            name="🏛️ 冥界國庫（伺服器金庫）",
            value=(
                f"```yaml\n"
                f"國庫總額: {self.format_number(vault_total)} 幽靈幣\n"
                f"可借額度: {self.format_number(max_borrow_amount)} 幽靈幣\n"
                f"```"
            ),
            inline=False
        )
        
        # 個人財富狀況
        embed.add_field(
            name="💰 你的財富狀況",
            value=(
                f"```yaml\n"
                f"手頭餘額: {user_balance:,.2f} 幽靈幣\n"
                f"個人金庫: {self.format_number(personal_bank_balance)} 幽靈幣\n"
                f"總資產: {self.format_number(user_balance + personal_bank_balance)} 幽靈幣\n"
                f"```"
            ),
            inline=False
        )
        
        if loan_info:
            embed.add_field(
                name="📋 借貸詳情",
                value=loan_info,
                inline=False
            )
        
        embed.set_footer(
            text="櫻花飄落處,財富也隨風而至 · 幽幽子",
            icon_url=self.bot.user.avatar.url if self.bot.user and self.bot.user.avatar else None
        )
        embed.set_thumbnail(url=ctx.author.display_avatar.url)

        view = BankButtonsView(self, ctx, guild_id, user_id, bool(loan))
        
        try:
            msg = await ctx.respond(embed=embed, view=view)
            resolved_msg = await msg.original_response()
            view.message = resolved_msg
            logger.info(f"👤 用戶 {ctx.author.name}({user_id}) 開啟櫻花金庫")
            
            # 保存 personal_bank（balance 不需要保存，因為使用內存）
            self.data_manager._save_json("economy/personal_bank.json", personal_bank)
        except Exception as e:
            logger.error(f"❌ 金庫開啟失敗: {e}", exc_info=True)


class BankButtonsView(View):
    """金庫操作按鈕"""
    
    def __init__(self, cog: ServerBank, ctx: discord.ApplicationContext, guild_id: str, user_id: str, has_loan: bool):
        super().__init__(timeout=60)
        self.cog = cog
        self.ctx = ctx
        self.guild_id = guild_id
        self.user_id = user_id
        self.has_loan = has_loan
        self.message = None
        self.interaction_completed = False
        
        if len(self.children) >= 4:
            self.children[3].disabled = not has_loan

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """確保只有命令發起者能操作"""
        if interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message("呀啦呀啦～這不是你的金庫操作哦!", ephemeral=True)
            return False
        
        if self.interaction_completed:
            await interaction.response.send_message("操作已完成,請重新執行 `/server_bank` 命令!", ephemeral=True)
            return False
        
        return True

    async def on_timeout(self):
        """超時處理"""
        if self.interaction_completed:
            return
        
        for item in self.children:
            item.disabled = True
        
        embed = discord.Embed(
            title="🌸 金庫操作已結束",
            description="操作已超時,櫻花已隨風散去...\n請重新執行 `/server_bank` 命令!",
            color=discord.Color.orange()
        )
        embed.set_footer(text="時光流逝如櫻花飄落 · 幽幽子")
        
        if self.message:
            try:
                await self.message.edit(embed=embed, view=self)
            except Exception as e:
                logger.error(f"❌ 金庫超時處理失敗: {e}")
    
    async def update_main_embed(self, interaction: discord.Interaction):
        """更新主介面"""
        try:
            # 使用內存數據
            balance = self.cog.data_manager.balance
            personal_bank = self.cog.data_manager._load_json("economy/personal_bank.json", {})
            server_vault = self.cog.data_manager._load_json("economy/server_vault.json", {})
            
            user_balance = balance.get(self.guild_id, {}).get(self.user_id, 0.0)
            personal_bank_balance = personal_bank.get(self.guild_id, {}).get(self.user_id, {}).get("balance", 0.0)
            
            # 從 server_vault 獲取國庫總額
            vault_total = server_vault.get(self.guild_id, {}).get("vault", {}).get("total", 0.0)
            
            # 計算可借貸額度
            max_borrow_amount = min(vault_total * 0.5, 1000000.0)
            
            loan = self.cog.check_loan_status(personal_bank, self.guild_id, self.user_id)
            loan_info = ""
            
            if loan:
                try:
                    due_date = datetime.fromisoformat(loan["due_date"])
                    if due_date.tzinfo is None:
                        due_date = due_date.replace(tzinfo=self.cog.tz)
                except Exception:
                    due_date = datetime.now(self.cog.tz) + timedelta(days=5)

                amount_with_interest = round(loan["amount"] * (1 + loan["interest_rate"]), 2)
                
                current_time = datetime.now(self.cog.tz)
                is_overdue = current_time > due_date
                days_overdue = (current_time - due_date).days if is_overdue else 0
                
                overdue_emoji = "⚠️" if is_overdue else "💸"
                overdue_text = ""
                if days_overdue >= 7:
                    overdue_text = " **已逾期超過一週!金額已4倍懲罰!**"
                elif is_overdue:
                    overdue_text = f" **已逾期 {days_overdue} 天!利息已加倍!**"
                
                loan_info = (
                    f"\n\n{overdue_emoji} **未還款的櫻花債**{overdue_text}\n"
                    f"```yaml\n"
                    f"借貸金額: {self.cog.format_number(loan['amount'])} 幽靈幣\n"
                    f"利息率: {loan['interest_rate'] * 100:.0f}%\n"
                    f"需還款: {self.cog.format_number(amount_with_interest)} 幽靈幣\n"
                    f"截止日期: {due_date.strftime('%Y-%m-%d %H:%M')}\n"
                    f"```"
                )
            
            embed = discord.Embed(
                title="🌸 幽幽子的櫻花金庫 🌸",
                description=(
                    f"呼呼～歡迎來到 **{self.ctx.guild.name}** 的金庫!\n"
                    f"你是要存錢、取錢還是借貸呢?\n"
                    f"幽幽子會好好保管你的幽靈幣哦～"
                ),
                color=discord.Color.from_rgb(255, 182, 193)
            )
            
            # 冥界國庫資訊
            embed.add_field(
                name="🏛️ 冥界國庫（伺服器金庫）",
                value=(
                    f"```yaml\n"
                    f"國庫總額: {self.cog.format_number(vault_total)} 幽靈幣\n"
                    f"可借額度: {self.cog.format_number(max_borrow_amount)} 幽靈幣\n"
                    f"```"
                ),
                inline=False
            )
            
            # 個人財富狀況
            embed.add_field(
                name="💰 你的財富狀況",
                value=(
                    f"```yaml\n"
                    f"手頭餘額: {user_balance:,.2f} 幽靈幣\n"
                    f"個人金庫: {self.cog.format_number(personal_bank_balance)} 幽靈幣\n"
                    f"總資產: {self.cog.format_number(user_balance + personal_bank_balance)} 幽靈幣\n"
                    f"```"
                ),
                inline=False
            )
            
            if loan_info:
                embed.add_field(
                    name="📋 借貸詳情",
                    value=loan_info,
                    inline=False
                )
            
            embed.set_footer(
                text="櫻花飄落處,財富也隨風而至 · 幽幽子",
                icon_url=self.cog.bot.user.avatar.url if self.cog.bot.user and self.cog.bot.user.avatar else None
            )
            embed.set_thumbnail(url=interaction.user.display_avatar.url)
            
            self.has_loan = bool(loan)
            if len(self.children) >= 4:
                self.children[3].disabled = not self.has_loan
            
            if self.message:
                await self.message.edit(embed=embed, view=self)
            
        except Exception as e:
            logger.error(f"❌ 更新主 embed 失敗: {e}", exc_info=True)

    @discord.ui.button(label="存錢", style=discord.ButtonStyle.primary, emoji="💰", row=0)
    async def deposit(self, button: discord.ui.Button, interaction: discord.Interaction):
        """存款按鈕"""
        modal = DepositModal(self.cog, self.guild_id, self.user_id, self)
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="取錢", style=discord.ButtonStyle.success, emoji="💵", row=0)
    async def withdraw(self, button: discord.ui.Button, interaction: discord.Interaction):
        """取款按鈕"""
        # 檢查個人金庫是否有餘額
        personal_bank = self.cog.data_manager._load_json("economy/personal_bank.json", {})
        bank_balance = personal_bank.get(self.guild_id, {}).get(self.user_id, {}).get("balance", 0.0)
        
        if bank_balance <= 0:
            embed = discord.Embed(
                title="🌸 金庫空空如也",
                description="呼呼～你的個人金庫裡空空如也呢...\n還沒有存入任何幽靈幣哦!",
                color=discord.Color.red()
            )
            embed.set_footer(text="先存錢才能取錢哦 · 幽幽子")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        modal = WithdrawModal(self.cog, self.guild_id, self.user_id, self)
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="借貸", style=discord.ButtonStyle.danger, emoji="📜", row=0)
    async def borrow(self, button: discord.ui.Button, interaction: discord.Interaction):
        """借貸按鈕"""
        modal = BorrowModal(self.cog, self.guild_id, self.user_id, self.has_loan, self)
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="還款", style=discord.ButtonStyle.green, emoji="✅", row=1)
    async def repay(self, button: discord.ui.Button, interaction: discord.Interaction):
        """還款按鈕"""
        if not self.has_loan:
            embed = discord.Embed(
                title="🌸 無需還款",
                description="呼呼～你目前沒有未還款的櫻花債呢!\n靈魂很輕盈,真好～",
                color=discord.Color.gold()
            )
            embed.set_footer(text="無債一身輕 · 幽幽子")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        await interaction.response.defer()
        
        async with self.cog.data_manager.balance_lock:
            balance = self.cog.data_manager.balance
            personal_bank = self.cog.data_manager._load_json("economy/personal_bank.json", {})
            server_vault = self.cog.data_manager._load_json("economy/server_vault.json", {})
            
            loan = self.cog.check_loan_status(personal_bank, self.guild_id, self.user_id)
        
        if not loan:
            await self.update_main_embed(interaction)
            return
        
        balance = self.cog.data_manager._load_json("economy/balance.json", {})
        user_balance = balance.get(self.guild_id, {}).get(self.user_id, 0.0)
        amount_with_interest = round(loan["amount"] * (1 + loan["interest_rate"]), 2)
        
        if user_balance < amount_with_interest:
            embed = discord.Embed(
                title="🌸 餘額不足",
                description=(
                    f"呼呼～你需要 **{self.cog.format_number(amount_with_interest)}** 幽靈幣才能還款,\n"
                    f"但你只有 **{user_balance:,.2f}** 幽靈幣...\n"
                    f"還差 **{self.cog.format_number(amount_with_interest - user_balance)}** 幽靈幣呢!"
                ),
                color=discord.Color.red()
            )
            embed.set_footer(text="先賺點幽靈幣吧 · 幽幽子")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        
        # 執行還款
        balance[self.guild_id][self.user_id] -= amount_with_interest
        personal_bank[self.guild_id][self.user_id]["loan"] = None
        
        self.cog.data_manager._save_json("economy/balance.json", balance)
        self.cog.data_manager._save_json("economy/personal_bank.json", personal_bank)
        self.cog.log_transaction(self.guild_id, self.user_id, amount_with_interest, "repay")
        
        # 更新主界面
        await self.update_main_embed(interaction)
        
        # 成功消息
        interest_amount = amount_with_interest - loan["amount"]
        embed = discord.Embed(
            title="🌸 還款成功!",
            description=f"呼呼～你已成功還款 **{self.cog.format_number(amount_with_interest)}** 幽靈幣!\n債務已清除,櫻花債不再～",
            color=discord.Color.from_rgb(144, 238, 144)
        )
        embed.add_field(
            name="💰 還款明細",
            value=(
                f"```yaml\n"
                f"借款本金: {self.cog.format_number(loan['amount'])} 幽靈幣（已歸還國庫）\n"
                f"利息支付: {self.cog.format_number(interest_amount)} 幽靈幣（國庫收益）\n"
                f"總支付: {self.cog.format_number(amount_with_interest)} 幽靈幣\n"
                f"```"
            ),
            inline=False
        )
        embed.add_field(
            name="📊 新餘額",
            value=(
                f"```yaml\n"
                f"手頭餘額: {balance[self.guild_id][self.user_id]:,.2f} 幽靈幣\n"
                f"```"
            ),
            inline=False
        )
        embed.set_footer(text="無債一身輕 · 幽幽子")
        await interaction.followup.send(embed=embed, ephemeral=True)
        logger.info(f"✅ 用戶 {self.user_id} 成功還款 {amount_with_interest:.2f} 幽靈幣（本金: {loan['amount']:.2f}, 利息: {interest_amount:.2f}）")
    
    @discord.ui.button(label="結束操作", style=discord.ButtonStyle.gray, emoji="❌", row=1)
    async def close_bank(self, button: discord.ui.Button, interaction: discord.Interaction):
        """結束操作"""
        self.interaction_completed = True
        self.stop()  # 停止 View,防止超時繼續運行
        
        for item in self.children:
            item.disabled = True
        
        embed = discord.Embed(
            title="🌸 金庫已關閉",
            description="呼呼～金庫操作已結束!\n櫻花隨風飄散,期待下次再見～",
            color=discord.Color.from_rgb(255, 182, 193)
        )
        embed.set_footer(
            text="願櫻花守護你的財富 · 幽幽子",
            icon_url=self.cog.bot.user.avatar.url if self.cog.bot.user and self.cog.bot.user.avatar else None
        )
        
        if self.message:
            await self.message.edit(embed=embed, view=self)
        
        await interaction.response.defer()
        logger.info(f"👋 用戶 {self.user_id} 結束金庫操作")


# ----------- Modal: 存款 -----------
class DepositModal(Modal):
    """存款模態窗口"""
    
    def __init__(self, cog: ServerBank, guild_id: str, user_id: str, view: BankButtonsView):
        super().__init__(title="🌸 存入幽靈幣至個人金庫")
        self.cog = cog
        self.guild_id = guild_id
        self.user_id = user_id
        self.view = view
        
        self.add_item(InputText(
            label="存款金額",
            placeholder="請輸入要存入的幽靈幣數量...",
            style=discord.InputTextStyle.short,
            required=True
        ))
    
    async def callback(self, interaction: discord.Interaction):
        # ✅ 立即 defer，防止超時
        await interaction.response.defer(ephemeral=True)
        
        try:
            # 解析金額
            try:
                amount = Decimal(self.children[0].value.strip())
                if amount <= 0:
                    raise ValueError("金額必須為正數")
                amount = amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            except (InvalidOperation, ValueError):
                embed = discord.Embed(
                    title="❌ 金額格式錯誤",
                    description="請輸入有效的正數金額!",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
            
            # 使用內存數據並加鎖
            async with self.cog.data_manager.balance_lock:
                balance = self.cog.data_manager.balance
                personal_bank = self.cog.data_manager._load_json("economy/personal_bank.json", {})
                
                # 確保結構存在
                if self.guild_id not in balance or self.user_id not in balance[self.guild_id]:
                    balance.setdefault(self.guild_id, {})[self.user_id] = 0.0
                
                if self.guild_id not in personal_bank or self.user_id not in personal_bank[self.guild_id]:
                    personal_bank.setdefault(self.guild_id, {})[self.user_id] = {"balance": 0.0, "loan": None}
                
                user_balance = Decimal(str(balance[self.guild_id][self.user_id]))
                
                # 檢查餘額
                if user_balance <= 0:
                    embed = discord.Embed(
                        title="🌸 手頭無幽靈幣",
                        description="呼呼～你手頭上沒有幽靈幣呢...\n無法存入金庫哦!",
                        color=discord.Color.red()
                    )
                    embed.set_footer(text="先賺點幽靈幣吧 · 幽幽子")
                    await interaction.followup.send(embed=embed, ephemeral=True)
                    return
                
                if user_balance < amount:
                    embed = discord.Embed(
                        title="🌸 餘額不足",
                        description=(
                            f"呼呼～你的手頭餘額只有 **{user_balance:,.2f}** 幽靈幣,\n"
                            f"不足以存入 **{float(amount):,.2f}** 幽靈幣呢..."
                        ),
                        color=discord.Color.red()
                    )
                    embed.add_field(
                        name="💡 建議",
                        value=f"• 你可以存入最多 {user_balance:,.2f} 幽靈幣",
                        inline=False
                    )
                    embed.set_footer(text="量入為出 · 幽幽子")
                    await interaction.followup.send(embed=embed, ephemeral=True)
                    return
                
                # 執行存款
                old_user_balance = balance[self.guild_id][self.user_id]
                old_bank_balance = personal_bank[self.guild_id][self.user_id]["balance"]
                
                balance[self.guild_id][self.user_id] -= float(amount)
                personal_bank[self.guild_id][self.user_id]["balance"] += float(amount)
                
                logger.info(f"💰 存款金額: {float(amount):.2f}")
                logger.info(f"👤 手頭餘額: {old_user_balance:.2f} -> {balance[self.guild_id][self.user_id]:.2f}")
                logger.info(f"🏦 個人金庫: {old_bank_balance:.2f} -> {personal_bank[self.guild_id][self.user_id]['balance']:.2f}")
                
                # 保存數據（balance 通過 save_all 保存，personal_bank 直接保存）
                try:
                    self.cog.data_manager._save_json("economy/personal_bank.json", personal_bank)
                    self.cog.data_manager.save_all()  # 保存內存中的 balance
                    logger.info(f"✅ 數據已保存")
                except Exception as e:
                    logger.error(f"❌ 保存數據失敗: {e}", exc_info=True)
                
                self.cog.log_transaction(self.guild_id, self.user_id, float(amount), "deposit")
            
            # 更新主界面
            await self.view.update_main_embed(interaction)
            
            # 成功消息
            embed = discord.Embed(
                title="🌸 存款成功!",
                description=f"呼呼～你已將 **{float(amount):,.2f}** 幽靈幣存入個人金庫!",
                color=discord.Color.from_rgb(144, 238, 144)
            )
            embed.add_field(
                name="📊 新餘額",
                value=(
                    f"```yaml\n"
                    f"手頭餘額: {balance[self.guild_id][self.user_id]:,.2f} 幽靈幣\n"
                    f"個人金庫: {self.cog.format_number(personal_bank[self.guild_id][self.user_id]['balance'])} 幽靈幣\n"
                    f"```"
                ),
                inline=False
            )
            embed.set_footer(text="櫻花守護你的財富 · 幽幽子")
            await interaction.followup.send(embed=embed, ephemeral=True)
            
            logger.info(f"💰 用戶 {self.user_id} 存款 {float(amount):.2f} 幽靈幣")
            
        except Exception as e:
            logger.error(f"❌ 存款失敗: {e}", exc_info=True)
            try:
                await interaction.followup.send("❌ 存款時發生錯誤，請稍後再試", ephemeral=True)
            except:
                pass


# ----------- Modal: 取款 -----------
class WithdrawModal(Modal):
    """取款模態窗口"""
    
    def __init__(self, cog: ServerBank, guild_id: str, user_id: str, view: BankButtonsView):
        super().__init__(title="🌸 從個人金庫取出幽靈幣")
        self.cog = cog
        self.guild_id = guild_id
        self.user_id = user_id
        self.view = view
        
        self.add_item(InputText(
            label="取款金額",
            placeholder="請輸入要取出的幽靈幣數量...",
            style=discord.InputTextStyle.short,
            required=True
        ))
    
    async def callback(self, interaction: discord.Interaction):
        # ✅ 立即 defer
        await interaction.response.defer(ephemeral=True)
        
        try:
            # 解析金額
            try:
                amount = Decimal(self.children[0].value.strip())
                if amount <= 0:
                    raise ValueError("金額必須為正數")
                amount = amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            except (InvalidOperation, ValueError):
                embed = discord.Embed(
                    title="❌ 金額格式錯誤",
                    description="請輸入有效的正數金額!",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
            
            # 使用內存數據並加鎖
            async with self.cog.data_manager.balance_lock:
                balance = self.cog.data_manager.balance
                personal_bank = self.cog.data_manager._load_json("economy/personal_bank.json", {})
                
                bank_balance = Decimal(str(personal_bank.get(self.guild_id, {}).get(self.user_id, {}).get("balance", 0.0)))
                
                # 檢查金庫餘額
                if bank_balance < amount:
                    embed = discord.Embed(
                        title="🌸 金庫餘額不足",
                        description=(
                            f"呼呼～你的個人金庫只有 **{self.cog.format_number(float(bank_balance))}** 幽靈幣,\n"
                            f"不足以取出 **{float(amount):,.2f}** 幽靈幣呢..."
                        ),
                        color=discord.Color.red()
                    )
                    embed.add_field(
                        name="💡 建議",
                        value=f"• 你可以取出最多 {self.cog.format_number(float(bank_balance))} 幽靈幣",
                        inline=False
                    )
                    embed.set_footer(text="金庫餘額有限 · 幽幽子")
                    await interaction.followup.send(embed=embed, ephemeral=True)
                    return
                
                # 執行取款
                old_user_balance = balance.get(self.guild_id, {}).get(self.user_id, 0.0)
                old_bank_balance = personal_bank[self.guild_id][self.user_id]["balance"]
                
                personal_bank[self.guild_id][self.user_id]["balance"] -= float(amount)
                
                # 確保用戶在 balance 中存在
                if self.guild_id not in balance:
                    balance[self.guild_id] = {}
                if self.user_id not in balance[self.guild_id]:
                    balance[self.guild_id][self.user_id] = 0.0
                    
                balance[self.guild_id][self.user_id] += float(amount)
                
                logger.info(f"💵 取款金額: {float(amount):.2f}")
                logger.info(f"🏦 個人金庫: {old_bank_balance:.2f} -> {personal_bank[self.guild_id][self.user_id]['balance']:.2f}")
                logger.info(f"👤 手頭餘額: {old_user_balance:.2f} -> {balance[self.guild_id][self.user_id]:.2f}")
                
                # 保存數據
                try:
                    self.cog.data_manager._save_json("economy/personal_bank.json", personal_bank)
                    self.cog.data_manager.save_all()  # 保存內存中的 balance
                    logger.info(f"✅ 數據已保存")
                except Exception as e:
                    logger.error(f"❌ 保存數據失敗: {e}", exc_info=True)
                
                self.cog.log_transaction(self.guild_id, self.user_id, float(amount), "withdraw")
            
            # 更新主界面
            await self.view.update_main_embed(interaction)
            
            # 成功消息
            embed = discord.Embed(
                title="🌸 取款成功!",
                description=f"呼呼～你已從個人金庫取出 **{float(amount):,.2f}** 幽靈幣!",
                color=discord.Color.from_rgb(144, 238, 144)
            )
            embed.add_field(
                name="📊 新餘額",
                value=(
                    f"```yaml\n"
                    f"手頭餘額: {balance[self.guild_id][self.user_id]:,.2f} 幽靈幣\n"
                    f"個人金庫: {self.cog.format_number(personal_bank[self.guild_id][self.user_id]['balance'])} 幽靈幣\n"
                    f"```"
                ),
                inline=False
            )
            embed.set_footer(text="櫻花守護你的財富 · 幽幽子")
            await interaction.followup.send(embed=embed, ephemeral=True)
            
            logger.info(f"💵 用戶 {self.user_id} 取款 {float(amount):.2f} 幽靈幣")
            
        except Exception as e:
            logger.error(f"❌ 取款失敗: {e}", exc_info=True)
            try:
                await interaction.followup.send("❌ 取款時發生錯誤，請稍後再試", ephemeral=True)
            except:
                pass


# ----------- Modal: 借貸 -----------
class BorrowModal(Modal):
    """借貸模態窗口"""
    
    def __init__(self, cog: ServerBank, guild_id: str, user_id: str, has_loan: bool, view: BankButtonsView):
        super().__init__(title="🌸 向國庫借貸幽靈幣")
        self.cog = cog
        self.guild_id = guild_id
        self.user_id = user_id
        self.has_loan = has_loan
        self.view = view
        
        self.add_item(InputText(
            label="借貸金額",
            placeholder="請輸入要借貸的幽靈幣數量...",
            style=discord.InputTextStyle.short,
            required=True
        ))
    
    async def callback(self, interaction: discord.Interaction):
        # ✅ 立即 defer
        await interaction.response.defer(ephemeral=True)
        
        try:
            # 解析金額
            try:
                amount = Decimal(self.children[0].value.strip())
                if amount <= 0:
                    raise ValueError("金額必須為正數")
                amount = amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            except (InvalidOperation, ValueError):
                embed = discord.Embed(
                    title="❌ 金額格式錯誤",
                    description="請輸入有效的正數金額!",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
            
            # 載入數據
            async with self.cog.data_manager.balance_lock:
                balance = self.cog.data_manager.balance
                personal_bank = self.cog.data_manager._load_json("economy/personal_bank.json", {})
                server_vault = self.cog.data_manager._load_json("economy/server_vault.json", {})
            
            # 從 server_vault 獲取國庫總額
            vault_total = server_vault.get(self.guild_id, {}).get("vault", {}).get("total", 0.0)
            max_borrow_amount = min(vault_total * 0.5, 1000000.0)
            
            # 檢查國庫是否有足夠的錢
            if vault_total < float(amount):
                embed = discord.Embed(
                    title="🌸 國庫餘額不足",
                    description=(
                        f"呼呼～國庫目前只有 **{self.cog.format_number(vault_total)}** 幽靈幣,\n"
                        f"不足以借出 **{float(amount):,.2f}** 幽靈幣呢..."
                    ),
                    color=discord.Color.red()
                )
                embed.add_field(
                    name="💡 說明",
                    value=f"• 國庫餘額不足，請聯繫管理員補充國庫",
                    inline=False
                )
                embed.set_footer(text="國庫需要補充 · 幽幽子")
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
            
            # 檢查借貸額度
            if float(amount) > max_borrow_amount:
                embed = discord.Embed(
                    title="🌸 超出可借額度",
                    description=(
                        f"呼呼～你想借 **{float(amount):,.2f}** 幽靈幣,\n"
                        f"但目前最多只能借 **{self.cog.format_number(max_borrow_amount)}** 幽靈幣呢..."
                    ),
                    color=discord.Color.red()
                )
                embed.add_field(
                    name="💡 說明",
                    value=(
                        f"```yaml\n"
                        f"國庫總額: {self.cog.format_number(vault_total)} 幽靈幣\n"
                        f"可借額度: {self.cog.format_number(max_borrow_amount)} 幽靈幣\n"
                        f"```\n"
                        f"• 可借額度為國庫的50%或100萬，取較小值"
                    ),
                    inline=False
                )
                embed.set_footer(text="量力而行 · 幽幽子")
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
            
            # 執行借貸 - 從國庫扣款
            if self.guild_id not in server_vault:
                server_vault[self.guild_id] = {"vault": {"total": 0.0, "contributions": {}}}
            if "vault" not in server_vault[self.guild_id]:
                server_vault[self.guild_id]["vault"] = {"total": 0.0, "contributions": {}}
            
            # 確保用戶數據結構存在
            if self.guild_id not in balance:
                balance[self.guild_id] = {}
            if self.user_id not in balance[self.guild_id]:
                balance[self.guild_id][self.user_id] = 0.0
            
            if self.guild_id not in personal_bank:
                personal_bank[self.guild_id] = {}
            if self.user_id not in personal_bank[self.guild_id]:
                personal_bank[self.guild_id][self.user_id] = {"balance": 0.0, "loan": None}
            
            # 從國庫扣款，給用戶增加餘額
            old_user_balance = balance.get(self.guild_id, {}).get(self.user_id, 0.0)
            old_vault_total = server_vault[self.guild_id]["vault"]["total"]
            
            server_vault[self.guild_id]["vault"]["total"] -= float(amount)
            
            # 確保用戶在 balance 中存在
            if self.guild_id not in balance:
                balance[self.guild_id] = {}
            if self.user_id not in balance[self.guild_id]:
                balance[self.guild_id][self.user_id] = 0.0
                
            balance[self.guild_id][self.user_id] += float(amount)
            
            logger.info(f"💰 借貸金額: {float(amount):.2f}")
            logger.info(f"👤 用戶餘額: {old_user_balance:.2f} -> {balance[self.guild_id][self.user_id]:.2f}")
            logger.info(f"🏛️ 國庫餘額: {old_vault_total:.2f} -> {server_vault[self.guild_id]['vault']['total']:.2f}")
            
            current_time = datetime.now(self.cog.tz)
            loan_data = personal_bank[self.guild_id][self.user_id].get("loan")
            
            # 累積借貸
            if loan_data and not loan_data.get("repaid"):
                old_amount = loan_data["amount"]
                loan_data["amount"] += float(amount)
                loan_data["last_borrowed_at"] = current_time.isoformat()
                loan_data["due_date"] = (current_time + timedelta(days=5)).isoformat()
                is_additional = True
            else:
                # 新借貸
                loan_data = {
                    "amount": float(amount),
                    "interest_rate": 0.1,
                    "borrowed_at": current_time.isoformat(),
                    "due_date": (current_time + timedelta(days=5)).isoformat(),
                    "repaid": False,
                    "last_penalty_cycle": 0
                }
                is_additional = False
                old_amount = 0
            
            personal_bank[self.guild_id][self.user_id]["loan"] = loan_data
            
            # 保存數據（包括 server_vault）- 按順序保存確保數據一致性
            try:
                self.cog.data_manager._save_json("economy/balance.json", balance)
                logger.info(f"✅ balance.json 已保存")
            except Exception as e:
                logger.error(f"❌ 保存 balance.json 失敗: {e}")
            
            try:
                self.cog.data_manager._save_json("economy/personal_bank.json", personal_bank)
                logger.info(f"✅ personal_bank.json 已保存")
            except Exception as e:
                logger.error(f"❌ 保存 personal_bank.json 失敗: {e}")
            
            try:
                self.cog.data_manager._save_json("economy/server_vault.json", server_vault)
                logger.info(f"✅ server_vault.json 已保存")
            except Exception as e:
                logger.error(f"❌ 保存 server_vault.json 失敗: {e}")
            
            self.cog.log_transaction(self.guild_id, self.user_id, float(amount), "borrow")
            
            # 更新主界面
            await self.view.update_main_embed(interaction)
            
            # 成功消息
            if is_additional:
                embed = discord.Embed(
                    title="🌸 借貸成功!債務已累積!",
                    description=(
                        f"呼呼～你又借貸了 **{float(amount):,.2f}** 幽靈幣!\n"
                        f"⚠️ **債務已累積,請注意還款!**"
                    ),
                    color=discord.Color.from_rgb(255, 140, 0)
                )
                embed.add_field(
                    name="📊 債務累積",
                    value=(
                        f"```diff\n"
                        f"- 原有債務: {self.cog.format_number(old_amount)} 幽靈幣\n"
                        f"+ 新增借貸: {float(amount):,.2f} 幽靈幣\n"
                        f"= 總債務: {self.cog.format_number(loan_data['amount'])} 幽靈幣\n"
                        f"```"
                    ),
                    inline=False
                )
            else:
                embed = discord.Embed(
                    title="🌸 借貸成功!",
                    description=f"呼呼～你已借貸 **{float(amount):,.2f}** 幽靈幣!",
                    color=discord.Color.from_rgb(255, 215, 0)
                )
            
            # 顯示更新後的餘額
            embed.add_field(
                name="💰 你的最新餘額",
                value=(
                    f"```yaml\n"
                    f"手頭餘額: {balance[self.guild_id][self.user_id]:,.2f} 幽靈幣\n"
                    f"```"
                ),
                inline=False
            )
            
            due_date = datetime.fromisoformat(loan_data["due_date"])
            embed.add_field(
                name="📋 借貸詳情",
                value=(
                    f"```yaml\n"
                    f"總借貸: {self.cog.format_number(loan_data['amount'])} 幽靈幣\n"
                    f"利息率: 10%\n"
                    f"需還款: {self.cog.format_number(loan_data['amount'] * 1.1)} 幽靈幣\n"
                    f"截止日期: {due_date.strftime('%Y-%m-%d %H:%M')}\n"
                    f"```"
                ),
                inline=False
            )
            embed.add_field(
                name="⚠️ 注意",
                value="• 逾期未還將利息提升至20%\n• 逾期超過7天將金額×4",
                inline=False
            )
            embed.set_footer(text="借貸需謹慎 · 幽幽子")
            await interaction.followup.send(embed=embed, ephemeral=True)
            
            logger.info(f"📜 用戶 {self.user_id} 借貸 {float(amount):.2f} (總: {loan_data['amount']:.2f})")
            
        except Exception as e:
            logger.error(f"❌ 借貸失敗: {e}", exc_info=True)
            try:
                await interaction.followup.send("❌ 借貸時發生錯誤，請稍後再試", ephemeral=True)
            except:
                pass


def setup(bot: discord.Bot):
    """註冊櫻花金庫"""
    bot.add_cog(ServerBank(bot))
    logger.info("🌸 櫻花金庫模組已載入")
