import discord
from discord.ext import commands
from discord.ui import View, Button
import math
import logging

SHOP_COLOR = discord.Color.from_rgb(255, 182, 193)  # 櫻花粉/幽幽子貪吃色
ITEMS_PER_PAGE = 5  # 每頁顯示商品數量

def calc_total_price(price, tax_percent):
    return round(price + price * (tax_percent / 100), 2)

class Shop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(
        name="shop",
        description="幽幽子的貪吃冥界商店（分頁瀏覽）"
    )
    async def shop(self, ctx: discord.ApplicationContext):
        # 讀取商品列表
        shop_items = self.bot.data_manager._load_json("config/config.json").get("shop_item", [])
        total_pages = max(1, math.ceil(len(shop_items) / ITEMS_PER_PAGE))
        current_page = 1

        def get_embed(page):
            embed = discord.Embed(
                title="🍡 幽幽子的貪吃冥界商店 🍡",
                description="冥界主人幽幽子為你呈上今日美味供品～\n快來選購讓靈魂愉悅的美食吧！",
                color=SHOP_COLOR
            )
            start = (page - 1) * ITEMS_PER_PAGE
            end = start + ITEMS_PER_PAGE
            for i, item in enumerate(shop_items[start:end], start=1):
                price = item["price"]
                tax = item["tax"]
                total = calc_total_price(price, tax)
                embed.add_field(
                    name=f"{item['name']} 🍽️",
                    value=(
                        f"價格：{price}幽靈幣\n"
                        f"稅收：{tax}%\n"
                        f"合計：{total}幽靈幣\n"
                        f"消除壓力：{item['MP']}\n"
                        f"選購編號：`{start + i}`"
                    ),
                    inline=False
                )
            embed.set_footer(text=f"第 {page} / {total_pages} 頁｜幽幽子：吃飽飽才有力氣賞花呢～")
            return embed

        # 分頁控制 UI
        class ShopPages(View):
            def __init__(self, page):
                super().__init__(timeout=120)
                self.page = page
                self.update_buttons()

            def update_buttons(self):
                self.clear_items()
                if self.page > 1:
                    self.add_item(Button(label="上一頁", style=discord.ButtonStyle.secondary, emoji="⬅️", custom_id="prev"))
                if self.page < total_pages:
                    self.add_item(Button(label="下一頁", style=discord.ButtonStyle.secondary, emoji="➡️", custom_id="next"))
                self.add_item(Button(label="選購", style=discord.ButtonStyle.success, emoji="🛒", custom_id="buy"))

            async def interaction_check(self, interaction: discord.Interaction):
                return interaction.user == ctx.author

            @discord.ui.button(label="上一頁", style=discord.ButtonStyle.secondary, emoji="⬅️", custom_id="prev", row=0)
            async def prev(self, button, interaction):
                if self.page > 1:
                    self.page -= 1
                    self.update_buttons()
                    await interaction.response.edit_message(embed=get_embed(self.page), view=self)

            @discord.ui.button(label="下一頁", style=discord.ButtonStyle.secondary, emoji="➡️", custom_id="next", row=0)
            async def next(self, button, interaction):
                if self.page < total_pages:
                    self.page += 1
                    self.update_buttons()
                    await interaction.response.edit_message(embed=get_embed(self.page), view=self)

            @discord.ui.button(label="選購", style=discord.ButtonStyle.success, emoji="🛒", custom_id="buy", row=0)
            async def buy(self, button, interaction):
                await interaction.response.send_message(
                    "請輸入你想購買的商品編號（於60秒內回覆）",
                    ephemeral=True
                )
                def check(m):
                    return m.author == ctx.author and m.channel == ctx.channel

                try:
                    msg = await self.bot.wait_for("message", timeout=60.0, check=check)
                    idx = int(msg.content) - 1
                    if 0 <= idx < len(shop_items):
                        item = shop_items[idx]
                        await show_confirm(interaction, item)
                    else:
                        await ctx.send("幽幽子：這個編號沒有供品喔～", ephemeral=True)
                except Exception as e:
                    await ctx.send("幽幽子：你想太久啦，供品飛走了！", ephemeral=True)

        # 購買確認頁面
        async def show_confirm(interaction, item):
            price = item["price"]
            tax = item["tax"]
            total = calc_total_price(price, tax)
            embed = discord.Embed(
                title=f"🍽️ 確認購買：{item['name']}",
                description=(
                    f"價格：{price}幽靈幣\n"
                    f"稅收：{tax}%\n"
                    f"合計：{total}幽靈幣\n"
                    f"消除壓力：{item['MP']}\n\n"
                    f"幽幽子：這份供品看起來好美味…你確定要買下它嗎？"
                ),
                color=SHOP_COLOR
            )
            class ConfirmBuy(View):
                def __init__(self):
                    super().__init__(timeout=60)

                @discord.ui.button(label="確認購買", style=discord.ButtonStyle.green, emoji="✅")
                async def confirm(self, button, interaction):
                    # 這裡要加扣錢/檢查餘額/更新資料邏輯
                    await interaction.response.send_message(
                        f"幽幽子：恭喜你獲得了「{item['name']}」！要放入背包還是直接食用呢？",
                        view=UseOrBackpack(item),
                        ephemeral=True
                    )

                @discord.ui.button(label="取消", style=discord.ButtonStyle.red, emoji="❌")
                async def cancel(self, button, interaction):
                    await interaction.response.send_message("幽幽子：好吧～供品留給下次吧！", ephemeral=True)

            await interaction.response.send_message(embed=embed, view=ConfirmBuy(), ephemeral=True)

        # 使用方式選擇
        class UseOrBackpack(View):
            def __init__(self, item):
                super().__init__(timeout=60)
                self.item = item

            @discord.ui.button(label="直接食用", style=discord.ButtonStyle.primary, emoji="🍡")
            async def eat(self, button, interaction):
                # 增加MP/消耗物品邏輯
                await interaction.response.send_message(f"幽幽子：呀～真好吃！你的壓力消除了 {self.item['MP']} 點！", ephemeral=True)

            @discord.ui.button(label="放入背包", style=discord.ButtonStyle.secondary, emoji="🎒")
            async def backpack(self, button, interaction):
                # 放入背包邏輯
                await interaction.response.send_message(f"幽幽子：供品已放入背包，等下再慢慢享用吧～", ephemeral=True)

        await ctx.respond(embed=get_embed(current_page), view=ShopPages(current_page), ephemeral=False)

def setup(bot):
    bot.add_cog(Shop(bot))