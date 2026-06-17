import discord
from discord.ext import commands
from discord import ApplicationContext, Interaction
import random
import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional, List  # [Debug 修復] 引入 typing 相容 Python 3.9

logger = logging.getLogger("SakuraBot.Fish")


class FishingButtons(discord.ui.View):
    """幽幽子的櫻花釣魚按鈕，如櫻花瓣般輕盈飄落"""

    def __init__(self, author_id, latest_fish_data, fish_data, current_rod, data_manager, cog):
        super().__init__(timeout=180)
        self.author_id = author_id
        self.latest_fish_data = latest_fish_data
        self.fish_data = fish_data
        self.current_rod = current_rod
        self.data_manager = data_manager
        self.cog = cog
        self.original_message = None

    async def interaction_check(self, interaction: Interaction) -> bool:
        if interaction.user.id != self.author_id:
            await interaction.response.send_message(
                "這不是你的櫻花釣魚按鈕哦～幽幽子會阻止你！🌸", ephemeral=True
            )
            return False
        return True

    async def on_timeout(self):
        try:
            for item in self.children:
                item.disabled = True
            if self.original_message:
                await self.original_message.edit(
                    content="釣魚操作已超時，幽幽子等你回來再釣一次吧～櫻花依舊會為你綻放 🌸",
                    view=self
                )
        except discord.errors.NotFound:
            logger.warning("櫻花釣魚訊息已消逝於冥界")
        except Exception as e:
            logger.error(f"釣魚超時處理時發生錯誤: {e}")

    # [Debug 修復 #2] 移除 custom_id，避免 View 超時或 Bot 重啟後按鈕靜默失效
    @discord.ui.button(label="🌸 再釣一次櫻花魚", style=discord.ButtonStyle.green)
    async def repeat_fishing(self, button: discord.ui.Button, interaction: Interaction):
        try:
            for item in self.children:
                item.disabled = True
            button.label = "幽幽子撒櫻花漁網中..."

            await interaction.response.edit_message(view=self)
            await asyncio.sleep(1.5)

            new_fish_data = self.cog.generate_fish_data(self.fish_data)
            new_embed = self.cog.create_fishing_embed(new_fish_data, self.current_rod)

            new_view = FishingButtons(
                self.author_id, new_fish_data, self.fish_data,
                self.current_rod, self.data_manager, self.cog
            )

            updated_message = await interaction.edit_original_response(
                content=None, embed=new_embed, view=new_view
            )
            new_view.original_message = updated_message

        except discord.errors.NotFound:
            await interaction.followup.send(
                "櫻花釣魚交互已失效，請重新使用 `/fish` 開始湖邊釣魚！🌸", ephemeral=True
            )
        except discord.errors.HTTPException as e:
            logger.error(f"重複釣魚時發生 HTTP 錯誤: {e}")
            await interaction.followup.send(
                "釣魚失敗，櫻花湖暫時波動異常！幽幽子會盡快修復～", ephemeral=True
            )
        except Exception as e:
            logger.error(f"重複釣魚時發生未預期錯誤: {e}", exc_info=True)
            await interaction.followup.send(
                "發生小故障，幽幽子會幫你修好！請稍後再試～🌸", ephemeral=True
            )

    # [Debug 修復 #2] 移除 custom_id
    @discord.ui.button(label="💾 保存櫻花漁獲", style=discord.ButtonStyle.blurple)
    async def save_fish(self, button: discord.ui.Button, interaction: Interaction):
        # [Debug 修復 #4] 加入在線備份攔截
        if self.data_manager.is_backing_up:
            await interaction.response.send_message(
                "⚠️ 幽幽子正在進行數據備份，保存漁獲暫時無法使用，請稍候再試哦～🌸",
                ephemeral=True
            )
            return

        try:
            button.disabled = True
            button.label = "封存櫻花漁獲中..."
            await interaction.response.edit_message(view=self)

            user_id = str(interaction.user.id)
            guild_id = str(interaction.guild.id) if interaction.guild else "DM"

            fish_record = {
                "name": self.latest_fish_data["name"],
                "rarity": self.latest_fish_data["rarity"],
                "size": self.latest_fish_data["size"],
                "rod": self.current_rod,
                "caught_at": datetime.now(self.cog.TIMEZONE).isoformat()
            }

            # [Debug 修復 #1] 徹底移除硬碟讀寫，直接操作記憶體中的 fishingbackpack！
            fishing_data = self.data_manager.fishingbackpack

            # [Debug 修復 #1] 使用 balance_lock 保護記憶體修改
            async with self.data_manager.balance_lock:
                if user_id not in fishing_data:
                    fishing_data[user_id] = {}
                if guild_id not in fishing_data[user_id]:
                    fishing_data[user_id][guild_id] = {"fishes": []}

                fishing_data[user_id][guild_id]["fishes"].append(fish_record)

            # [Debug 修復 #1] 鎖釋放後，統一呼叫 save_all_async 保存所有數據
            await self.data_manager.save_all_async()

            button.label = "✅ 已封存櫻花漁獲"
            button.style = discord.ButtonStyle.success
            await interaction.edit_original_response(view=self)

            logger.info(f"用戶 {user_id} 在伺服器 {guild_id} 保存了 {fish_record['name']}")

        except discord.errors.NotFound:
            await interaction.followup.send(
                "櫻花保存失效，訊息已消逝於冥界～請重新釣魚！🌸", ephemeral=True
            )
        except discord.errors.HTTPException as e:
            logger.error(f"保存漁獲時發生 HTTP 錯誤: {e}")
            await interaction.followup.send(
                "保存漁獲失敗～櫻花湖的記憶暫時混亂，請稍後再試！", ephemeral=True
            )
        except Exception as e:
            logger.error(f"保存漁獲時發生未預期錯誤: {e}", exc_info=True)
            await interaction.followup.send(
                "保存櫻花漁獲時發生小故障，幽幽子會幫你修好！請重試～🌸", ephemeral=True
            )


class Fish(commands.Cog):
    """幽幽子的櫻花湖釣魚系統，如夢似幻的漁獲體驗"""

    DEFAULT_RARITY_WEIGHTS = {
        "common":   50.0,
        "uncommon": 30.0,
        "rare":     15.0,
        "legendary": 4.0,
        "deify":     1.0,
        "unknown":   0.5
    }

    TIMEZONE = timezone(timedelta(hours=8))

    def __init__(self, bot):
        self.bot = bot
        self.rarity_weights_cache = None
        logger.info("櫻花釣魚系統已初始化，幽幽子在湖邊等你～")

    # [Debug 修復 #3] 修正型別提示，相容 Python 3.9
    def get_fish_data(self) -> Optional[List[dict]]:
        data_manager = self.bot.data_manager
        try:
            config_data = data_manager._load_json("config/config.json", {})
            fish_data = config_data.get("fish")
            if fish_data and isinstance(fish_data, list) and len(fish_data) > 0:
                logger.debug(f"成功載入 {len(fish_data)} 種櫻花魚")
                return fish_data
            else:
                logger.warning("config.json 中的魚種資料為空或格式不正確")
                return None
        except Exception as e:
            logger.error(f"幽幽子讀取湖中魚資料時迷糊了: {e}", exc_info=True)
            return None

    def calculate_rarity_weights(self, fish_data: list) -> dict:
        if self.rarity_weights_cache:
            return self.rarity_weights_cache

        actual_rarities = set()
        for fish in fish_data:
            rarity = fish.get("rarity", "common").lower()
            actual_rarities.add(rarity)

        final_weights = {}
        unknown_rarities = []

        for rarity in actual_rarities:
            if rarity in self.DEFAULT_RARITY_WEIGHTS:
                final_weights[rarity] = self.DEFAULT_RARITY_WEIGHTS[rarity]
            else:
                unknown_rarities.append(rarity)
                final_weights[rarity] = 0.5

        if unknown_rarities:
            logger.warning(
                f"發現未配置權重的稀有度: {unknown_rarities}，已自動分配 0.5% 機率"
            )

        self.rarity_weights_cache = final_weights
        logger.info(f"最終稀有度權重: {final_weights}")
        return final_weights

    def generate_fish_data(self, fish_data: list) -> dict:
        if not fish_data:
            logger.warning("魚種資料為空，返回預設櫻花魚")
            return {"name": "神秘櫻花魚", "rarity": "common", "size": 0.5}

        rarity_weights = self.calculate_rarity_weights(fish_data)

        rarity_pools = {}
        for fish in fish_data:
            rarity = fish.get("rarity", "common").lower()
            if rarity not in rarity_pools:
                rarity_pools[rarity] = []
            rarity_pools[rarity].append(fish)

        rarities = list(rarity_weights.keys())
        weights = [rarity_weights[r] for r in rarities]
        selected_rarity = random.choices(rarities, weights=weights, k=1)[0]
        selected_fish = random.choice(rarity_pools[selected_rarity])

        fish_name = selected_fish.get("name", "未知櫻花魚種")
        fish_rarity = selected_fish.get("rarity", "common").lower()

        try:
            min_size = float(selected_fish.get("min_size", 0.1))
            max_size = float(selected_fish.get("max_size", 1.0))
            if min_size > max_size:
                min_size, max_size = max_size, min_size
            fish_size = round(random.uniform(min_size, max_size), 2)
        except (ValueError, TypeError) as e:
            logger.warning(f"幽幽子生成櫻花魚大小時遇到小問題: {e}，使用預設值")
            fish_size = 0.5

        return {"name": fish_name, "rarity": fish_rarity, "size": fish_size}

    def create_fishing_embed(self, fish_data: dict, current_rod: str) -> discord.Embed:
        rarity_info = {
            "common":    {"color": discord.Color.green(),     "emoji": "🟢", "desc": "常見的櫻花湖住民"},
            "uncommon":  {"color": discord.Color.blue(),      "emoji": "🔵", "desc": "不太常見的美麗魚種"},
            "rare":      {"color": discord.Color.purple(),    "emoji": "🟣", "desc": "稀有的櫻花湖珍寶"},
            "legendary": {"color": discord.Color.orange(),    "emoji": "🟠", "desc": "傳說中的夢幻魚種"},
            "deify":     {"color": discord.Color.gold(),      "emoji": "⭐", "desc": "神格化的冥界聖魚"},
            "unknown":   {"color": discord.Color.dark_gray(), "emoji": "❓", "desc": "神秘的未知魚種"},
        }

        rarity = fish_data.get("rarity", "common").lower()
        info = rarity_info.get(rarity, {
            "color": discord.Color.light_gray(),
            "emoji": "⚪",
            "desc": "幽幽子也不認識的神秘魚種"
        })

        embed = discord.Embed(
            title="🌸 幽幽子的櫻花湖釣魚結果！",
            description=f"使用的魚竿：**{current_rod}**\n幽幽子在湖邊為你加油～櫻花隨風飄落 🌸",
            color=info["color"],
            timestamp=datetime.now(self.TIMEZONE)
        )
        embed.add_field(
            name="🐟 捕獲櫻花魚種",
            value=f"**{fish_data['name']}**\n{info['desc']}",
            inline=False
        )
        embed.add_field(name=f"{info['emoji']} 稀有度", value=f"**{rarity.capitalize()}**", inline=True)
        embed.add_field(name="⚖️ 重量", value=f"**{fish_data['size']}** 公斤", inline=True)

        size = fish_data['size']
        if size >= 10:
            comment = "天啊！這是巨物級別的漁獲！"
        elif size >= 5:
            comment = "好大的一條魚～幽幽子都驚訝了！"
        elif size >= 2:
            comment = "不錯的收穫呢！"
        else:
            comment = "小小的也很可愛～"

        embed.set_footer(text=f"{comment} | 幽幽子祝你天天釣到靈魂櫻花魚～不要空軍喲！")
        return embed

    @discord.slash_command(
        name="fish",
        description="🌸 幽幽子邀你到櫻花湖畔釣魚～在夢幻的湖光中等待漁獲的驚喜"
    )
    async def fish(self, ctx: ApplicationContext):
        # [Debug 修復 #3] 使用 to_thread 包裝同步的 get_fish_data，避免阻塞 Event Loop
        fish_data = await asyncio.to_thread(self.get_fish_data)
        
        if not fish_data:
            await ctx.respond(
                "幽幽子迷糊了，無法正確讀取櫻花湖魚資料～\n"
                "請確認 `config/config.json` 中有正確的魚種配置！",
                ephemeral=True
            )
            logger.error(f"用戶 {ctx.user.id} 嘗試釣魚但魚種資料載入失敗")
            return

        current_rod = "櫻花魚竿"
        await ctx.defer()
        await asyncio.sleep(1)

        latest_fish_data = self.generate_fish_data(fish_data)
        embed = self.create_fishing_embed(latest_fish_data, current_rod)

        view = FishingButtons(
            ctx.user.id, latest_fish_data, fish_data,
            current_rod, self.bot.data_manager, self
        )

        message = await ctx.followup.send(embed=embed, view=view)
        view.original_message = message

        logger.info(
            f"用戶 {ctx.user} ({ctx.user.id}) 在 "
            f"{ctx.guild.name if ctx.guild else 'DM'} "
            f"釣到了 {latest_fish_data['name']} "
            f"({latest_fish_data['rarity']}, {latest_fish_data['size']}kg)"
        )


def setup(bot):
    bot.add_cog(Fish(bot))
    logger.info("Fish Cog 已載入，櫻花湖等待著釣魚者～")
