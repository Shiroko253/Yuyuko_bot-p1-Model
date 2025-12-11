import discord
from discord.ext import commands
from discord import ApplicationContext, Interaction
import random
import asyncio
import logging
from datetime import datetime, timezone, timedelta

logger = logging.getLogger("SakuraBot.Fish")


class FishingButtons(discord.ui.View):
    """幽幽子的櫻花釣魚按鈕,如櫻花瓣般輕盈飄落"""
    
    def __init__(self, author_id, latest_fish_data, fish_data, current_rod, data_manager, cog):
        super().__init__(timeout=180)
        self.author_id = author_id
        self.latest_fish_data = latest_fish_data
        self.fish_data = fish_data
        self.current_rod = current_rod
        self.data_manager = data_manager
        self.cog = cog
        self.original_message = None  # 儲存原始訊息引用

    async def interaction_check(self, interaction: Interaction) -> bool:
        """確保只有釣魚的主人能觸碰按鈕,幽幽子守護著你的漁獲"""
        if interaction.user.id != self.author_id:
            await interaction.response.send_message(
                "這不是你的櫻花釣魚按鈕哦～幽幽子會阻止你！🌸", 
                ephemeral=True
            )
            return False
        return True

    async def on_timeout(self):
        """當櫻花瓣隨風散去,釣魚時光也悄然結束"""
        try:
            for item in self.children:
                item.disabled = True
            
            if self.original_message:
                await self.original_message.edit(
                    content="釣魚操作已超時,幽幽子等你回來再釣一次吧～櫻花依舊會為你綻放 🌸",
                    view=self
                )
        except discord.errors.NotFound:
            logger.warning("櫻花釣魚訊息已消逝於冥界")
        except Exception as e:
            logger.error(f"釣魚超時處理時發生錯誤: {e}")

    @discord.ui.button(label="🌸 再釣一次櫻花魚", style=discord.ButtonStyle.green, custom_id="fish_again")
    async def repeat_fishing(self, button: discord.ui.Button, interaction: Interaction):
        """再次撒下櫻花漁網,期待新的奇蹟"""
        try:
            # 禁用所有按鈕,展示載入狀態
            for item in self.children:
                item.disabled = True
            button.label = "幽幽子撒櫻花漁網中..."
            
            await interaction.response.edit_message(view=self)
            
            # 等待櫻花飄落的瞬間
            await asyncio.sleep(1.5)
            
            # 生成新的櫻花魚
            new_fish_data = self.cog.generate_fish_data(self.fish_data)
            new_embed = self.cog.create_fishing_embed(new_fish_data, self.current_rod)
            
            # 創建新的按鈕視圖
            new_view = FishingButtons(
                self.author_id, 
                new_fish_data, 
                self.fish_data,
                self.current_rod,
                self.data_manager, 
                self.cog
            )
            new_view.original_message = await interaction.original_response()
            
            await interaction.edit_original_response(
                content=None,
                embed=new_embed, 
                view=new_view
            )
            
        except discord.errors.NotFound:
            await interaction.followup.send(
                "櫻花釣魚交互已失效,請重新使用 `/fish` 開始湖邊釣魚！🌸", 
                ephemeral=True
            )
        except discord.errors.HTTPException as e:
            logger.error(f"重複釣魚時發生 HTTP 錯誤: {e}")
            await interaction.followup.send(
                f"釣魚失敗,櫻花湖暫時波動異常！幽幽子會盡快修復～", 
                ephemeral=True
            )
        except Exception as e:
            logger.error(f"重複釣魚時發生未預期錯誤: {e}", exc_info=True)
            await interaction.followup.send(
                f"發生小故障,幽幽子會幫你修好！請稍後再試～🌸", 
                ephemeral=True
            )

    @discord.ui.button(label="💾 保存櫻花漁獲", style=discord.ButtonStyle.blurple, custom_id="save_fish")
    async def save_fish(self, button: discord.ui.Button, interaction: Interaction):
        """將漁獲封存於櫻花圖鑑,永恆珍藏"""
        try:
            # 立即回應以避免超時
            button.disabled = True
            button.label = "封存櫻花漁獲中..."
            await interaction.response.edit_message(view=self)

            user_id = str(interaction.user.id)
            guild_id = str(interaction.guild.id) if interaction.guild else "DM"
            fishingpack_path = "config/fishingpack.json"
            
            # 準備漁獲資料,附上時間印記 (使用本地時區)
            fish_record = {
                "name": self.latest_fish_data["name"],
                "rarity": self.latest_fish_data["rarity"],
                "size": self.latest_fish_data["size"],
                "rod": self.current_rod,
                "caught_at": datetime.now(self.cog.TIMEZONE).isoformat()
            }

            # 使用 data_manager 的鎖保護保存操作
            async with self.data_manager.save_lock:
                # 載入現有資料
                fishingpack_data = await asyncio.to_thread(
                    self.data_manager._load_json, 
                    fishingpack_path, 
                    {}
                )
                
                # 確保資料結構存在
                if user_id not in fishingpack_data:
                    fishingpack_data[user_id] = {}
                if guild_id not in fishingpack_data[user_id]:
                    fishingpack_data[user_id][guild_id] = {"fishes": []}
                
                # 添加新漁獲
                fishingpack_data[user_id][guild_id]["fishes"].append(fish_record)
                
                # 保存資料
                await asyncio.to_thread(
                    self.data_manager._save_json, 
                    fishingpack_path, 
                    fishingpack_data
                )

            # 更新按鈕狀態
            button.label = "✅ 已封存櫻花漁獲"
            button.style = discord.ButtonStyle.success
            await interaction.edit_original_response(view=self)
            
            logger.info(f"用戶 {user_id} 在伺服器 {guild_id} 保存了 {fish_record['name']}")
            
        except discord.errors.NotFound:
            await interaction.followup.send(
                "櫻花保存失效,訊息已消逝於冥界～請重新釣魚！🌸", 
                ephemeral=True
            )
        except discord.errors.HTTPException as e:
            logger.error(f"保存漁獲時發生 HTTP 錯誤: {e}")
            await interaction.followup.send(
                f"保存漁獲失敗～櫻花湖的記憶暫時混亂,請稍後再試！", 
                ephemeral=True
            )
        except Exception as e:
            logger.error(f"保存漁獲時發生未預期錯誤: {e}", exc_info=True)
            await interaction.followup.send(
                f"保存櫻花漁獲時發生小故障,幽幽子會幫你修好！請重試～🌸", 
                ephemeral=True
            )


class Fish(commands.Cog):
    """幽幽子的櫻花湖釣魚系統,如夢似幻的漁獲體驗"""
    
    # 稀有度機率配置 (百分比) - 預設權重
    DEFAULT_RARITY_WEIGHTS = {
        "common": 50.0,      # 50% - 常見
        "uncommon": 30.0,    # 30% - 不常見
        "rare": 15.0,        # 15% - 稀有
        "legendary": 4.0,    # 4% - 傳說
        "deify": 1.0,        # 1% - 神格
        "unknown": 0.5       # 0.5% - 未知 (預設給極低機率)
    }
    
    # 時區設定 (UTC+8 馬來西亞/台灣/新加坡時區)
    TIMEZONE = timezone(timedelta(hours=8))
    
    def __init__(self, bot):
        self.bot = bot
        self.rarity_weights_cache = None  # 快取計算後的權重
        logger.info("櫻花釣魚系統已初始化,幽幽子在湖邊等你～")

    def get_fish_data(self) -> list | None:
        """從櫻花配置中讀取魚種資料,如翻閱冥界圖鑑"""
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
        """
        計算實際的稀有度權重,確保所有魚種都有機會被釣到
        如果魚種的稀有度不在預設權重中,給予預設機率
        """
        if self.rarity_weights_cache:
            return self.rarity_weights_cache
        
        # 收集所有實際存在的稀有度
        actual_rarities = set()
        for fish in fish_data:
            rarity = fish.get("rarity", "common").lower()
            actual_rarities.add(rarity)
        
        # 構建最終權重字典
        final_weights = {}
        unknown_rarities = []
        
        for rarity in actual_rarities:
            if rarity in self.DEFAULT_RARITY_WEIGHTS:
                final_weights[rarity] = self.DEFAULT_RARITY_WEIGHTS[rarity]
            else:
                # 未知稀有度記錄下來
                unknown_rarities.append(rarity)
                final_weights[rarity] = 0.5  # 給予 0.5% 的預設機率
        
        # 如果有未知稀有度,記錄警告
        if unknown_rarities:
            logger.warning(
                f"發現未配置權重的稀有度: {unknown_rarities}, "
                f"已自動分配 0.5% 機率"
            )
        
        # 快取結果
        self.rarity_weights_cache = final_weights
        
        logger.info(f"最終稀有度權重: {final_weights}")
        return final_weights

    def generate_fish_data(self, fish_data: list) -> dict:
        """生成隨機櫻花魚,每條都是獨一無二的奇蹟 (基於稀有度機率)"""
        if not fish_data:
            logger.warning("魚種資料為空,返回預設櫻花魚")
            return {
                "name": "神秘櫻花魚",
                "rarity": "common",
                "size": 0.5
            }
        
        # 計算實際權重
        rarity_weights = self.calculate_rarity_weights(fish_data)
        
        # 根據稀有度過濾魚種
        rarity_pools = {}
        for fish in fish_data:
            rarity = fish.get("rarity", "common").lower()
            if rarity not in rarity_pools:
                rarity_pools[rarity] = []
            rarity_pools[rarity].append(fish)
        
        # 根據機率選擇稀有度
        rarities = list(rarity_weights.keys())
        weights = [rarity_weights[r] for r in rarities]
        
        # 根據權重選擇稀有度
        selected_rarity = random.choices(rarities, weights=weights, k=1)[0]
        
        # 從該稀有度池中隨機選一條魚
        selected_fish = random.choice(rarity_pools[selected_rarity])
        
        fish_name = selected_fish.get("name", "未知櫻花魚種")
        fish_rarity = selected_fish.get("rarity", "common").lower()
        
        try:
            min_size = float(selected_fish.get("min_size", 0.1))
            max_size = float(selected_fish.get("max_size", 1.0))
            
            # 確保最小值不大於最大值
            if min_size > max_size:
                min_size, max_size = max_size, min_size
                
            fish_size = round(random.uniform(min_size, max_size), 2)
            
        except (ValueError, TypeError) as e:
            logger.warning(f"幽幽子生成櫻花魚大小時遇到小問題: {e},使用預設值")
            fish_size = 0.5
            
        return {
            "name": fish_name,
            "rarity": fish_rarity,
            "size": fish_size
        }

    def create_fishing_embed(self, fish_data: dict, current_rod: str) -> discord.Embed:
        """創建櫻花釣魚結果嵌入,如詩如畫的漁獲展示"""
        
        # 稀有度對應的顏色與描述
        rarity_info = {
            "common": {
                "color": discord.Color.green(),
                "emoji": "🟢",
                "desc": "常見的櫻花湖住民"
            },
            "uncommon": {
                "color": discord.Color.blue(),
                "emoji": "🔵",
                "desc": "不太常見的美麗魚種"
            },
            "rare": {
                "color": discord.Color.purple(),
                "emoji": "🟣",
                "desc": "稀有的櫻花湖珍寶"
            },
            "legendary": {
                "color": discord.Color.orange(),
                "emoji": "🟠",
                "desc": "傳說中的夢幻魚種"
            },
            "deify": {
                "color": discord.Color.gold(),
                "emoji": "⭐",
                "desc": "神格化的冥界聖魚"
            },
            "unknown": {
                "color": discord.Color.dark_gray(),
                "emoji": "❓",
                "desc": "神秘的未知魚種"
            }
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
        embed.add_field(
            name=f"{info['emoji']} 稀有度", 
            value=f"**{rarity.capitalize()}**", 
            inline=True
        )
        embed.add_field(
            name="⚖️ 重量", 
            value=f"**{fish_data['size']}** 公斤", 
            inline=True
        )
        
        # 根據重量添加評語
        size = fish_data['size']
        if size >= 10:
            comment = "天啊！這是巨物級別的漁獲！"
        elif size >= 5:
            comment = "好大的一條魚～幽幽子都驚訝了！"
        elif size >= 2:
            comment = "不錯的收穫呢！"
        else:
            comment = "小小的也很可愛～"
            
        embed.set_footer(
            text=f"{comment} | 幽幽子祝你天天釣到靈魂櫻花魚～不要空軍喲！"
        )
        
        return embed

    @discord.slash_command(
        name="fish", 
        description="🌸 幽幽子邀你到櫻花湖畔釣魚～在夢幻的湖光中等待漁獲的驚喜"
    )
    async def fish(self, ctx: ApplicationContext):
        """櫻花湖釣魚主指令,開啟一場與魚兒的邂逅"""
        
        # 載入魚種資料
        fish_data = self.get_fish_data()
        if not fish_data:
            await ctx.respond(
                "幽幽子迷糊了,無法正確讀取櫻花湖魚資料～\n"
                "請確認 `config/config.json` 中有正確的魚種配置！",
                ephemeral=True
            )
            logger.error(f"用戶 {ctx.user.id} 嘗試釣魚但魚種資料載入失敗")
            return

        # 當前使用的魚竿 (可擴展為多種魚竿系統)
        current_rod = "櫻花魚竿"
        
        # 延遲回應以增加期待感
        await ctx.defer()
        
        # 等待櫻花飄落...
        await asyncio.sleep(1)
        
        # 生成漁獲
        latest_fish_data = self.generate_fish_data(fish_data)
        embed = self.create_fishing_embed(latest_fish_data, current_rod)
        
        # 創建互動按鈕
        view = FishingButtons(
            ctx.user.id,
            latest_fish_data,
            fish_data,
            current_rod,
            self.bot.data_manager,
            self
        )
        
        # 發送釣魚結果
        message = await ctx.followup.send(embed=embed, view=view)
        view.original_message = message
        
        logger.info(
            f"用戶 {ctx.user} ({ctx.user.id}) 在 {ctx.guild.name if ctx.guild else 'DM'} "
            f"釣到了 {latest_fish_data['name']} ({latest_fish_data['rarity']}, {latest_fish_data['size']}kg)"
        )


def setup(bot):
    """將櫻花釣魚系統加入幽幽子的靈魂"""
    bot.add_cog(Fish(bot))
    logger.info("Fish Cog 已載入,櫻花湖等待著釣魚者～")
