import discord
from discord.ext import commands
from discord import ApplicationContext, Interaction
import asyncio
import logging

logger = logging.getLogger("SakuraBot.FishShop")

# ----------- 冥界櫻花魚市的靈魂設定 -----------

# 稀有度對應的基礎價格和重量倍率
RARITY_PRICES = {
    "common": (100, 10),
    "uncommon": (350, 15),
    "rare": (7400, 50),
    "legendary": (450000, 100),
    "deify": (3000000, 500),
    "unknown": (100000000, 1000)
}

# 稀有度對應的顏色
RARITY_COLORS = {
    "common": discord.Color.green(),
    "uncommon": discord.Color.blue(),
    "rare": discord.Color.purple(),
    "legendary": discord.Color.orange(),
    "deify": discord.Color.gold(),
    "unknown": discord.Color.light_grey()
}

# 稀有度的中文名稱
RARITY_NAMES = {
    "common": "普通",
    "uncommon": "不常見",
    "rare": "史詩",
    "legendary": "傳奇",
    "deify": "神級",
    "unknown": "未知"
}


def calculate_fish_price(fish: dict) -> int:
    """計算櫻花漁獲的售價，如幽幽子的靈魂估價"""
    try:
        rarity = fish.get("rarity", "unknown")
        base_price, weight_multiplier = RARITY_PRICES.get(rarity, (0, 0))
        size = float(fish.get("size", 0))
        return int(base_price + size * weight_multiplier)
    except (KeyError, ValueError, TypeError) as e:
        logger.error(f"計算魚價失敗: {e}, fish data: {fish}")
        return 0


class ConfirmSellView(discord.ui.View):
    """確認販售的櫻花介面，幽幽子溫柔地等待你的決定"""
    
    def __init__(self, fish_index: int, original_user_id: int, fish_shop_cog):
        super().__init__(timeout=180)
        self.fish_index = fish_index
        self.original_user_id = original_user_id
        self.cog = fish_shop_cog

    @discord.ui.button(label="🌸 確認售出櫻花漁獲", style=discord.ButtonStyle.green)
    async def confirm_sell(self, button: discord.ui.Button, interaction: Interaction):
        """確認售出漁獲"""
        if interaction.user.id != self.original_user_id:
            await interaction.response.send_message(
                "🌸 這不是你的櫻花魚市，幽幽子會阻止你哦～",
                ephemeral=True
            )
            return

        try:
            result = await self.cog.sell_fish(
                interaction.user.id,
                interaction.guild.id,
                self.fish_index
            )
            
            if not result["success"]:
                await interaction.response.edit_message(
                    content=f"❌ {result['message']}",
                    embed=None,
                    view=None
                )
                return
            
            fish = result["fish"]
            price = result["price"]
            remaining_fishes = result["remaining_fishes"]
            
            # 如果沒有剩餘漁獲
            if remaining_fishes == 0:
                await interaction.response.edit_message(
                    content=(
                        f"🌸 成功售出 **{fish['name']}**，獲得 **{price:,}** 幽靈幣！\n\n"
                        f"目前已無漁獲可販售，幽幽子祝你櫻花湖大豐收～"
                    ),
                    embed=None,
                    view=None
                )
                return
            
            # 還有剩餘漁獲，顯示新的販售介面
            sell_view = FishSellView(self.original_user_id, self.cog, page=0)
            embed = await sell_view.get_updated_embed(interaction.user.id, interaction.guild.id)
            
            await interaction.response.edit_message(
                content=f"🌸 成功售出 **{fish['name']}**，獲得 **{price:,}** 幽靈幣！",
                embed=embed,
                view=sell_view
            )
            
        except Exception as e:
            logger.error(f"售出漁獲時發生錯誤: {e}", exc_info=True)
            await interaction.response.edit_message(
                content="❌ 啊呀…櫻花瓣在交易時散落了，請稍後再試～",
                embed=None,
                view=None
            )

    @discord.ui.button(label="❀ 取消，暫不賣出", style=discord.ButtonStyle.red)
    async def cancel_sell(self, button: discord.ui.Button, interaction: Interaction):
        """取消販售"""
        if interaction.user.id != self.original_user_id:
            await interaction.response.send_message(
                "🌸 這不是你的櫻花魚市，幽幽子會阻止你哦～",
                ephemeral=True
            )
            return
        
        sell_view = FishSellView(self.original_user_id, self.cog, page=0)
        embed = await sell_view.get_updated_embed(interaction.user.id, interaction.guild.id)
        
        await interaction.response.edit_message(
            content="已取消販售，幽幽子靜候你下一次櫻花選擇～",
            embed=embed,
            view=sell_view
        )

    async def on_timeout(self):
        """超時處理"""
        logger.info(f"用戶 {self.original_user_id} 的確認介面已超時")


class FishSellView(discord.ui.View):
    """櫻花漁獲販售選擇器，如幽幽子的優雅商店"""
    
    def __init__(self, original_user_id: int, fish_shop_cog, page: int = 0):
        super().__init__(timeout=180)
        self.original_user_id = original_user_id
        self.cog = fish_shop_cog
        self.page = page
        self.items_per_page = 25

    async def get_updated_embed(self, user_id: int, guild_id: int) -> discord.Embed:
        """獲取更新後的 Embed"""
        user_fishes = await self.cog.get_user_fishes(user_id, guild_id)
        user_balance = await self.cog.get_user_balance(user_id, guild_id)
        
        embed = discord.Embed(
            title="🌸 請選擇櫻花漁獲進行販售",
            color=discord.Color.from_rgb(255, 182, 193)
        )
        
        if not user_fishes:
            embed.description = (
                "目前沒有櫻花漁獲可以販售～\n\n"
                "幽幽子在湖邊等你釣魚！快去使用 `/fishing` 試試手氣吧！"
            )
        else:
            total_pages = (len(user_fishes) + self.items_per_page - 1) // self.items_per_page
            embed.description = "請點選下方櫻花菜單，選擇你要販售的漁獲～"
            embed.set_footer(
                text=f"共 {len(user_fishes)} 條漁獲 | 第 {self.page + 1}/{total_pages} 頁 • 餘額：{user_balance:,} 幽靈幣"
            )
        
        return embed

    async def setup_components(self, user_id: int, guild_id: int):
        """設置 UI 組件"""
        self.clear_items()
        
        user_fishes = await self.cog.get_user_fishes(user_id, guild_id)
        
        if not user_fishes:
            self.add_item(
                discord.ui.Button(
                    label="目前沒有漁獲可販售～櫻花湖靜待你釣魚",
                    style=discord.ButtonStyle.grey,
                    disabled=True
                )
            )
            return

        # 計算分頁
        start_idx = self.page * self.items_per_page
        end_idx = min((self.page + 1) * self.items_per_page, len(user_fishes))
        current_fishes = user_fishes[start_idx:end_idx]

        # 創建選擇菜單
        select_options = []
        for index, fish in enumerate(current_fishes):
            rarity_name = RARITY_NAMES.get(fish.get("rarity", "unknown"), "未知")
            price = calculate_fish_price(fish)
            
            select_options.append(
                discord.SelectOption(
                    label=f"{fish.get('name', '未知魚種')} ({rarity_name})",
                    description=f"重量: {fish.get('size', 0)} 公斤 | 預計售價: {price:,} 幽靈幣",
                    value=str(start_idx + index)
                )
            )

        select_menu = discord.ui.Select(
            placeholder="請選擇你要販售的櫻花漁獲～",
            options=select_options
        )
        select_menu.callback = self.select_fish_callback
        self.add_item(select_menu)

        # 添加翻頁按鈕
        if self.page > 0:
            prev_button = discord.ui.Button(
                label="⬅️ 上一頁",
                style=discord.ButtonStyle.grey
            )
            prev_button.callback = self.prev_page_callback
            self.add_item(prev_button)

        if end_idx < len(user_fishes):
            next_button = discord.ui.Button(
                label="下一頁 ➡️",
                style=discord.ButtonStyle.grey
            )
            next_button.callback = self.next_page_callback
            self.add_item(next_button)

    async def select_fish_callback(self, interaction: Interaction):
        """選擇魚的回調"""
        if interaction.user.id != self.original_user_id:
            await interaction.response.send_message(
                "🌸 只能賣自己的櫻花漁獲哦～",
                ephemeral=True
            )
            return

        select_menu = [item for item in self.children if isinstance(item, discord.ui.Select)][0]
        selected_index = int(select_menu.values[0])
        
        user_fishes = await self.cog.get_user_fishes(interaction.user.id, interaction.guild.id)
        selected_fish = user_fishes[selected_index]
        price = calculate_fish_price(selected_fish)
        
        rarity = selected_fish.get("rarity", "unknown")
        rarity_name = RARITY_NAMES.get(rarity, "未知")
        
        embed = discord.Embed(
            title=f"🌸 你選擇的櫻花漁獲: {selected_fish.get('name', '未知魚種')}",
            color=RARITY_COLORS.get(rarity, discord.Color.default())
        )
        
        embed.add_field(
            name="🐟 名稱",
            value=selected_fish.get("name", "未知魚種"),
            inline=True
        )
        embed.add_field(
            name="⚖️ 重量",
            value=f"{selected_fish.get('size', 0)} 公斤",
            inline=True
        )
        embed.add_field(
            name="✨ 等級",
            value=rarity_name,
            inline=True
        )
        embed.add_field(
            name="💰 預計販售價格",
            value=f"**{price:,}** 幽靈幣",
            inline=False
        )
        embed.add_field(
            name="📝 操作",
            value="請選擇是否售出此櫻花漁獲。",
            inline=False
        )
        
        sell_confirm_view = ConfirmSellView(selected_index, self.original_user_id, self.cog)
        await interaction.response.edit_message(embed=embed, view=sell_confirm_view)

    async def prev_page_callback(self, interaction: Interaction):
        """上一頁回調"""
        if interaction.user.id != self.original_user_id:
            await interaction.response.send_message(
                "🌸 只能翻自己的櫻花魚市！",
                ephemeral=True
            )
            return
        
        new_view = FishSellView(self.original_user_id, self.cog, self.page - 1)
        await new_view.setup_components(interaction.user.id, interaction.guild.id)
        embed = await new_view.get_updated_embed(interaction.user.id, interaction.guild.id)
        await interaction.response.edit_message(embed=embed, view=new_view)

    async def next_page_callback(self, interaction: Interaction):
        """下一頁回調"""
        if interaction.user.id != self.original_user_id:
            await interaction.response.send_message(
                "🌸 只能翻自己的櫻花魚市！",
                ephemeral=True
            )
            return
        
        new_view = FishSellView(self.original_user_id, self.cog, self.page + 1)
        await new_view.setup_components(interaction.user.id, interaction.guild.id)
        embed = await new_view.get_updated_embed(interaction.user.id, interaction.guild.id)
        await interaction.response.edit_message(embed=embed, view=new_view)

    async def on_timeout(self):
        """超時處理"""
        logger.info(f"用戶 {self.original_user_id} 的販售介面已超時")


class FishShopView(discord.ui.View):
    """櫻花魚市的歡迎介面，幽幽子的溫柔迎接"""
    
    def __init__(self, original_user_id: int, fish_shop_cog):
        super().__init__(timeout=180)
        self.original_user_id = original_user_id
        self.cog = fish_shop_cog

    @discord.ui.button(label="🌸 前往出售櫻花漁獲", style=discord.ButtonStyle.primary)
    async def go_to_sell(self, button: discord.ui.Button, interaction: Interaction):
        """前往販售介面"""
        if interaction.user.id != self.original_user_id:
            await interaction.response.send_message(
                "🌸 櫻花魚市只能由自己的靈魂操作哦～",
                ephemeral=True
            )
            return

        user_fishes = await self.cog.get_user_fishes(interaction.user.id, interaction.guild.id)
        
        if not user_fishes:
            embed = discord.Embed(
                title="🌸 櫻花魚市通知",
                description=(
                    "你目前沒有漁獲可以販售～\n\n"
                    "幽幽子等你再來釣魚！快去使用 `/fishing` 試試手氣吧！"
                ),
                color=discord.Color.red()
            )
            embed.set_footer(text="櫻花湖靜待你的身影")
            await interaction.response.edit_message(embed=embed, view=None)
            return

        sell_view = FishSellView(self.original_user_id, self.cog)
        await sell_view.setup_components(interaction.user.id, interaction.guild.id)
        embed = await sell_view.get_updated_embed(interaction.user.id, interaction.guild.id)
        await interaction.response.edit_message(embed=embed, view=sell_view)

    async def on_timeout(self):
        """超時處理"""
        logger.info(f"用戶 {self.original_user_id} 的魚市歡迎介面已超時")


class FishShop(commands.Cog):
    """
    ✿ 幽幽子的冥界櫻花魚市 ✿
    讓你的漁獲化作幽靈幣，櫻花和幽幽子都會為你祝福～
    """
    
    def __init__(self, bot: discord.Bot):
        self.bot = bot
        self.data_manager = bot.data_manager
        
        # 確保有文件鎖
        if not hasattr(bot, 'file_lock'):
            bot.file_lock = asyncio.Lock()
        self.file_lock = bot.file_lock
        
        logger.info("櫻花湖漁獲商店已開張")

    async def get_user_fishes(self, user_id: int, guild_id: int) -> list:
        """獲取用戶的漁獲列表"""
        fishingpack_path = f"{self.data_manager.config_dir}/fishingpack.json"
        
        async with self.file_lock:
            fishing_data = self.data_manager._load_json(fishingpack_path) or {}
        
        user_id_str = str(user_id)
        guild_id_str = str(guild_id)
        
        return fishing_data.get(user_id_str, {}).get(guild_id_str, {}).get("fishes", [])

    async def get_user_balance(self, user_id: int, guild_id: int) -> int:
        """獲取用戶餘額"""
        async with self.data_manager.balance_lock:
            guild_id_str = str(guild_id)
            user_id_str = str(user_id)
            return self.data_manager.balance.get(guild_id_str, {}).get(user_id_str, 0)

    async def sell_fish(self, user_id: int, guild_id: int, fish_index: int) -> dict:
        """售出漁獲"""
        fishingpack_path = f"{self.data_manager.config_dir}/fishingpack.json"
        
        user_id_str = str(user_id)
        guild_id_str = str(guild_id)
        
        try:
            async with self.file_lock:
                fishing_data = self.data_manager._load_json(fishingpack_path) or {}
                
                # 獲取用戶漁獲
                user_fishes = fishing_data.get(user_id_str, {}).get(guild_id_str, {}).get("fishes", [])
                
                if fish_index >= len(user_fishes) or fish_index < 0:
                    return {
                        "success": False,
                        "message": "櫻花漁獲不存在，可能已被售出～"
                    }
                
                fish = user_fishes[fish_index]
                price = calculate_fish_price(fish)
                
                if price == 0:
                    return {
                        "success": False,
                        "message": "櫻花漁獲資料錯誤，幽幽子暫時無法售出！"
                    }
                
                # 更新餘額
                async with self.data_manager.balance_lock:
                    if guild_id_str not in self.data_manager.balance:
                        self.data_manager.balance[guild_id_str] = {}
                    if user_id_str not in self.data_manager.balance[guild_id_str]:
                        self.data_manager.balance[guild_id_str][user_id_str] = 0
                    
                    self.data_manager.balance[guild_id_str][user_id_str] += price
                
                # 移除漁獲
                user_fishes.pop(fish_index)
                
                # 更新漁獲數據
                if user_id_str not in fishing_data:
                    fishing_data[user_id_str] = {}
                if guild_id_str not in fishing_data[user_id_str]:
                    fishing_data[user_id_str][guild_id_str] = {}
                
                fishing_data[user_id_str][guild_id_str]["fishes"] = user_fishes
                
                # 保存數據
                self.data_manager._save_json(fishingpack_path, fishing_data)
                
                # 異步保存所有數據
                await self.data_manager.save_all_async()
                
                logger.info(f"用戶 {user_id} 售出了 {fish.get('name')}，獲得 {price} 幽靈幣")
                
                return {
                    "success": True,
                    "fish": fish,
                    "price": price,
                    "remaining_fishes": len(user_fishes)
                }
                
        except Exception as e:
            logger.error(f"售出漁獲時發生錯誤: {e}", exc_info=True)
            return {
                "success": False,
                "message": "售出時發生錯誤，請稍後再試～"
            }

    @discord.slash_command(
        name="fish_shop",
        description="幽幽子的櫻花湖漁獲商店～"
    )
    async def fish_shop(self, ctx: ApplicationContext):
        """進入櫻花魚市"""
        await ctx.defer()
        
        try:
            user_balance = await self.get_user_balance(ctx.user.id, ctx.guild.id)
            user_fishes = await self.get_user_fishes(ctx.user.id, ctx.guild.id)
            
            welcome_embed = discord.Embed(
                title="🌸 歡迎來到幽幽子的櫻花湖漁獲商店～",
                description=(
                    f"在這裡你可以販售櫻花湖釣到的漁獲，\n"
                    f"換取幽靈幣與幽幽子的祝福！\n\n"
                    f"💰 **你目前餘額:** {user_balance:,} 幽靈幣\n"
                    f"🐟 **漁獲數量:** {len(user_fishes)} 條"
                ),
                color=discord.Color.from_rgb(255, 182, 193)
            )
            welcome_embed.set_footer(
                text="點擊下方按鈕開始販售 • 幽幽子祝你交易順利～",
                icon_url=self.bot.user.display_avatar.url
            )
            
            welcome_view = FishShopView(ctx.user.id, self)
            await ctx.respond(embed=welcome_embed, view=welcome_view)
            
            logger.info(f"{ctx.user} 進入了櫻花魚市")
            
        except Exception as e:
            logger.error(f"開啟魚市時發生錯誤: {e}", exc_info=True)
            await ctx.respond(
                "❌ 啊呀…櫻花魚市暫時無法開啟～\n幽幽子需要稍作休息，請稍後再試！",
                ephemeral=True
            )


def setup(bot: discord.Bot):
    """
    ✿ 幽幽子優雅地將櫻花湖漁獲商店裝進 bot ✿
    """
    bot.add_cog(FishShop(bot))
