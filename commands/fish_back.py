import discord
from discord.ext import commands
from discord import ApplicationContext, Interaction
import asyncio

# 等級排序與顏色
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
        self.fish_list = sorted(fish_list, key=lambda fish: get_rarity_sort_index(fish))
        self.page = page
        self.fishes_per_page = 5
        self.max_page = max(0, (len(self.fish_list) - 1) // self.fishes_per_page)
        self.update_buttons()

    def update_buttons(self):
        self.clear_items()
        if self.page > 0:
            self.add_item(PageButton("← 上一頁", self.page - 1, self))
        if self.page < self.max_page:
            self.add_item(PageButton("下一頁 →", self.page + 1, self))

    def get_embed(self):
        embed = discord.Embed(
            title="🎣 你的漁獲列表",
            description=f"頁數：{self.page + 1} / {self.max_page + 1}\n等級排序：未知 → 神級 → 傳奇 → 史詩 → 不常見 → 普通",
            color=discord.Color.blue()
        )
        start = self.page * self.fishes_per_page
        end = start + self.fishes_per_page
        fishes_on_page = self.fish_list[start:end]
        if not fishes_on_page:
            embed.description = "❌ 你還沒有捕到任何魚！"
            embed.set_footer(text="數據提供為釣魚協會")
            return embed
        for idx, fish in enumerate(fishes_on_page, start=1):
            rarity = fish.get("rarity", "unknown")
            color = RARITY_COLORS.get(rarity, discord.Color.light_gray())
            embed.add_field(
                name=f"{idx + start}. {fish.get('name', '未知魚種')} ({rarity.capitalize()})",
                value=f"重量：{fish.get('size', '?')} 公斤\n來源：{fish.get('rod', '未知')}",
                inline=False
            )
        embed.set_footer(text="數據提供為釣魚協會\n可使用下方按鈕翻頁")
        return embed

class PageButton(discord.ui.Button):
    def __init__(self, label, target_page, view_ref):
        super().__init__(label=label, style=discord.ButtonStyle.blurple)
        self.target_page = target_page
        self.view_ref = view_ref

    async def callback(self, interaction: Interaction):
        if interaction.user.id != self.view_ref.user_id:
            await interaction.response.send_message("你無法操作別人的背包！", ephemeral=True)
            return
        self.view_ref.page = self.target_page
        self.view_ref.update_buttons()
        embed = self.view_ref.get_embed()
        await interaction.response.edit_message(embed=embed, view=self.view_ref)

class FishBack(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(name="fish_back", description="查看你的漁獲")
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
                        f"{ctx.user.mention} ❌ 你的查詢超時，請重新使用 `/fish_back` 查看漁獲！"
                    )
            else:
                await ctx.respond("❌ 你還沒有捕到任何魚！", ephemeral=True)
        else:
            await ctx.respond("❌ 你還沒有捕到任何魚！", ephemeral=True)

def setup(bot):
    bot.add_cog(FishBack(bot))
