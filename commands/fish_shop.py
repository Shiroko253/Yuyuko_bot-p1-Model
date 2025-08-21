import discord
from discord.ext import commands
from discord import ApplicationContext, Interaction
import asyncio

def calculate_fish_price(fish):
    rarity_prices = {
        "common": (100, 10),
        "uncommon": (350, 15),
        "rare": (7400, 50),
        "legendary": (450000, 100),
        "deify": (3000000, 500),
        "unknown": (100000000, 1000)
    }
    try:
        base_price, weight_multiplier = rarity_prices.get(fish["rarity"], (0, 0))
        size = float(fish["size"])
        return int(base_price + size * weight_multiplier)
    except (KeyError, ValueError, TypeError):
        return 0

class FishShop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(name="fish_shop", description="釣魚商店")
    async def fish_shop(self, ctx: ApplicationContext):
        data_manager = self.bot.data_manager
        file_lock = getattr(self.bot, "file_lock", asyncio.Lock())
        fishingpack_path = "config/fishingpack.json"
        balance_path = "economy/balance.json"
        user_id = str(ctx.user.id)
        guild_id = str(ctx.guild.id)

        await ctx.defer()

        async with file_lock:
            fishingpack_data = data_manager.load_json(fishingpack_path) or {}
            balance_data = data_manager.load_json(balance_path) or {}

        user_fishes = fishingpack_data.get(user_id, {}).get(guild_id, {}).get("fishes", [])
        user_balance = balance_data.get(guild_id, {}).get(user_id, 0)

        class ConfirmSellView(discord.ui.View):
            def __init__(self, fish_index, original_user_id):
                super().__init__(timeout=180)
                self.fish_index = fish_index
                self.original_user_id = original_user_id

            @discord.ui.button(label="確認售出", style=discord.ButtonStyle.green)
            async def confirm_sell(self, button: discord.ui.Button, interaction: Interaction):
                if interaction.user.id != self.original_user_id:
                    await interaction.response.send_message("這不是你的商店，無法操作！", ephemeral=True)
                    return

                fish = user_fishes[self.fish_index]
                price = calculate_fish_price(fish)
                if price == 0:
                    await interaction.response.edit_message(
                        content="漁獲資料錯誤，無法售出！", embed=None, view=None
                    )
                    return

                # 更新資料
                balance_data.setdefault(guild_id, {}).setdefault(user_id, 0)
                balance_data[guild_id][user_id] += price
                user_fishes.pop(self.fish_index)
                fishingpack_data.setdefault(user_id, {}).setdefault(guild_id, {})["fishes"] = user_fishes

                async with file_lock:
                    data_manager.save_json(fishingpack_path, fishingpack_data)
                    data_manager.save_json(balance_path, balance_data)

                if not user_fishes:
                    await interaction.response.edit_message(
                        content=f"成功售出 {fish['name']}，獲得幽靈幣 {price}！目前已無漁獲可販售。",
                        embed=None, view=None
                    )
                    return

                sell_view = FishSellView(self.original_user_id, 0)
                embed = sell_view.get_updated_embed()
                await interaction.response.edit_message(
                    content=f"成功售出 {fish['name']}，獲得幽靈幣 {price}！",
                    embed=embed, view=sell_view
                )

            @discord.ui.button(label="取消", style=discord.ButtonStyle.red)
            async def cancel_sell(self, button: discord.ui.Button, interaction: Interaction):
                if interaction.user.id != self.original_user_id:
                    await interaction.response.send_message("這不是你的商店，無法操作！", ephemeral=True)
                    return
                sell_view = FishSellView(self.original_user_id, 0)
                embed = sell_view.get_updated_embed()
                await interaction.response.edit_message(
                    content="已取消販售，請選擇其他漁獲。",
                    embed=embed, view=sell_view
                )

            async def on_timeout(self):
                try:
                    await ctx.edit(content="確認介面已超時，請重新開啟。", embed=None, view=None)
                except discord.errors.NotFound:
                    pass

        class FishSellView(discord.ui.View):
            def __init__(self, original_user_id, page=0):
                super().__init__(timeout=180)
                self.original_user_id = original_user_id
                self.page = page
                self.items_per_page = 25
                self.update_options()

            def update_options(self):
                self.clear_items()
                if not user_fishes:
                    self.add_item(discord.ui.Button(label="目前沒有漁獲可販售", style=discord.ButtonStyle.grey, disabled=True))
                    return

                total_pages = (len(user_fishes) + self.items_per_page - 1) // self.items_per_page
                start_idx = self.page * self.items_per_page
                end_idx = min((self.page + 1) * self.items_per_page, len(user_fishes))
                current_fishes = user_fishes[start_idx:end_idx]

                select_menu = discord.ui.Select(
                    placeholder="選擇您要販售的漁獲",
                    options=[
                        discord.SelectOption(
                            label=f"{fish['name']} ({fish['rarity'].capitalize()})",
                            description=f"重量: {fish['size']} 公斤 | 預計販售: {calculate_fish_price(fish)} 幽靈幣",
                            value=str(start_idx + index)
                        ) for index, fish in enumerate(current_fishes)
                    ]
                )

                async def select_fish_callback(interaction: discord.Interaction):
                    if interaction.user.id != self.original_user_id:
                        await interaction.response.send_message("這不是你的商店，無法操作！", ephemeral=True)
                        return

                    selected_index = int(select_menu.values[0])
                    selected_fish = user_fishes[selected_index]
                    price = calculate_fish_price(selected_fish)

                    rarity_colors = {
                        "common": discord.Color.green(),
                        "uncommon": discord.Color.blue(),
                        "rare": discord.Color.purple(),
                        "legendary": discord.Color.orange(),
                        "deify": discord.Color.gold(),
                        "unknown": discord.Color.light_grey()
                    }
                    embed = discord.Embed(
                        title=f"選擇的漁獲: {selected_fish['name']}",
                        color=rarity_colors.get(selected_fish["rarity"], discord.Color.default())
                    )
                    embed.add_field(name="名稱", value=selected_fish["name"], inline=False)
                    embed.add_field(name="重量", value=f"{selected_fish['size']} 公斤", inline=False)
                    embed.add_field(name="等級", value=selected_fish["rarity"].capitalize(), inline=False)
                    embed.add_field(name="預計販售價格", value=f"{price} 幽靈幣", inline=False)
                    embed.add_field(name="操作", value="請選擇是否售出此漁獲。", inline=False)

                    sell_confirm_view = ConfirmSellView(selected_index, self.original_user_id)
                    await interaction.response.edit_message(embed=embed, view=sell_confirm_view)

                select_menu.callback = select_fish_callback
                self.add_item(select_menu)

                if self.page > 0:
                    prev_button = discord.ui.Button(label="上一頁", style=discord.ButtonStyle.grey)
                    async def prev_callback(interaction: discord.Interaction):
                        if interaction.user.id != self.original_user_id:
                            await interaction.response.send_message("這不是你的商店，無法操作！", ephemeral=True)
                            return
                        new_view = FishSellView(self.original_user_id, self.page - 1)
                        embed = new_view.get_updated_embed()
                        await interaction.response.edit_message(embed=embed, view=new_view)
                    prev_button.callback = prev_callback
                    self.add_item(prev_button)

                if end_idx < len(user_fishes):
                    next_button = discord.ui.Button(label="下一頁", style=discord.ButtonStyle.grey)
                    async def next_callback(interaction: discord.Interaction):
                        if interaction.user.id != self.original_user_id:
                            await interaction.response.send_message("這不是你的商店，無法操作！", ephemeral=True)
                            return
                        new_view = FishSellView(self.original_user_id, self.page + 1)
                        embed = new_view.get_updated_embed()
                        await interaction.response.edit_message(embed=embed, view=new_view)
                    next_button.callback = next_callback
                    self.add_item(next_button)

            def get_updated_embed(self):
                embed = discord.Embed(
                    title="選擇漁獲進行販售",
                    description="點擊下方菜單選擇漁獲進行操作。",
                    color=discord.Color.blue()
                )
                if not user_fishes:
                    embed.description = "目前沒有漁獲可以販售！"
                else:
                    total_pages = (len(user_fishes) + self.items_per_page - 1) // self.items_per_page
                    embed.set_footer(text=f"共 {len(user_fishes)} 條漁獲 | 第 {self.page + 1}/{total_pages} 頁\n餘額：{balance_data.get(guild_id, {}).get(user_id, 0)} 幽靈幣")
                return embed

            async def on_timeout(self):
                try:
                    await ctx.edit(content="販售介面已超時，請重新開啟。", embed=None, view=None)
                except discord.errors.NotFound:
                    pass

        class FishShopView(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=180)
                self.original_user_id = ctx.user.id

            @discord.ui.button(label="前往出售漁獲", style=discord.ButtonStyle.primary)
            async def go_to_sell(self, button: discord.ui.Button, interaction: discord.Interaction):
                if interaction.user.id != self.original_user_id:
                    await interaction.response.send_message("這不是你的商店，無法操作！", ephemeral=True)
                    return

                if not user_fishes:
                    embed = discord.Embed(
                        title="釣魚商店通知",
                        description="您目前沒有漁獲可以販售！",
                        color=discord.Color.red()
                    )
                    embed.set_footer(text="請繼續努力釣魚吧！")
                    await interaction.response.edit_message(embed=embed, view=None)
                    return

                sell_view = FishSellView(self.original_user_id)
                embed = sell_view.get_updated_embed()
                await interaction.response.edit_message(embed=embed, view=sell_view)

            async def on_timeout(self):
                try:
                    await ctx.edit(content="商店已超時，請重新開啟。", embed=None, view=None)
                except discord.errors.NotFound:
                    pass

        welcome_embed = discord.Embed(
            title="歡迎來到漁獲商店",
            description=f"在這裡您可以販售釣得的漁獲，換取幽靈幣！\n你目前餘額：{user_balance} 幽靈幣",
            color=discord.Color.blue()
        )
        welcome_view = FishShopView()
        await ctx.edit(embed=welcome_embed, view=welcome_view)

def setup(bot):
    bot.add_cog(FishShop(bot))
