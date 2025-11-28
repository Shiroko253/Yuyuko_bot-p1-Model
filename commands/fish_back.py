import discord
from discord.ext import commands
from discord import ApplicationContext, Interaction
import asyncio
import logging
from datetime import datetime

logger = logging.getLogger("SakuraBot.FishBack")

# ----------- 冥界釣魚祭典的靈魂設定 -----------

# 稀有度排序規則（幽幽子的櫻花評級）
RARITY_ORDER = {
    "unknown": 0,   # 未知
    "deify": 1,     # 神級
    "legendary": 2, # 傳奇
    "rare": 3,      # 史詩
    "uncommon": 4,  # 不常見
    "common": 5,    # 普通
}

# 稀有度對應的櫻花顏色
RARITY_COLORS = {
    "unknown": discord.Color.dark_gray(),
    "deify": discord.Color.gold(),
    "legendary": discord.Color.orange(),
    "rare": discord.Color.purple(),
    "uncommon": discord.Color.blue(),
    "common": discord.Color.green(),
}

# 稀有度的中文名稱
RARITY_NAMES = {
    "unknown": "未知",
    "deify": "神級",
    "legendary": "傳奇",
    "rare": "史詩",
    "uncommon": "不常見",
    "common": "普通",
}

# 稀有度對應的櫻花表情
RARITY_EMOJIS = {
    "unknown": "❓",
    "deify": "👑",
    "legendary": "🌟",
    "rare": "💎",
    "uncommon": "🔷",
    "common": "🌸",
}


def get_rarity_sort_index(fish: dict) -> int:
    """根據稀有度獲取排序索引，如櫻花按美麗程度排列"""
    return RARITY_ORDER.get(fish.get("rarity", "unknown"), 99)


class PageButton(discord.ui.Button):
    """櫻花翻頁按鈕，輕輕一點就能看到更多靈魂漁獲"""
    
    def __init__(self, label: str, target_page: int, view_ref):
        super().__init__(label=label, style=discord.ButtonStyle.blurple)
        self.target_page = target_page
        self.view_ref = view_ref

    async def callback(self, interaction: Interaction):
        """當櫻花瓣被輕撫時"""
        if interaction.user.id != self.view_ref.user_id:
            await interaction.response.send_message(
                "🌸 櫻花湖的背包只能由主人自己翻閱哦～",
                ephemeral=True
            )
            return
        
        # 更新頁面，如翻開新的記憶
        self.view_ref.page = self.target_page
        self.view_ref.update_buttons()
        embed = self.view_ref.get_embed()
        
        await interaction.response.edit_message(embed=embed, view=self.view_ref)
        logger.info(f"{interaction.user} 翻至第 {self.target_page + 1} 頁")


class FishBackView(discord.ui.View):
    """幽幽子的櫻花漁獲展示器，優雅地呈現每一尾靈魂之魚"""
    
    def __init__(self, user_id: int, guild_id: str, fish_list: list, bot: discord.Bot, page: int = 0):
        super().__init__(timeout=180)
        self.user_id = user_id
        self.guild_id = guild_id
        self.bot = bot
        
        # 幽幽子為你按照稀有度排序（從神級到普通）
        self.fish_list = sorted(fish_list, key=get_rarity_sort_index)
        
        self.page = page
        self.fishes_per_page = 5
        self.max_page = max(0, (len(self.fish_list) - 1) // self.fishes_per_page)
        
        self.update_buttons()

    def update_buttons(self):
        """更新櫻花翻頁按鈕"""
        self.clear_items()
        
        if self.page > 0:
            self.add_item(
                PageButton("⬅️ 前一頁（櫻花還沒飄完）", self.page - 1, self)
            )
        
        if self.page < self.max_page:
            self.add_item(
                PageButton("下一頁 ➡️（還有更多魚等著你）", self.page + 1, self)
            )

    def get_embed(self) -> discord.Embed:
        """構建櫻花漁獲展示 Embed，如詩般優雅"""
        embed = discord.Embed(
            title="🌸 幽幽子的櫻花漁獲背包",
            color=discord.Color.from_rgb(255, 182, 193)
        )
        
        # 計算當前頁的魚
        start = self.page * self.fishes_per_page
        end = start + self.fishes_per_page
        fishes_on_page = self.fish_list[start:end]
        
        # 如果沒有魚
        if not fishes_on_page:
            embed.description = (
                "❌ 你還沒有捕到任何魚～\n\n"
                "櫻花湖靜待你的身影，快去使用 `/fishing` 試試手氣吧！"
            )
            embed.set_footer(text="幽幽子在湖邊等你來釣魚～")
            return embed
        
        # 添加頁數和排序說明
        embed.description = (
            f"📄 **頁數:** {self.page + 1} / {self.max_page + 1}\n"
            f"🎯 **總計:** {len(self.fish_list)} 條魚\n"
            f"📊 **排序:** 未知 → 神級 → 傳奇 → 史詩 → 不常見 → 普通\n"
        )
        
        # 展示每一條魚
        for idx, fish in enumerate(fishes_on_page, start=1):
            rarity = fish.get("rarity", "unknown")
            rarity_name = RARITY_NAMES.get(rarity, "未知")
            rarity_emoji = RARITY_EMOJIS.get(rarity, "❓")
            
            fish_name = fish.get("name", "未知魚種")
            size = fish.get("size", 0)
            rod = fish.get("rod", "未知釣竿")
            
            # 格式化捕獲時間
            caught_at = fish.get("caught_at", "未知時間")
            try:
                caught_time = datetime.fromisoformat(caught_at.replace('Z', '+00:00'))
                time_str = caught_time.strftime("%Y-%m-%d %H:%M")
            except:
                time_str = "未知時間"
            
            # 構建魚的展示內容
            field_value = (
                f"{rarity_emoji} **稀有度:** {rarity_name}\n"
                f"⚖️ **重量:** {size:.2f} 公斤\n"
                f"🎣 **釣竿:** {rod}\n"
                f"🕐 **捕獲時間:** {time_str}"
            )
            
            embed.add_field(
                name=f"🐟 {start + idx}. {fish_name}",
                value=field_value,
                inline=False
            )
        
        embed.set_footer(
            text="可用下方櫻花按鈕翻頁 • 幽幽子祝你漁獲豐收～",
            icon_url=self.bot.user.display_avatar.url
        )
        
        return embed

    async def on_timeout(self):
        """當櫻花飄落時（超時處理）"""
        self.clear_items()
        logger.info(f"用戶 {self.user_id} 的漁獲背包已超時關閉")


class FishBack(commands.Cog):
    """
    ✿ 冥界櫻花湖釣魚背包 ✿
    幽幽子帶你一頁頁翻閱過往釣魚的靈魂回憶～
    """
    
    def __init__(self, bot: discord.Bot):
        self.bot = bot
        self.data_manager = bot.data_manager
        # 確保有文件鎖
        if not hasattr(bot, 'file_lock'):
            bot.file_lock = asyncio.Lock()
        self.file_lock = bot.file_lock
        logger.info("櫻花湖釣魚背包系統已啟動")

    @discord.slash_command(
        name="fish_back",
        description="幽幽子帶你翻閱靈魂釣魚背包～"
    )
    async def fish_back(self, ctx: ApplicationContext):
        """查看你在櫻花湖釣到的所有靈魂之魚"""
        
        await ctx.defer(ephemeral=True)
        
        user_id = str(ctx.user.id)
        guild_id = str(ctx.guild.id) if ctx.guild else "dm"
        
        try:
            # 讀取釣魚資料，如翻開冥界的記憶
            fishingpack_path = f"{self.data_manager.config_dir}/fishingpack.json"
            async with self.file_lock:
                fishing_data = self.data_manager._load_json(fishingpack_path) or {}
            
            # 檢查用戶是否有釣魚記錄
            if user_id not in fishing_data:
                await ctx.respond(
                    "❌ 你還沒有捕到任何魚～\n\n"
                    "櫻花湖靜待你的身影！快去使用 `/fishing` 試試手氣吧！",
                    ephemeral=True
                )
                logger.info(f"{ctx.user} 尚未有任何釣魚記錄")
                return
            
            if guild_id not in fishing_data[user_id]:
                await ctx.respond(
                    "❌ 你在這個伺服器還沒有捕到任何魚～\n\n"
                    "櫻花湖靜待你的身影！快去使用 `/fishing` 試試手氣吧！",
                    ephemeral=True
                )
                logger.info(f"{ctx.user} 在伺服器 {guild_id} 尚未有釣魚記錄")
                return
            
            # 獲取用戶的魚列表
            user_fishes = fishing_data[user_id][guild_id].get('fishes', [])
            
            if not user_fishes:
                await ctx.respond(
                    "❌ 你的漁獲背包是空的～\n\n"
                    "櫻花湖靜待你的身影！快去使用 `/fishing` 試試手氣吧！",
                    ephemeral=True
                )
                logger.info(f"{ctx.user} 的漁獲列表為空")
                return
            
            # 創建漁獲展示器
            view = FishBackView(ctx.user.id, guild_id, user_fishes, self.bot, page=0)
            embed = view.get_embed()
            
            await ctx.respond(embed=embed, view=view, ephemeral=True)
            logger.info(f"{ctx.user} 查看了釣魚背包，共 {len(user_fishes)} 條魚")
            
        except discord.errors.NotFound:
            # 處理互動超時
            await ctx.channel.send(
                f"{ctx.user.mention} ❌ 櫻花湖的查詢超時啦～\n"
                f"請重新使用 `/fish_back` 再來看看你的漁獲！"
            )
            logger.warning(f"{ctx.user} 的背包查詢超時")
            
        except Exception as e:
            logger.error(f"查看釣魚背包時發生錯誤: {e}", exc_info=True)
            try:
                await ctx.respond(
                    "❌ 啊呀…櫻花湖的記憶有些模糊了～\n"
                    "幽幽子需要稍作休息，請稍後再試！",
                    ephemeral=True
                )
            except:
                pass


def setup(bot: discord.Bot):
    """
    ✿ 幽幽子優雅地將櫻花湖釣魚背包功能裝進 bot ✿
    """
    bot.add_cog(FishBack(bot))
