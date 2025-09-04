import discord
from discord.ext import commands
from discord.ui import View, Modal, InputText
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from zoneinfo import ZoneInfo

class ServerBank(commands.Cog):
    """
    ✿ 幽幽子的櫻花金庫 ✿
    冥界國庫、個人金庫、借貸、存取款──幽幽子陪你守護每一枚幽靈幣～
    """
    def __init__(self, bot):
        self.bot = bot
        self.data_manager = bot.data_manager
        self.tz = ZoneInfo('Asia/Taipei')

    def format_number(self, num):
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

    def log_transaction(self, guild_id, user_id, amount, transaction_type):
        transactions = self.data_manager.load_json("economy/transactions.json")
        if guild_id not in transactions:
            transactions[guild_id] = []
        transactions[guild_id].append({
            "user_id": user_id,
            "amount": float(amount),
            "type": transaction_type,
            "timestamp": datetime.now(self.tz).isoformat()
        })
        self.data_manager.save_json("economy/transactions.json", transactions)

    def initialize_user_data(self, balance, personal_bank, guild_id, user_id):
        if guild_id not in balance:
            balance[guild_id] = {}
        if user_id not in balance[guild_id] or not isinstance(balance[guild_id][user_id], (int, float)):
            balance[guild_id][user_id] = 0.0
        if guild_id not in personal_bank:
            personal_bank[guild_id] = {}
        if user_id not in personal_bank[guild_id] or not isinstance(personal_bank[guild_id][user_id], (int, float)):
            personal_bank[guild_id][user_id] = 0.0
        return balance, personal_bank

    def check_loan_status(self, server_config, guild_id, user_id):
        if guild_id not in server_config or "loans" not in server_config[guild_id]:
            return None
        if user_id not in server_config[guild_id]["loans"]:
            return None
        loan = server_config[guild_id]["loans"][user_id]
        if loan.get("repaid"):
            return None
        due_date = datetime.fromisoformat(loan["due_date"]).replace(tzinfo=self.tz)
        current_date = datetime.now(self.tz)
        if current_date > due_date and loan["interest_rate"] == 0.1:
            loan["interest_rate"] = 0.2
            server_config[guild_id]["loans"][user_id] = loan
            self.data_manager.save_json("config/server_config.json", server_config)
        return loan

    @discord.slash_command(name="server_bank", description="與幽幽子的金庫互動，存錢、取錢或借貸～")
    async def server_bank(self, ctx: discord.ApplicationContext):
        guild_id = str(ctx.guild.id)
        user_id = str(ctx.author.id)
        server_name = ctx.guild.name

        balance = self.data_manager.load_json("economy/balance.json")
        personal_bank = self.data_manager.load_json("economy/personal_bank.json")
        server_config = self.data_manager.load_json("config/server_config.json")

        balance, personal_bank = self.initialize_user_data(balance, personal_bank, guild_id, user_id)
        if guild_id not in server_config:
            server_config[guild_id] = {}
        if "server_bank" not in server_config[guild_id]:
            server_config[guild_id]["server_bank"] = {
                "total": 0.0,
                "contributions": {}
            }

        user_balance = balance[guild_id][user_id]
        personal_bank_balance = personal_bank[guild_id][user_id]
        server_bank_balance = server_config[guild_id]["server_bank"]["total"]

        loan = self.check_loan_status(server_config, guild_id, user_id)
        loan_info = ""
        if loan:
            due_date = datetime.fromisoformat(loan["due_date"]).replace(tzinfo=self.tz)
            amount_with_interest = round(loan["amount"] * (1 + loan["interest_rate"]), 2)
            loan_info = (
                f"\n\n⚠️ 你有一筆未還款的借貸！\n"
                f"借貸金額：{self.format_number(loan['amount'])} 幽靈幣\n"
                f"當前利息率：{loan['interest_rate'] * 100:.0f}%\n"
                f"需還款金額：{self.format_number(amount_with_interest)} 幽靈幣\n"
                f"還款截止日期：{due_date.strftime('%Y-%m-%d %H:%M:%S')}"
            )

        embed = discord.Embed(
            title="🌸 幽幽子的金庫 🌸",
            description=(
                f"歡迎來到 **{server_name}** 的金庫，你是要存錢、取錢還是借貸？\n\n"
                f"你的餘額：{self.format_number(user_balance)} 幽靈幣\n"
                f"你的個人金庫：{self.format_number(personal_bank_balance)} 幽靈幣\n"
                f"國庫餘額：{self.format_number(server_bank_balance)} 幽靈幣"
                f"{loan_info}"
            ),
            color=discord.Color.from_rgb(255, 182, 193)
        )

        view = self.BankButtons(self, ctx, guild_id, user_id, bool(loan))
        msg = await ctx.respond(embed=embed, view=view)
        resolved_msg = await msg.original_response()
        view.message = resolved_msg

    class BankButtons(View):
        """
        ✿ 幽幽子的金庫操作按鈕 ✿
        存款、取款、借貸、還款──全部都在櫻花下進行～
        """
        def __init__(self, cog, ctx, guild_id, user_id, has_loan):
            super().__init__(timeout=60)
            self.cog = cog
            self.ctx = ctx
            self.guild_id = guild_id
            self.user_id = user_id
            self.has_loan = has_loan
            self.message = None
            self.interaction_completed = False

        async def interaction_check(self, interaction: discord.Interaction) -> bool:
            if interaction.user.id != self.ctx.author.id:
                await interaction.response.send_message("這不是你的金庫操作哦～", ephemeral=True)
                return False
            if self.interaction_completed:
                await interaction.response.send_message("操作已完成，請重新執行 /server_bank！", ephemeral=True)
                return False
            return True

        async def on_timeout(self):
            for item in self.children:
                item.disabled = True
            embed = discord.Embed(
                title="🌸 金庫操作已結束 🌸",
                description="操作已超時，請重新執行 /server_bank 命令！",
                color=discord.Color.red()
            )
            if self.message:
                await self.message.edit(embed=embed, view=self)

        @discord.ui.button(label="取錢", style=discord.ButtonStyle.success)
        async def withdraw(self, button: discord.ui.Button, interaction: discord.Interaction):
            await interaction.response.send_modal(self.cog.WithdrawModal(self, self.guild_id, self.user_id))

        @discord.ui.button(label="存錢", style=discord.ButtonStyle.primary)
        async def deposit(self, button: discord.ui.Button, interaction: discord.Interaction):
            await interaction.response.send_modal(self.cog.DepositModal(self, self.guild_id, self.user_id))

        @discord.ui.button(label="借貸", style=discord.ButtonStyle.danger, disabled=False)
        async def borrow(self, button: discord.ui.Button, interaction: discord.Interaction):
            if self.has_loan:
                await interaction.response.send_message("你已經有一筆借貸尚未還清，無法再借款哦～", ephemeral=True)
                return
            await interaction.response.send_modal(self.cog.BorrowModal(self, self.guild_id, self.user_id))

        @discord.ui.button(label="還款", style=discord.ButtonStyle.green, disabled=True)
        async def repay(self, button: discord.ui.Button, interaction: discord.Interaction):
            if not self.has_loan:
                await interaction.response.send_message("你目前沒有未還款的借貸哦～", ephemeral=True)
                return
            
            await interaction.response.defer(ephemeral=True)
            server_config = self.cog.data_manager.load_json("config/server_config.json")
            loan = self.cog.check_loan_status(server_config, self.guild_id, self.user_id)
            
            if not loan or loan.get("repaid"):
                await interaction.followup.send(embed=discord.Embed(
                    title="🌸 無需還款！🌸",
                    description="你目前沒有未還款的借貸哦～",
                    color=discord.Color.red()
                ), ephemeral=True)
                return
            
            balance = self.cog.data_manager.load_json("economy/balance.json")
            user_balance = balance[self.guild_id][self.user_id]
            amount_with_interest = round(loan["amount"] * (1 + loan["interest_rate"]), 2)
            
            if user_balance < amount_with_interest:
                await interaction.followup.send(embed=discord.Embed(
                    title="🌸 餘額不足！🌸",
                    description=f"你需要 {self.cog.format_number(amount_with_interest)} 幽靈幣來還款，但你的餘額只有 {self.cog.format_number(user_balance)} 幽靈幣哦～",
                    color=discord.Color.red()
                ), ephemeral=True)
                return
            
            balance[self.guild_id][self.user_id] -= amount_with_interest
            server_config[self.guild_id]["server_bank"]["total"] += amount_with_interest
            server_config[self.guild_id]["loans"][self.user_id]["repaid"] = True
            
            self.cog.data_manager.save_json("economy/balance.json", balance)
            self.cog.data_manager.save_json("config/server_config.json", server_config)
            self.cog.log_transaction(self.guild_id, self.user_id, amount_with_interest, "repay")
            
            embed = discord.Embed(
                title="🌸 還款成功！🌸",
                description=(
                    f"你已還款 **{self.cog.format_number(amount_with_interest)} 幽靈幣**（包含利息）～\n\n"
                    f"你的新餘額：{self.cog.format_number(balance[self.guild_id][self.user_id])} 幽靈幣\n"
                    f"國庫新餘額：{self.cog.format_number(server_config[self.guild_id]['server_bank']['total'])} 幽靈幣"
                ),
                color=discord.Color.gold()
            )
            self.interaction_completed = True
            for item in self.children:
                item.disabled = True
            if self.message:
                await self.message.edit(embed=embed, view=self)
            await interaction.followup.send(embed=embed, ephemeral=True)

        async def setup_buttons(self):
            # 動態啟用/禁用借貸/還款按鈕
            self.children[2].disabled = self.has_loan  # borrow
            self.children[3].disabled = not self.has_loan  # repay

        async def on_ready(self):
            await self.setup_buttons()

    class WithdrawModal(Modal):
        """
        ✿ 幽幽子的金庫取錢表單 ✿
        輕輕取出幽靈幣，櫻花飄落也為你祝福～
        """
        def __init__(self, parent_view, guild_id, user_id):
            super().__init__(title="幽幽子的金庫 - 取錢", timeout=60)
            self.parent_view = parent_view
            self.guild_id = guild_id
            self.user_id = user_id
            self.add_item(InputText(
                label="輸入取款金額",
                placeholder="輸入你想從個人金庫取出的幽靈幣金額",
                style=discord.InputTextStyle.short
            ))

        async def callback(self, interaction: discord.Interaction):
            await interaction.response.defer(ephemeral=True)
            cog = self.parent_view.cog
            try:
                amount = Decimal(self.children[0].value).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                amount = float(amount)
                if amount <= 0 or amount > 1e20:
                    await interaction.followup.send(embed=discord.Embed(
                        title="🌸 無效金額！🌸",
                        description="金額必須大於 0 且不超過 1e20 幽靈幣哦～",
                        color=discord.Color.red()
                    ), ephemeral=True)
                    return
                balance = cog.data_manager.load_json("economy/balance.json")
                personal_bank = cog.data_manager.load_json("economy/personal_bank.json")
                balance, personal_bank = cog.initialize_user_data(balance, personal_bank, self.guild_id, self.user_id)
                personal_bank_balance = personal_bank[self.guild_id][self.user_id]
                if amount > personal_bank_balance:
                    await interaction.followup.send(embed=discord.Embed(
                        title="🌸 個人金庫餘額不足！🌸",
                        description=f"你的個人金庫只有 {cog.format_number(personal_bank_balance)} 幽靈幣，無法取出 {cog.format_number(amount)} 哦～",
                        color=discord.Color.red()
                    ), ephemeral=True)
                    return
                personal_bank[self.guild_id][self.user_id] -= amount
                balance[self.guild_id][self.user_id] += amount
                cog.data_manager.save_json("economy/balance.json", balance)
                cog.data_manager.save_json("economy/personal_bank.json", personal_bank)
                cog.log_transaction(self.guild_id, self.user_id, amount, "withdraw")
                embed = discord.Embed(
                    title="🌸 取款成功！🌸",
                    description=(
                        f"你從個人金庫取出了 **{cog.format_number(amount)} 幽靈幣**～\n\n"
                        f"你的新餘額：{cog.format_number(balance[self.guild_id][self.user_id])} 幽靈幣\n"
                        f"你的個人金庫新餘額：{cog.format_number(personal_bank[self.guild_id][self.user_id])} 幽靈幣"
                    ),
                    color=discord.Color.gold()
                )
                self.parent_view.interaction_completed = True
                for item in self.parent_view.children:
                    item.disabled = True
                if self.parent_view.message:
                    await self.parent_view.message.edit(embed=embed, view=self.parent_view)
                await interaction.followup.send(embed=embed, ephemeral=True)
            except ValueError:
                await interaction.followup.send(embed=discord.Embed(
                    title="🌸 無效金額！🌸",
                    description="請輸入有效的數字金額哦～",
                    color=discord.Color.red()
                ), ephemeral=True)
            except Exception as e:
                await interaction.followup.send(embed=discord.Embed(
                    title="🌸 系統錯誤！🌸",
                    description=f"取錢時發生錯誤：{str(e)}，請稍後再試～",
                    color=discord.Color.red()
                ), ephemeral=True)

    class DepositModal(Modal):
        """
        ✿ 幽幽子的金庫存錢表單 ✿
        櫻花飄落，靈魂也跟著豐盈～
        """
        def __init__(self, parent_view, guild_id, user_id):
            super().__init__(title="幽幽子的金庫 - 存錢", timeout=60)
            self.parent_view = parent_view
            self.guild_id = guild_id
            self.user_id = user_id
            self.add_item(InputText(
                label="輸入存款金額",
                placeholder="輸入你想存入個人金庫的幽靈幣金額",
                style=discord.InputTextStyle.short
            ))

        async def callback(self, interaction: discord.Interaction):
            await interaction.response.defer(ephemeral=True)
            cog = self.parent_view.cog
            try:
                amount = Decimal(self.children[0].value).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                amount = float(amount)
                if amount <= 0 or amount > 1e20:
                    await interaction.followup.send(embed=discord.Embed(
                        title="🌸 無效金額！🌸",
                        description="金額必須大於 0 且不超過 1e20 幽靈幣哦～",
                        color=discord.Color.red()
                    ), ephemeral=True)
                    return
                balance = cog.data_manager.load_json("economy/balance.json")
                personal_bank = cog.data_manager.load_json("economy/personal_bank.json")
                balance, personal_bank = cog.initialize_user_data(balance, personal_bank, self.guild_id, self.user_id)
                user_balance = balance[self.guild_id][self.user_id]
                if amount > user_balance:
                    await interaction.followup.send(embed=discord.Embed(
                        title="🌸 餘額不足！🌸",
                        description=f"你的餘額只有 {cog.format_number(user_balance)} 幽靈幣，無法存入 {cog.format_number(amount)} 哦～",
                        color=discord.Color.red()
                    ), ephemeral=True)
                    return
                balance[self.guild_id][self.user_id] -= amount
                personal_bank[self.guild_id][self.user_id] += amount
                cog.data_manager.save_json("economy/balance.json", balance)
                cog.data_manager.save_json("economy/personal_bank.json", personal_bank)
                cog.log_transaction(self.guild_id, self.user_id, amount, "deposit")
                embed = discord.Embed(
                    title="🌸 存款成功！🌸",
                    description=(
                        f"你存入了 **{cog.format_number(amount)} 幽靈幣** 到個人金庫～\n\n"
                        f"你的新餘額：{cog.format_number(balance[self.guild_id][self.user_id])} 幽靈幣\n"
                        f"你的個人金庫新餘額：{cog.format_number(personal_bank[self.guild_id][self.user_id])} 幽靈幣"
                    ),
                    color=discord.Color.gold()
                )
                self.parent_view.interaction_completed = True
                for item in self.parent_view.children:
                    item.disabled = True
                if self.parent_view.message:
                    await self.parent_view.message.edit(embed=embed, view=self.parent_view)
                await interaction.followup.send(embed=embed, ephemeral=True)
            except ValueError:
                await interaction.followup.send(embed=discord.Embed(
                    title="🌸 無效金額！🌸",
                    description="請輸入有效的數字金額哦～",
                    color=discord.Color.red()
                ), ephemeral=True)
            except Exception as e:
                await interaction.followup.send(embed=discord.Embed(
                    title="🌸 系統錯誤！🌸",
                    description=f"存錢時發生錯誤：{str(e)}，請稍後再試～",
                    color=discord.Color.red()
                ), ephemeral=True)

    class BorrowModal(Modal):
        """
        ✿ 幽幽子的金庫借貸表單 ✿
        向冥界國庫借幽靈幣，記得按時還哦～
        """
        def __init__(self, parent_view, guild_id, user_id):
            super().__init__(title="幽幽子的金庫 - 借貸", timeout=60)
            self.parent_view = parent_view
            self.guild_id = guild_id
            self.user_id = user_id
            self.add_item(InputText(
                label="輸入借貸金額",
                placeholder="輸入你想從國庫借的幽靈幣金額",
                style=discord.InputTextStyle.short
            ))

        async def callback(self, interaction: discord.Interaction):
            await interaction.response.defer(ephemeral=True)
            cog = self.parent_view.cog
            try:
                amount = Decimal(self.children[0].value).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                amount = float(amount)
                if amount <= 0 or amount > 1e20:
                    await interaction.followup.send(embed=discord.Embed(
                        title="🌸 無效金額！🌸",
                        description="金額必須大於 0 且不超過 1e20 幽靈幣哦～",
                        color=discord.Color.red()
                    ), ephemeral=True)
                    return
                balance = cog.data_manager.load_json("economy/balance.json")
                server_config = cog.data_manager.load_json("config/server_config.json")
                server_bank_balance = server_config[self.guild_id]["server_bank"]["total"]
                if amount > server_bank_balance:
                    await interaction.followup.send(embed=discord.Embed(
                        title="🌸 國庫餘額不足！🌸",
                        description=f"國庫只有 {cog.format_number(server_bank_balance)} 幽靈幣，無法借出 {cog.format_number(amount)} 哦～",
                        color=discord.Color.red()
                    ), ephemeral=True)
                    return
                borrowed_at = datetime.now(cog.tz)
                due_date = borrowed_at + timedelta(days=5)
                if "loans" not in server_config[self.guild_id]:
                    server_config[self.guild_id]["loans"] = {}
                server_config[self.guild_id]["loans"][self.user_id] = {
                    "amount": amount,
                    "interest_rate": 0.1,
                    "borrowed_at": borrowed_at.isoformat(),
                    "due_date": due_date.isoformat(),
                    "repaid": False
                }
                server_config[self.guild_id]["server_bank"]["total"] -= amount
                balance[self.guild_id][self.user_id] += amount
                cog.data_manager.save_json("economy/balance.json", balance)
                cog.data_manager.save_json("config/server_config.json", server_config)
                cog.log_transaction(self.guild_id, self.user_id, amount, "borrow")
                embed = discord.Embed(
                    title="🌸 借貸成功！🌸",
                    description=(
                        f"你從國庫借了 **{cog.format_number(amount)} 幽靈幣**～\n"
                        f"初始利息率：10%\n"
                        f"需還款金額：{cog.format_number(amount * 1.1)} 幽靈幣\n"
                        f"還款截止日期：{due_date.strftime('%Y-%m-%d %H:%M:%S')}\n"
                        f"（若逾期未還，利息將翻倍至 20%！）\n\n"
                        f"你的新餘額：{cog.format_number(balance[self.guild_id][self.user_id])} 幽靈幣\n"
                        f"國庫新餘額：{cog.format_number(server_config[self.guild_id]['server_bank']['total'])} 幽靈幣"
                    ),
                    color=discord.Color.gold()
                )
                self.parent_view.interaction_completed = True
                for item in self.parent_view.children:
                    item.disabled = True
                if self.parent_view.message:
                    await self.parent_view.message.edit(embed=embed, view=self.parent_view)
                await interaction.followup.send(embed=embed, ephemeral=True)
            except ValueError:
                await interaction.followup.send(embed=discord.Embed(
                    title="🌸 無效金額！🌸",
                    description="請輸入有效的數字金額哦～",
                    color=discord.Color.red()
                ), ephemeral=True)
            except Exception as e:
                await interaction.followup.send(embed=discord.Embed(
                    title="🌸 系統錯誤！🌸",
                    description=f"借貸時發生錯誤：{str(e)}，請稍後再試～",
                    color=discord.Color.red()
                ), ephemeral=True)

def setup(bot):
    bot.add_cog(ServerBank(bot))