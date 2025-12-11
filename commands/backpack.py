import discord
from discord.ext import commands
from discord.ui import View, Select, Button
import logging

logger = logging.getLogger("SakuraBot.commands.backpack")


class Backpack(commands.Cog):
    """
    ✿ 幽幽子的背包小空間 ✿
    來看看你收集了哪些可愛小東西吧～幽幽子會一直陪著你♪
    """

    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @discord.slash_command(
        name="backpack",
        description="幽幽子帶你看看背包裡的小寶貝哦～"
    )
    async def backpack(self, ctx: discord.ApplicationContext):
        """查看背包並管理物品"""
        # 檢查是否在伺服器中
        if not ctx.guild:
            await ctx.respond("❌ 背包功能只能在伺服器裡使用哦～", ephemeral=True)
            return

        guild_id = str(ctx.guild.id)
        user_id = str(ctx.author.id)

        # 獲取數據管理器
        if not hasattr(self.bot, "data_manager"):
            await ctx.respond("❌ 幽幽子的背包系統暫時找不到了...", ephemeral=True)
            logger.error("data_manager 不存在")
            return

        data_manager = self.bot.data_manager

        # 載入用戶數據和商店數據
        try:
            user_data = data_manager._load_yaml("config/config_user.yml", default={})
            # 修正: 從 config.json 載入商店數據
            config_data = data_manager._load_json("config/config.json", default={})
            shop_data = config_data.get("shop_item", [])
        except Exception as e:
            logger.error(f"載入背包數據失敗: {e}")
            await ctx.respond("❌ 背包數據載入失敗...", ephemeral=True)
            return

        # 初始化用戶數據
        if guild_id not in user_data:
            user_data[guild_id] = {}
        if user_id not in user_data[guild_id]:
            user_data[guild_id][user_id] = {"MP": 200, "backpack": []}

        backpack_items = user_data[guild_id][user_id].get("backpack", [])

        # 檢查背包是否為空
        if not backpack_items:
            embed = discord.Embed(
                title="🎒 空空的背包",
                description="哎呀～你的背包空空的，像櫻花瓣一樣輕呢！🌸\n\n快去 `/shop` 買些東西吧～",
                color=discord.Color.from_rgb(255, 182, 193)
            )
            await ctx.respond(embed=embed, ephemeral=True)
            return

        # 統計背包內容
        item_counts = {}
        for item in backpack_items:
            item_name = item.get("name", "未知物品")
            item_counts[item_name] = item_counts.get(item_name, 0) + 1

        # 創建選項列表
        options = [
            discord.SelectOption(
                label=item_name,
                description=f"數量: {count}",
                value=item_name,
                emoji="🎁"
            )
            for item_name, count in sorted(item_counts.items())
        ]

        # 限制選項數量 (Discord 限制最多 25 個)
        if len(options) > 25:
            options = options[:25]

        class BackpackSelect(Select):
            """幽幽子的背包選擇器"""

            def __init__(self):
                super().__init__(
                    placeholder="選一件小東西吧～",
                    options=options,
                    min_values=1,
                    max_values=1
                )

            async def callback(self, interaction: discord.Interaction):
                # 權限檢查
                if interaction.user.id != ctx.author.id:
                    await interaction.response.send_message(
                        "嘻嘻，這可不是你的小背包哦～",
                        ephemeral=True
                    )
                    return

                selected_item_name = self.values[0]

                # 從商店數據中查找物品資訊
                item_data = next(
                    (item for item in shop_data if item.get("name") == selected_item_name),
                    None
                )

                if not item_data:
                    await interaction.response.send_message(
                        "哎呀～幽幽子找不到這個東西的秘密呢...",
                        ephemeral=True
                    )
                    return

                mp_value = item_data.get("MP", 0)
                item_count = item_counts.get(selected_item_name, 0)

                # 構建物品詳情 Embed
                embed = discord.Embed(
                    title=f"🎒 {selected_item_name}",
                    description=(
                        f"**效果:** 減少 {mp_value} 點壓力\n"
                        f"**擁有數量:** {item_count}\n"
                        f"**當前 MP:** {user_data[guild_id][user_id]['MP']}\n\n"
                        "你想怎麼處理它呢？"
                    ),
                    color=discord.Color.from_rgb(255, 105, 180)
                )
                embed.set_footer(text="幽幽子陪你一起做決定～")

                # 創建按鈕
                use_button = Button(
                    label="享用它～",
                    style=discord.ButtonStyle.success,
                    emoji="✨"
                )
                donate_button = Button(
                    label="送給幽幽子",
                    style=discord.ButtonStyle.secondary,
                    emoji="💝"
                )
                cancel_button = Button(
                    label="算了",
                    style=discord.ButtonStyle.danger,
                    emoji="❌"
                )

                async def use_callback(use_inter: discord.Interaction):
                    """使用物品"""
                    if use_inter.user.id != ctx.author.id:
                        await use_inter.response.send_message(
                            "這可不是你的選擇啦～",
                            ephemeral=True
                        )
                        return

                    # 移除物品
                    for i, item in enumerate(user_data[guild_id][user_id]["backpack"]):
                        if item.get("name") == selected_item_name:
                            user_data[guild_id][user_id]["backpack"].pop(i)
                            break

                    # 減少 MP
                    old_mp = user_data[guild_id][user_id]["MP"]
                    user_data[guild_id][user_id]["MP"] = max(0, old_mp - mp_value)
                    new_mp = user_data[guild_id][user_id]["MP"]

                    # 保存數據
                    data_manager._save_yaml("config/config_user.yml", user_data)

                    result_embed = discord.Embed(
                        title="✨ 使用成功",
                        description=(
                            f"你享用了 **{selected_item_name}**，壓力像櫻花一樣飄走了！\n\n"
                            f"**MP 變化:** {old_mp} → {new_mp} (-{mp_value})\n"
                            f"真是輕鬆呢～🌸"
                        ),
                        color=discord.Color.green()
                    )

                    await use_inter.response.edit_message(
                        embed=result_embed,
                        view=None
                    )
                    logger.info(
                        f"{ctx.author} 使用了 {selected_item_name}, "
                        f"MP: {old_mp} -> {new_mp}"
                    )

                async def donate_callback(donate_inter: discord.Interaction):
                    """捐贈物品給幽幽子"""
                    if donate_inter.user.id != ctx.author.id:
                        await donate_inter.response.send_message(
                            "這可不是你的禮物哦～",
                            ephemeral=True
                        )
                        return

                    # 幽幽子不喜歡的物品
                    blacklist = ["香烟", "台灣啤酒", "煙", "酒"]
                    if selected_item_name in blacklist:
                        reject_embed = discord.Embed(
                            title="❌ 幽幽子婉拒了",
                            description=f"哎呀～幽幽子才不要這種 **{selected_item_name}** 呢，拿回去吧！",
                            color=discord.Color.red()
                        )
                        await donate_inter.response.edit_message(
                            embed=reject_embed,
                            view=None
                        )
                        return

                    # 移除物品
                    for i, item in enumerate(user_data[guild_id][user_id]["backpack"]):
                        if item.get("name") == selected_item_name:
                            user_data[guild_id][user_id]["backpack"].pop(i)
                            break

                    # 保存數據
                    data_manager._save_yaml("config/config_user.yml", user_data)

                    success_embed = discord.Embed(
                        title="💝 感謝你的禮物",
                        description=f"你把 **{selected_item_name}** 送給了幽幽子！\n\n她開心地說：「謝謝你哦～❤」",
                        color=discord.Color.from_rgb(255, 105, 180)
                    )

                    await donate_inter.response.edit_message(
                        embed=success_embed,
                        view=None
                    )
                    logger.info(f"{ctx.author} 捐贈了 {selected_item_name} 給幽幽子")

                async def cancel_callback(cancel_inter: discord.Interaction):
                    """取消操作"""
                    if cancel_inter.user.id != ctx.author.id:
                        return

                    await cancel_inter.response.edit_message(
                        content="好吧～這次就先留著它吧～",
                        embed=None,
                        view=None
                    )

                use_button.callback = use_callback
                donate_button.callback = donate_callback
                cancel_button.callback = cancel_callback

                action_view = View(timeout=180)
                action_view.add_item(use_button)
                action_view.add_item(donate_button)
                action_view.add_item(cancel_button)

                await interaction.response.edit_message(embed=embed, view=action_view)

        # 主 Embed
        embed = discord.Embed(
            title="🎒 幽幽子的背包小天地",
            description=(
                f"來看看你收集了哪些可愛的小東西吧～🌸\n\n"
                f"**物品種類:** {len(item_counts)}\n"
                f"**物品總數:** {len(backpack_items)}\n"
                f"**當前 MP:** {user_data[guild_id][user_id]['MP']}"
            ),
            color=discord.Color.from_rgb(255, 105, 180)
        )
        embed.set_footer(text="幽幽子會一直陪著你的哦～")
        embed.set_thumbnail(url=ctx.author.display_avatar.url)

        view = View(timeout=300)
        view.add_item(BackpackSelect())

        await ctx.respond(embed=embed, view=view, ephemeral=False)


def setup(bot: discord.Bot):
    """將幽幽子的背包功能裝進 bot 裡"""
    bot.add_cog(Backpack(bot))
    logger.info("背包系統已載入")
