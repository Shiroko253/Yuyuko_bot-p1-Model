import discord
from discord.ext import commands
from discord.ui import View, Select, Button
import logging
from typing import Dict, Any, List
import asyncio
from contextlib import contextmanager
from datetime import datetime


class BackpackView(View):
    """背包視圖管理器"""
    def __init__(self, timeout: float = 300.0):  # 5分鐘超時
        super().__init__(timeout=timeout)


class Backpack(commands.Cog):
    """
    ✿ 幽幽子的背包小空間 ✿
    來看看你收集了哪些可愛小東西吧～幽幽子會一直陪著你♪
    """

    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger("SakuraBot.commands.backpack")
        # 添加鎖機制防止並發問題
        self.user_locks = {}

    def _get_user_lock(self, user_id: str) -> asyncio.Lock:
        """獲取用戶專屬鎖"""
        if user_id not in self.user_locks:
            self.user_locks[user_id] = asyncio.Lock()
        return self.user_locks[user_id]

    @contextmanager
    def _safe_data_access(self, data_manager, file_path: str, file_type: str = "yaml"):
        """安全的資料存取上下文管理器"""
        try:
            if file_type == "json":
                data = data_manager._load_json(file_path)
                yield data
                data_manager._save_json(file_path, data)
            else:  # yaml
                data = data_manager._load_yaml(file_path)
                yield data
                data_manager._save_yaml(file_path, data)
        except Exception as e:
            self.logger.error(f"資料存取錯誤 {file_path}: {e}")
            raise

    @discord.slash_command(
        name="backpack", 
        description="幽幽子帶你看看背包裡的小寶貝哦～",
        guild_ids=None
    )
    async def backpack(self, ctx: discord.ApplicationContext):
        try:
            guild_id = str(ctx.guild.id)
            user_id = str(ctx.author.id)

            # 獲取資料管理器
            data_manager = getattr(self.bot, "data_manager", None)
            if not data_manager:
                await ctx.respond(
                    "❌ 幽幽子的資料管理員暫時不在，請稍後再試～", 
                    ephemeral=True
                )
                return

            # 獲取用戶鎖，防止並發修改
            user_lock = self._get_user_lock(user_id)
            async with user_lock:
                # 安全地載入用戶資料 - 使用正確的 JSON 路徑
                try:
                    user_file_path = f"{data_manager.config_dir}/user_config.json"
                    # 確保文件存在
                    data_manager._initialize_json(user_file_path, {})
                    
                    with self._safe_data_access(data_manager, user_file_path, "json") as user_data:
                        user_data.setdefault(guild_id, {})
                        user_data[guild_id].setdefault(user_id, {"MP": 200, "backpack": []})
                        backpack_items = user_data[guild_id][user_id]["backpack"].copy()  # 複製避免修改問題
                except Exception as e:
                    self.logger.error(f"用戶資料載入錯誤: {e}")
                    await ctx.respond(
                        "❌ 背包資料載入失敗，請稍後再試～", 
                        ephemeral=True
                    )
                    return

                # 獲取商店數據 - 從 config.json 的 shop_item 鍵讀取
                try:
                    config_file_path = f"{data_manager.config_dir}/config.json"
                    config_data = data_manager._load_json(config_file_path, {})
                    shop_data = config_data.get("shop_item", [])
                except Exception as e:
                    self.logger.error(f"商店資料載入錯誤: {e}")
                    shop_data = []

                if not backpack_items:
                    embed = discord.Embed(
                        title="🎒 空空的背包",
                        description="哎呀～你的背包空空的，像櫻花瓣一樣輕呢！🌸\n快去商店收集一些可愛的小東西吧～",
                        color=discord.Color.orange()
                    )
                    embed.set_thumbnail(url=ctx.author.display_avatar.url)
                    await ctx.respond(embed=embed, ephemeral=True)
                    return

                # 統計背包內容
                item_counts = {}
                for item in backpack_items:
                    item_name = item.get("name", "未知物品")
                    if item_name:  # 確保有物品名稱
                        item_counts[item_name] = item_counts.get(item_name, 0) + 1

                if not item_counts:
                    embed = discord.Embed(
                        title="🎒 空空的背包",
                        description="你的背包裡沒有有效的物品呢～",
                        color=discord.Color.orange()
                    )
                    await ctx.respond(embed=embed, ephemeral=True)
                    return

                # 限制選項數量（最多25個）
                limited_items = dict(list(item_counts.items())[:25])
                
                options = [
                    discord.SelectOption(
                        label=item_name[:25],  # 限制標籤長度
                        description=f"數量: {count}",
                        value=item_name
                    )
                    for item_name, count in limited_items.items()
                ]

                class BackpackSelect(Select):
                    """背包選擇器"""
                    def __init__(self):
                        super().__init__(
                            placeholder="選一件小東西吧～",
                            options=options,
                            min_values=1,
                            max_values=1
                        )

                    async def callback(self, interaction: discord.Interaction):
                        try:
                            # 權限檢查
                            if interaction.user.id != ctx.author.id:
                                await interaction.response.send_message(
                                    "❌ 嘻嘻，這可不是你的小背包哦～", 
                                    ephemeral=True
                                )
                                return

                            selected_item_name = self.values[0]
                            
                            # 驗證物品是否存在
                            item_data = next(
                                (item for item in shop_data if item.get("name") == selected_item_name), 
                                None
                            )

                            if not item_data:
                                await interaction.response.send_message(
                                    "❌ 幽幽子找不到這個東西的秘密呢…", 
                                    ephemeral=True
                                )
                                return

                            mp_value = item_data.get("MP", 0)
                            
                            # 構建互動嵌入
                            embed = discord.Embed(
                                title=f"🎒 {selected_item_name}",
                                description=(
                                    f"**壓力變化：** {mp_value:+d} 點\n"
                                    f"你想怎麼處理這個物品呢？"
                                ),
                                color=discord.Color.purple()
                            )
                            embed.set_footer(
                                text=f"幽幽子的背包系統 | 選擇時間：{datetime.now().strftime('%H:%M:%S')}"
                            )

                            # 創建動作按鈕
                            use_button = Button(
                                label="享用它～", 
                                style=discord.ButtonStyle.success,
                                emoji="🍽️"
                            )
                            donate_button = Button(
                                label="送給幽幽子", 
                                style=discord.ButtonStyle.secondary,
                                emoji="💝"
                            )

                            async def use_callback(use_inter: discord.Interaction):
                                try:
                                    if use_inter.user.id != ctx.author.id:
                                        await use_inter.response.send_message(
                                            "❌ 這可不是你的選擇啦～", 
                                            ephemeral=True
                                        )
                                        return

                                    confirm_embed = discord.Embed(
                                        title="❓ 確認使用",
                                        description=f"真的要用 **{selected_item_name}** 嗎？",
                                        color=discord.Color.orange()
                                    )
                                    confirm_embed.add_field(
                                        name="壓力變化",
                                        value=f"{mp_value:+d} 點",
                                        inline=False
                                    )

                                    confirm_button = Button(
                                        label="確定使用", 
                                        style=discord.ButtonStyle.success,
                                        emoji="✅"
                                    )
                                    cancel_button = Button(
                                        label="取消", 
                                        style=discord.ButtonStyle.danger,
                                        emoji="❌"
                                    )

                                    async def confirm_use(confirm_inter: discord.Interaction):
                                        try:
                                            if confirm_inter.user.id != ctx.author.id:
                                                await confirm_inter.response.send_message(
                                                    "❌ 別搶幽幽子的點心哦～", 
                                                    ephemeral=True
                                                )
                                                return

                                            # 重新獲取鎖並更新資料
                                            async with user_lock:
                                                user_file_path = f"{data_manager.config_dir}/user_config.json"
                                                with self._safe_data_access(data_manager, user_file_path, "json") as user_data:
                                                    current_mp = user_data[guild_id][user_id]["MP"]
                                                    new_mp = max(0, current_mp + mp_value)  # ✅ 正確：MP 是壓力值
                                                    user_data[guild_id][user_id]["MP"] = new_mp

                                                    # 移除物品
                                                    backpack = user_data[guild_id][user_id]["backpack"]
                                                    for i, item in enumerate(backpack):
                                                        if item.get("name") == selected_item_name:
                                                            backpack.pop(i)
                                                            break

                                            effect_desc = f"壓力{'減少' if mp_value < 0 else '增加'}了 {abs(mp_value)} 點～"
                                            await confirm_inter.response.edit_message(
                                                content=(
                                                    f"🎉 你享用了 **{selected_item_name}**！\n"
                                                    f"{effect_desc}\n"
                                                    f"現在的壓力值：{new_mp} 點"
                                                ),
                                                embed=None,
                                                view=None
                                            )
                                        except Exception as e:
                                            self.logger.error(f"使用物品錯誤: {e}")
                                            await confirm_inter.response.send_message(
                                                "❌ 操作失敗，請稍後再試～", 
                                                ephemeral=True
                                            )

                                    async def cancel_use(cancel_inter: discord.Interaction):
                                        await cancel_inter.response.edit_message(
                                            content="🔄 已取消操作，物品已保留～",
                                            embed=None,
                                            view=None
                                        )

                                    confirm_button.callback = confirm_use
                                    cancel_button.callback = cancel_use

                                    confirm_view = BackpackView(timeout=60.0)
                                    confirm_view.add_item(confirm_button)
                                    confirm_view.add_item(cancel_button)

                                    await use_inter.response.edit_message(
                                        embed=confirm_embed,
                                        view=confirm_view
                                    )
                                except Exception as e:
                                    self.logger.error(f"使用回調錯誤: {e}")
                                    await use_inter.response.send_message(
                                        "❌ 操作失敗，請稍後再試～", 
                                        ephemeral=True
                                    )

                            async def donate_callback(donate_inter: discord.Interaction):
                                try:
                                    if donate_inter.user.id != ctx.author.id:
                                        await donate_inter.response.send_message(
                                            "❌ 這可不是你的禮物哦～", 
                                            ephemeral=True
                                        )
                                        return

                                    # 特殊物品檢查
                                    if selected_item_name in ["香烟", "台灣啤酒"]:
                                        await donate_inter.response.edit_message(
                                            content=f"❌ 幽幽子才不要這種 **{selected_item_name}** 呢，拿回去吧！",
                                            embed=None,
                                            view=None
                                        )
                                        return

                                    confirm_embed = discord.Embed(
                                        title="💝 確認贈送",
                                        description=f"真的要把 **{selected_item_name}** 送給幽幽子嗎？",
                                        color=discord.Color.pink()
                                    )

                                    confirm_button = Button(
                                        label="確定贈送", 
                                        style=discord.ButtonStyle.success,
                                        emoji="💝"
                                    )
                                    cancel_button = Button(
                                        label="取消", 
                                        style=discord.ButtonStyle.danger,
                                        emoji="❌"
                                    )

                                    async def confirm_donate(confirm_inter: discord.Interaction):
                                        try:
                                            if confirm_inter.user.id != ctx.author.id:
                                                await confirm_inter.response.send_message(
                                                    "❌ 這可不是你能送的啦～", 
                                                    ephemeral=True
                                                )
                                                return

                                            # 重新獲取鎖並更新資料
                                            async with user_lock:
                                                user_file_path = f"{data_manager.config_dir}/user_config.json"
                                                with self._safe_data_access(data_manager, user_file_path, "json") as user_data:
                                                    backpack = user_data[guild_id][user_id]["backpack"]
                                                    for i, item in enumerate(backpack):
                                                        if item.get("name") == selected_item_name:
                                                            backpack.pop(i)
                                                            break

                                            await confirm_inter.response.edit_message(
                                                content=f"💝 你把 **{selected_item_name}** 送給了幽幽子！\n她開心地說：「謝謝你哦～❤」",
                                                embed=None,
                                                view=None
                                            )
                                        except Exception as e:
                                            self.logger.error(f"贈送物品錯誤: {e}")
                                            await confirm_inter.response.send_message(
                                                "❌ 操作失敗，請稍後再試～", 
                                                ephemeral=True
                                            )

                                    async def cancel_donate(cancel_inter: discord.Interaction):
                                        await cancel_inter.response.edit_message(
                                            content="🔄 已取消贈送，物品已保留～",
                                            embed=None,
                                            view=None
                                        )

                                    confirm_button.callback = confirm_donate
                                    cancel_button.callback = cancel_donate

                                    confirm_view = BackpackView(timeout=60.0)
                                    confirm_view.add_item(confirm_button)
                                    confirm_view.add_item(cancel_button)

                                    await donate_inter.response.edit_message(
                                        embed=confirm_embed,
                                        view=confirm_view
                                    )
                                except Exception as e:
                                    self.logger.error(f"贈送回調錯誤: {e}")
                                    await donate_inter.response.send_message(
                                        "❌ 操作失敗，請稍後再試～", 
                                        ephemeral=True
                                    )

                            use_button.callback = use_callback
                            donate_button.callback = donate_callback

                            action_view = BackpackView(timeout=300.0)
                            action_view.add_item(use_button)
                            action_view.add_item(donate_button)

                            await interaction.response.edit_message(embed=embed, view=action_view)

                        except Exception as e:
                            self.logger.error(f"選擇回調錯誤: {e}")
                            if not interaction.response.is_done():
                                await interaction.response.send_message(
                                    "❌ 操作失敗，請稍後再試～", 
                                    ephemeral=True
                                )

                # 構建初始嵌入
                embed = discord.Embed(
                    title="🎒 幽幽子的背包小天地",
                    description=(
                        f"🎯 **{ctx.author.display_name}** 的背包\n"
                        f"📋 **物品數量：** {len(backpack_items)} 件\n"
                        f"✨ **獨特物品：** {len(item_counts)} 種"
                    ),
                    color=discord.Color.from_rgb(255, 105, 180)
                )
                embed.set_thumbnail(url=ctx.author.display_avatar.url)
                embed.set_footer(
                    text="選擇一個物品來查看詳細資訊～ | 5分鐘後自動關閉",
                    icon_url=self.bot.user.display_avatar.url
                )

                view = BackpackView(timeout=300.0)
                view.add_item(BackpackSelect())

                await ctx.respond(embed=embed, view=view, ephemeral=True)

        except Exception as e:
            self.logger.error(f"背包指令錯誤: {e}")
            try:
                await ctx.respond(
                    "❌ 幽幽子的系統有點小狀況，請稍後再來～", 
                    ephemeral=True
                )
            except:
                pass  # 避免重複回應錯誤


def setup(bot):
    """註冊背包功能"""
    bot.add_cog(Backpack(bot))
    logging.getLogger("SakuraBot.commands.backpack").info("背包模組已載入")
