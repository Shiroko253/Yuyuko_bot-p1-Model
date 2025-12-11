import discord
from discord.ext import commands
from discord.ui import View, Button, Modal, InputText
import math
import logging
from decimal import Decimal

logger = logging.getLogger("SakuraBot.Shop")

SHOP_COLOR = discord.Color.from_rgb(255, 182, 193)  # 櫻花粉
ITEMS_PER_PAGE = 5  # 每頁顯示商品數量


def calc_total_price(price: float, tax_percent: float) -> float:
    """計算含稅總價"""
    return round(price + price * (tax_percent / 100), 2)


class Shop(commands.Cog):
    """
    🌸 幽幽子的貪吃冥界商店 🌸
    購買各種美味供品,讓幽幽子和你的靈魂都滿足
    """
    
    def __init__(self, bot: discord.Bot):
        self.bot = bot
        self.data_manager = bot.data_manager
        logger.info("🌸 商店指令已於櫻花樹下甦醒")

    @discord.slash_command(
        name="shop",
        description="🌸 幽幽子的貪吃冥界商店～購買美味供品讓靈魂愉悅"
    )
    async def shop(self, ctx: discord.ApplicationContext):
        """幽幽子的冥界商店,販售各種美味供品"""
        
        try:
            # ----------- 載入商品列表 -----------
            config = self.data_manager._load_json("config/config.json", {})
            shop_items = config.get("shop_item", [])
            
            # ----------- 檢查商品是否為空 -----------
            if not shop_items:
                embed = discord.Embed(
                    title="🌸 商店空空如也",
                    description=(
                        "哎呀～商店裡沒有供品了!\n"
                        "幽幽子都快餓扁了…請管理員補貨!"
                    ),
                    color=discord.Color.red()
                )
                embed.set_footer(text="商店暫時關閉 · 幽幽子")
                await ctx.respond(embed=embed, ephemeral=True)
                return

            # ----------- 計算分頁 -----------
            total_pages = max(1, math.ceil(len(shop_items) / ITEMS_PER_PAGE))
            
            # ----------- 創建分頁視圖 -----------
            view = ShopPagesView(ctx, shop_items, total_pages, self.data_manager, self)
            embed = view.get_embed()
            
            await ctx.respond(embed=embed, view=view)
            logger.info(f"🛒 {ctx.user.name} 打開了商店")
            
        except Exception as e:
            logger.error(f"❌ 商店開啟失敗: {e}", exc_info=True)
            embed = discord.Embed(
                title="❌ 商店開啟失敗",
                description=(
                    "哎呀,幽幽子的商店好像關門了...\n"
                    "請聯絡管理員檢查 `config/config.json`!"
                ),
                color=discord.Color.dark_red()
            )
            embed.set_footer(text="術式受阻,請稍後重試 · 幽幽子")
            await ctx.respond(embed=embed, ephemeral=True)


class ShopPagesView(View):
    """商店分頁視圖"""
    
    def __init__(
        self, 
        ctx: discord.ApplicationContext, 
        shop_items: list, 
        total_pages: int, 
        data_manager,
        cog: Shop
    ):
        super().__init__(timeout=120)
        self.ctx = ctx
        self.shop_items = shop_items
        self.total_pages = total_pages
        self.current_page = 1
        self.data_manager = data_manager
        self.cog = cog
        self.message = None
        self.update_buttons()

    def get_embed(self) -> discord.Embed:
        """生成當前頁面的 Embed"""
        embed = discord.Embed(
            title="🍡 幽幽子的貪吃冥界商店 🍡",
            description=(
                "呼呼～冥界主人幽幽子為你呈上今日美味供品!\n"
                "快來選購讓靈魂愉悅的美食吧～\n\n"
                "💡 **使用說明**: 點擊「選購」按鈕輸入商品編號和數量"
            ),
            color=SHOP_COLOR,
            timestamp=discord.utils.utcnow()
        )
        
        # ----------- 顯示當前頁商品 -----------
        start = (self.current_page - 1) * ITEMS_PER_PAGE
        end = start + ITEMS_PER_PAGE
        
        for i, item in enumerate(self.shop_items[start:end], start=start + 1):
            price = item.get("price", 0)
            tax = item.get("tax", 0)
            total = calc_total_price(price, tax)
            mp = item.get("MP", 0)
            
            embed.add_field(
                name=f"🍽️ 編號 {i} - {item.get('name', '未命名供品')}",
                value=(
                    f"```yaml\n"
                    f"單價: {price:,} 幽靈幣\n"
                    f"稅收: {tax}%\n"
                    f"合計: {total:,} 幽靈幣\n"
                    f"效果: 消除壓力 {mp} 點\n"
                    f"```"
                ),
                inline=False
            )
        
        embed.set_footer(
            text=f"第 {self.current_page} / {self.total_pages} 頁 ｜ 幽幽子：吃飽飽才有力氣賞花呢～",
            icon_url=self.cog.bot.user.avatar.url if self.cog.bot.user.avatar else None
        )
        
        return embed

    def update_buttons(self):
        """更新按鈕狀態"""
        self.clear_items()
        
        # 第一排: 翻頁按鈕
        if self.current_page > 1:
            prev_button = Button(
                label="上一頁",
                style=discord.ButtonStyle.secondary,
                emoji="⬅️",
                row=0
            )
            prev_button.callback = self.prev_page
            self.add_item(prev_button)
        
        if self.current_page < self.total_pages:
            next_button = Button(
                label="下一頁",
                style=discord.ButtonStyle.secondary,
                emoji="➡️",
                row=0
            )
            next_button.callback = self.next_page
            self.add_item(next_button)
        
        # 第二排: 功能按鈕
        buy_button = Button(
            label="選購",
            style=discord.ButtonStyle.success,
            emoji="🛒",
            row=1
        )
        buy_button.callback = self.start_buy
        self.add_item(buy_button)
        
        close_button = Button(
            label="關閉商店",
            style=discord.ButtonStyle.danger,
            emoji="❌",
            row=1
        )
        close_button.callback = self.close_shop
        self.add_item(close_button)

    async def prev_page(self, interaction: discord.Interaction):
        """上一頁"""
        if interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message(
                "呀啦呀啦～這不是你的商店頁面哦!",
                ephemeral=True
            )
            return
        
        if self.current_page > 1:
            self.current_page -= 1
            self.update_buttons()
            await interaction.response.edit_message(
                embed=self.get_embed(),
                view=self
            )

    async def next_page(self, interaction: discord.Interaction):
        """下一頁"""
        if interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message(
                "呀啦呀啦～這不是你的商店頁面哦!",
                ephemeral=True
            )
            return
        
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.update_buttons()
            await interaction.response.edit_message(
                embed=self.get_embed(),
                view=self
            )

    async def start_buy(self, interaction: discord.Interaction):
        """開始購買流程 - 顯示 Modal"""
        if interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message(
                "呀啦呀啦～這不是你的商店頁面哦!",
                ephemeral=True
            )
            return
        
        # 顯示 Modal 讓用戶輸入商品編號和數量
        modal = BuyModal(self.ctx, self.shop_items, self.data_manager, self.cog)
        await interaction.response.send_modal(modal)
    
    async def close_shop(self, interaction: discord.Interaction):
        """關閉商店"""
        if interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message(
                "呀啦呀啦～這不是你的商店頁面哦!",
                ephemeral=True
            )
            return
        
        # 禁用所有按鈕
        for item in self.children:
            item.disabled = True
        
        embed = discord.Embed(
            title="🌸 商店已關閉",
            description=(
                "呼呼～感謝光臨幽幽子的商店!\n"
                "櫻花樹下歡迎你隨時再來～"
            ),
            color=SHOP_COLOR
        )
        embed.set_footer(
            text="期待下次見面 · 幽幽子",
            icon_url=self.cog.bot.user.avatar.url if self.cog.bot.user.avatar else None
        )
        
        await interaction.response.edit_message(embed=embed, view=self)
        logger.info(f"🚪 {interaction.user.name} 關閉了商店")


class BuyModal(Modal):
    """購買 Modal - 輸入商品編號和數量"""
    
    def __init__(
        self, 
        ctx: discord.ApplicationContext, 
        shop_items: list, 
        data_manager,
        cog: Shop
    ):
        super().__init__(title="🌸 幽幽子的商店購物車")
        self.ctx = ctx
        self.shop_items = shop_items
        self.data_manager = data_manager
        self.cog = cog
        
        self.add_item(InputText(
            label="商品編號",
            placeholder="請輸入商品編號 (例如: 1)",
            style=discord.InputTextStyle.short,
            required=True,
            min_length=1,
            max_length=5
        ))
        
        self.add_item(InputText(
            label="購買數量",
            placeholder="請輸入購買數量 (例如: 1)",
            style=discord.InputTextStyle.short,
            required=True,
            min_length=1,
            max_length=5
        ))
    
    async def callback(self, interaction: discord.Interaction):
        try:
            # ----------- 解析輸入 -----------
            try:
                item_number = int(self.children[0].value.strip())
                quantity = int(self.children[1].value.strip())
                
                if quantity <= 0:
                    raise ValueError("數量必須大於0")
                
            except ValueError:
                await interaction.response.send_message(
                    embed=discord.Embed(
                        title="❌ 輸入格式錯誤",
                        description="請輸入有效的數字!",
                        color=discord.Color.red()
                    ),
                    ephemeral=True
                )
                return
            
            # ----------- 檢查商品是否存在 -----------
            item_index = item_number - 1
            if item_index < 0 or item_index >= len(self.shop_items):
                await interaction.response.send_message(
                    embed=discord.Embed(
                        title="🌸 商品不存在",
                        description=f"呼呼～編號 `{item_number}` 沒有對應的供品哦!",
                        color=discord.Color.orange()
                    ),
                    ephemeral=True
                )
                return
            
            item = self.shop_items[item_index]
            
            # ----------- 計算總價 -----------
            unit_price = item.get("price", 0)
            tax = item.get("tax", 0)
            unit_total = calc_total_price(unit_price, tax)
            total_price = round(unit_total * quantity, 2)
            
            # ----------- 檢查餘額 -----------
            guild_id = str(self.ctx.guild.id)
            user_id = str(self.ctx.author.id)
            
            balance = self.data_manager._load_json("economy/balance.json", {})
            
            if guild_id not in balance:
                balance[guild_id] = {}
            if user_id not in balance[guild_id]:
                balance[guild_id][user_id] = 0.0
            
            user_balance = balance[guild_id][user_id]
            
            if user_balance < total_price:
                await interaction.response.send_message(
                    embed=discord.Embed(
                        title="🌸 餘額不足",
                        description=(
                            f"哎呀,購買需要 **{total_price:,}** 幽靈幣,\n"
                            f"但你只有 **{user_balance:,}** 幽靈幣呢...\n\n"
                            f"快去賺錢或從個人金庫取錢吧!"
                        ),
                        color=discord.Color.red()
                    ),
                    ephemeral=True
                )
                return
            
            # ----------- 顯示確認購買 -----------
            await interaction.response.defer()
            
            confirm_embed = discord.Embed(
                title=f"🍽️ 確認購買",
                description=(
                    f"**商品**: {item.get('name', '未命名供品')}\n"
                    f"**編號**: `{item_number}`\n"
                    f"**數量**: `{quantity}` 個\n"
                    f"**單價**: `{unit_total:,}` 幽靈幣/個\n"
                    f"**總價**: `{total_price:,}` 幽靈幣\n"
                    f"**效果**: 消除壓力 `{item.get('MP', 0) * quantity}` 點\n\n"
                    f"幽幽子：這些供品看起來好美味…你確定要買下它們嗎?"
                ),
                color=SHOP_COLOR,
                timestamp=discord.utils.utcnow()
            )
            confirm_embed.add_field(
                name="💰 你的餘額",
                value=f"```yaml\n目前餘額: {user_balance:,} 幽靈幣\n購買後餘額: {user_balance - total_price:,} 幽靈幣\n```",
                inline=False
            )
            
            view = ConfirmBuyView(
                self.ctx, 
                item, 
                quantity,
                total_price, 
                self.data_manager,
                self.cog
            )
            
            await interaction.followup.send(embed=confirm_embed, view=view, ephemeral=True)
            
        except Exception as e:
            logger.error(f"❌ 購買流程失敗: {e}", exc_info=True)
            try:
                await interaction.response.send_message(
                    "❌ 購買流程發生錯誤,請稍後再試!",
                    ephemeral=True
                )
            except:
                await interaction.followup.send(
                    "❌ 購買流程發生錯誤,請稍後再試!",
                    ephemeral=True
                )


class ConfirmBuyView(View):
    """購買確認視圖"""
    
    def __init__(
        self, 
        ctx: discord.ApplicationContext, 
        item: dict, 
        quantity: int,
        total_price: float, 
        data_manager,
        cog: Shop
    ):
        super().__init__(timeout=60)
        self.ctx = ctx
        self.item = item
        self.quantity = quantity
        self.total_price = total_price
        self.data_manager = data_manager
        self.cog = cog

    @discord.ui.button(label="確認購買", style=discord.ButtonStyle.green, emoji="✅")
    async def confirm(self, button: Button, interaction: discord.Interaction):
        """確認購買"""
        if interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message(
                "呀啦呀啦～這不是你的購買確認哦!",
                ephemeral=True
            )
            return
        
        try:
            await interaction.response.defer()
            
            guild_id = str(self.ctx.guild.id)
            user_id = str(self.ctx.author.id)
            
            # ----------- 扣款 -----------
            balance = self.data_manager._load_json("economy/balance.json", {})
            
            if guild_id not in balance:
                balance[guild_id] = {}
            if user_id not in balance[guild_id]:
                balance[guild_id][user_id] = 0.0
            
            user_balance = balance[guild_id][user_id]
            
            # 再次檢查餘額
            if user_balance < self.total_price:
                await interaction.followup.send(
                    "❌ 餘額不足,購買失敗!",
                    ephemeral=True
                )
                return
            
            # 扣除金額
            balance[guild_id][user_id] -= self.total_price
            new_balance = balance[guild_id][user_id]
            
            # 保存
            self.data_manager._save_json("economy/balance.json", balance)
            
            # ----------- 記錄交易 -----------
            transactions = self.data_manager._load_json("economy/transactions.json", {})
            if guild_id not in transactions:
                transactions[guild_id] = []
            
            from datetime import datetime
            from zoneinfo import ZoneInfo
            
            transactions[guild_id].append({
                "user_id": user_id,
                "amount": -self.total_price,
                "type": "shop_purchase",
                "item": self.item.get("name"),
                "quantity": self.quantity,
                "timestamp": datetime.now(ZoneInfo('Asia/Taipei')).isoformat()
            })
            
            self.data_manager._save_json("economy/transactions.json", transactions)
            
            # ----------- 購買成功 -----------
            success_embed = discord.Embed(
                title="🎉 購買成功!",
                description=(
                    f"呼呼～你成功購買了 **{self.quantity}** 個 **{self.item.get('name')}**!\n"
                    f"供品已經送到了,要放入背包還是直接食用呢?"
                ),
                color=discord.Color.from_rgb(144, 238, 144)
            )
            success_embed.add_field(
                name="💰 交易詳情",
                value=(
                    f"```yaml\n"
                    f"花費金額: {self.total_price:,} 幽靈幣\n"
                    f"剩餘餘額: {new_balance:,} 幽靈幣\n"
                    f"```"
                ),
                inline=False
            )
            
            view = UseOrBackpackView(self.item, self.quantity, self.cog)
            
            await interaction.followup.send(embed=success_embed, view=view, ephemeral=True)
            
            # 禁用確認按鈕
            for item in self.children:
                item.disabled = True
            
            logger.info(
                f"💰 {interaction.user.name} 購買了 {self.quantity} 個 {self.item.get('name')}, "
                f"花費 {self.total_price:.2f} 幽靈幣"
            )
            
        except Exception as e:
            logger.error(f"❌ 購買執行失敗: {e}", exc_info=True)
            await interaction.followup.send(
                "❌ 購買執行失敗,請稍後再試!",
                ephemeral=True
            )

    @discord.ui.button(label="取消", style=discord.ButtonStyle.red, emoji="❌")
    async def cancel(self, button: Button, interaction: discord.Interaction):
        """取消購買"""
        if interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message(
                "呀啦呀啦～這不是你的購買確認哦!",
                ephemeral=True
            )
            return
        
        embed = discord.Embed(
            title="🌸 取消購買",
            description="呼呼～好吧,供品留給下次吧!",
            color=SHOP_COLOR
        )
        embed.set_footer(text="歡迎隨時再來 · 幽幽子")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
        # 禁用按鈕
        for item in self.children:
            item.disabled = True


class UseOrBackpackView(View):
    """使用或放入背包視圖"""
    
    def __init__(self, item: dict, quantity: int, cog: Shop):
        super().__init__(timeout=60)
        self.item = item
        self.quantity = quantity
        self.cog = cog

    @discord.ui.button(label="直接食用", style=discord.ButtonStyle.primary, emoji="🍡")
    async def eat(self, button: Button, interaction: discord.Interaction):
        """直接食用"""
        mp = self.item.get("MP", 0) * self.quantity
        
        # TODO: 實作增加 MP 邏輯
        
        embed = discord.Embed(
            title="🍡 享用美味!",
            description=(
                f"呀～真好吃!\n"
                f"你食用了 **{self.quantity}** 個 **{self.item.get('name')}**,\n"
                f"壓力消除了 **{mp}** 點!\n\n"
                f"櫻花樹下的美食,果然是最棒的～"
            ),
            color=discord.Color.from_rgb(144, 238, 144)
        )
        embed.set_footer(text="美味無比 · 幽幽子")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
        # 禁用按鈕
        for item in self.children:
            item.disabled = True
        
        logger.info(f"🍽️ {interaction.user.name} 食用了 {self.quantity} 個 {self.item.get('name')}")

    @discord.ui.button(label="放入背包", style=discord.ButtonStyle.secondary, emoji="🎒")
    async def backpack(self, button: Button, interaction: discord.Interaction):
        """放入背包"""
        
        # TODO: 實作背包邏輯
        
        embed = discord.Embed(
            title="🎒 存入背包!",
            description=(
                f"供品已放入背包,等下再慢慢享用吧～\n"
                f"記得不要放太久哦,不然會壞掉的!"
            ),
            color=SHOP_COLOR
        )
        embed.set_footer(text="妥善保管 · 幽幽子")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
        # 禁用按鈕
        for item in self.children:
            item.disabled = True
        
        logger.info(f"🎒 {interaction.user.name} 將 {self.quantity} 個 {self.item.get('name')} 放入背包")


def setup(bot: discord.Bot):
    """將商店術式註冊於幽幽子的靈魂"""
    bot.add_cog(Shop(bot))
    logger.info("🌸 商店模組已於櫻花樹下綻放完成")
