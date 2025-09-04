import discord
from discord.ext import commands
from discord import ApplicationContext, Interaction
import asyncio

# ✿ 冥界釣魚祭典 ✿
# 幽幽子邀你在櫻花湖邊翻閱靈魂的漁獲～
RARITY_ORDER = {
    "unknown": 0,   # 未知
    "deify": 1,     # 神級
    "legendary": 2, # 傳奇
    "rare": 3,      # 史詩
    "uncommon": 4,  # 不常見
    "common": 5,    # 普通
}
RARITY_COLORS = {
    "unknown": discord.Color.dark_gray(),
    "deify": discord.Color.gold(),
    "legendary": discord.Color.orange(),
    "rare": discord.Color.purple(),
    "uncommon": discord.Color.blue(),
    "common": discord.Color.green(),
}

def get_rarity_sort_index(fish):
    return RARITY_ORDER.get(fish.get("rarity", "unknown"), 99)

def get_fishing_data(data_manager, file_lock):
    fishingpack_path = "config/fishingpack.json"
    async def async_loader():
        async with file_lock:
            fishing_data = data_manager.load_json(fishingpack_path) or {}
        return fishing_data
    return async_loader

class FishBackView(discord.ui.View):
    def __init__(self, user_id, guild_id, fish_list, page=0):
        super().__init__(timeout=180)
        self.user_id = user_id
        self.guild_id = guild_id
        # 幽幽子為你按照稀有度排序
        self.fish_list = sorted(fish_list, key=lambda fish: get_rarity_sort_index(fish))
        self.page = page
        self.fishes_per_page = 5
        self.max_page = max(0, (len(self.fish_list) - 1) // self.fishes_per_page)
        self.update_buttons()

    def update_buttons(self):
        self.clear_items()
        if self.page > 0:
            self.add_item(PageButton("← 前一頁（櫻花還沒飄完）", self.page - 1, self))
        if self.page < self.max_page:
            self.add_item(PageButton("下一頁 →（還有更多魚等著你）", self.page + 1, self))

    def get_embed(self):
        embed = discord.Embed(
            title="🌸 幽幽子的櫻花漁獲背包",
            description=f"頁數：{self.page + 1} / {self.max_page + 1}\n等級排序：未知 → 神級 → 傳奇 → 史詩 → 不常見 → 普通",
            color=discord.Color.from_rgb(255, 182, 193)
        )
        start = self.page * self.fishes_per_page
        end = start + self.fishes_per_page
        fishes_on_page = self.fish_list[start:end]
        if not fishes_on_page:
            embed.description = "❌ 你還沒有捕到任何魚～櫻花湖靜待你的身影！"
            embed.set_footer(text="幽幽子在湖邊等你來釣魚～")
            return embed
        for idx, fish in enumerate(fishes_on_page, start=1):
            rarity = fish.get("rarity", "unknown")
            color = RARITY_COLORS.get(rarity, discord.Color.light_gray())
            # 冥界魚種展示
            fish_name = fish.get("name", "未知魚種")
            fish_rarity = rarity.capitalize()
            size = fish.get("size", "?")
            rod = fish.get("rod", "未知")
            embed.add_field(
                name=f"{idx + start}. {fish_name}（{fish_rarity}）",
                value=f"重量：{size} 公斤\n釣竿：{rod}\n櫻花評價：{fish_rarity}",
                inline=False
            )
        embed.set_footer(text="可用下方櫻花按鈕翻頁\n幽幽子祝你漁獲豐收～")
        return embed

class PageButton(discord.ui.Button):
    def __init__(self, label, target_page, view_ref):
        super().__init__(label=label, style=discord.ButtonStyle.blurple)
        self.target_page = target_page
        self.view_ref = view_ref

    async def callback(self, interaction: Interaction):
        if interaction.user.id != self.view_ref.user_id:
            await interaction.response.send_message("櫻花湖的背包只能由主人自己翻閱哦～", ephemeral=True)
            return
        self.view_ref.page = self.target_page
        self.view_ref.update_buttons()
        embed = self.view_ref.get_embed()
        await interaction.response.edit_message(embed=embed, view=self.view_ref)

class FishBack(commands.Cog):
    """
    ✿ 冥界櫻花湖釣魚背包 ✿
    幽幽子帶你一頁頁翻閱過往釣魚的靈魂回憶～
    """
    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(name="fish_back", description="幽幽子帶你翻閱靈魂釣魚背包～")
    async def fish_back(self, ctx: ApplicationContext):
        user_id = str(ctx.user.id)
        guild_id = str(ctx.guild.id)
        file_lock = getattr(self.bot, "file_lock", asyncio.Lock())
        fishingpack_path = "config/fishingpack.json"

        async with file_lock:
            fishing_data = self.bot.data_manager.load_json(fishingpack_path) or {}

        # 判斷資料結構
        if user_id in fishing_data and guild_id in fishing_data[user_id]:
            user_fishes = fishing_data[user_id][guild_id].get('fishes', [])
            if user_fishes:
                view = FishBackView(user_id, guild_id, user_fishes, page=0)
                embed = view.get_embed()
                try:
                    await ctx.defer(ephemeral=True)
                    await asyncio.sleep(1)
                    await ctx.respond(embed=embed, view=view, ephemeral=True)
                except discord.errors.NotFound:
                    await ctx.channel.send(
                        f"{ctx.user.mention} ❌ 櫻花湖的查詢超時啦～請重新使用 `/fish_back` 再來看看你的漁獲！"
                    )
            else:
                await ctx.respond("❌ 你還沒有捕到任何魚～櫻花湖靜待你的身影！", ephemeral=True)
        else:
            await ctx.respond("❌ 你還沒有捕到任何魚～櫻花湖靜待你的身影！", ephemeral=True)

def setup(bot):
    """
    ✿ 幽幽子優雅地將櫻花湖釣魚背包功能裝進 bot ✿
    """
    bot.add_cog(FishBack(bot))