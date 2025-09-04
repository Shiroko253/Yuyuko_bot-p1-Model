import discord
from discord.ext import commands
from discord.ui import View, Select, Button
import logging

class Backpack(commands.Cog):
    """
    ✿ 幽幽子的背包小空間 ✿
    來看看你收集了哪些可愛小東西吧～幽幽子會一直陪著你♪
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="backpack", description="幽幽子帶你看看背包裡的小寶貝哦～")
    async def backpack(self, ctx: discord.ApplicationContext):
        guild_id = str(ctx.guild.id)
        user_id = str(ctx.author.id)

        # 幽幽子溫柔地從數據管理員要來資料
        data_manager = ctx.bot.data_manager
        user_data = data_manager.load_yaml("config_user.yml")
        shop_data = data_manager.load_yaml("shop.yml", default=[])

        user_data.setdefault(guild_id, {})
        user_data[guild_id].setdefault(user_id, {"MP": 200, "backpack": []})

        backpack_items = user_data[guild_id][user_id]["backpack"]

        if not backpack_items:
            await ctx.respond("哎呀～你的背包空空的，像櫻花瓣一樣輕呢！🌸", ephemeral=True)
            return

        # 統計背包內容（幽幽子溫柔地數著你的寶貝）
        item_counts = {}
        for item in backpack_items:
            item_name = item["name"]
            item_counts[item_name] = item_counts.get(item_name, 0) + 1

        options = [
            discord.SelectOption(
                label=item_name,
                description=f"數量: {count}",
                value=item_name
            )
            for item_name, count in item_counts.items()
        ]

        class BackpackSelect(Select):
            """
            ✿ 幽幽子的背包選擇器 ✿
            選一件小東西，讓幽幽子陪你一起欣賞吧～
            """
            def __init__(self):
                super().__init__(
                    placeholder="選一件小東西吧～",
                    options=options,
                    min_values=1,
                    max_values=1
                )

            async def callback(self, interaction: discord.Interaction):
                if interaction.user.id != ctx.author.id:
                    await interaction.response.send_message("嘻嘻，這可不是你的小背包哦～", ephemeral=True)
                    return

                selected_item_name = self.values[0]
                item_data = next((item for item in shop_data if item["name"] == selected_item_name), None)

                if not item_data:
                    await interaction.response.send_message("哎呀～幽幽子找不到這個東西的秘密呢…", ephemeral=True)
                    return

                mp_value = item_data.get("MP", 0)

                embed = discord.Embed(
                    title=f"幽幽子的背包小角落 - {selected_item_name}",
                    description=f"這個小東西能讓你輕鬆 {mp_value} 點壓力哦～\n你想怎麼處理它呢？",
                    color=discord.Color.from_rgb(255, 105, 180)
                )

                use_button = Button(label="享用它～", style=discord.ButtonStyle.success)
                donate_button = Button(label="送給幽幽子", style=discord.ButtonStyle.secondary)

                async def use_callback(use_inter: discord.Interaction):
                    if use_inter.user.id != ctx.author.id:
                        await use_inter.response.send_message("這可不是你的選擇啦～", ephemeral=True)
                        return

                    confirm_button = Button(label="確定要用～", style=discord.ButtonStyle.success)
                    cancel_button = Button(label="再想想", style=discord.ButtonStyle.danger)

                    async def confirm_use(confirm_inter: discord.Interaction):
                        if confirm_inter.user.id != ctx.author.id:
                            await confirm_inter.response.send_message("嘻嘻，別搶幽幽子的點心哦～", ephemeral=True)
                            return

                        user_data[guild_id][user_id]["MP"] = max(
                            0, user_data[guild_id][user_id]["MP"] - mp_value
                        )
                        for i, item in enumerate(user_data[guild_id][user_id]["backpack"]):
                            if item["name"] == selected_item_name:
                                user_data[guild_id][user_id]["backpack"].pop(i)
                                break
                        data_manager.save_yaml("config_user.yml", user_data)

                        await confirm_inter.response.edit_message(
                            content=(
                                f"你享用了 **{selected_item_name}**，壓力像櫻花一樣飄走了 {mp_value} 點！\n"
                                f"現在的 MP：{user_data[guild_id][user_id]['MP']} 點，真是輕鬆呢～🌸"
                            ),
                            embed=None,
                            view=None
                        )

                    async def cancel_use(cancel_inter: discord.Interaction):
                        await cancel_inter.response.edit_message(
                            content="好吧～這次就先留著它吧～", embed=None, view=None
                        )

                    confirm_button.callback = confirm_use
                    cancel_button.callback = cancel_use

                    confirm_view = View()
                    confirm_view.add_item(confirm_button)
                    confirm_view.add_item(cancel_button)

                    await use_inter.response.edit_message(
                        content=f"真的要用 **{selected_item_name}** 嗎？幽幽子幫你再確認一下哦～",
                        embed=None,
                        view=confirm_view
                    )

                async def donate_callback(donate_inter: discord.Interaction):
                    if donate_inter.user.id != ctx.author.id:
                        await donate_inter.response.send_message("這可不是你的禮物哦～", ephemeral=True)
                        return

                    if selected_item_name in ["香烟", "台灣啤酒"]:
                        await donate_inter.response.edit_message(
                            content=f"哎呀～幽幽子才不要這種 **{selected_item_name}** 呢，拿回去吧！",
                            embed=None,
                            view=None
                        )
                        return

                    confirm_button = Button(label="確定送出～", style=discord.ButtonStyle.success)
                    cancel_button = Button(label="再想想", style=discord.ButtonStyle.danger)

                    async def confirm_donate(confirm_inter: discord.Interaction):
                        if confirm_inter.user.id != ctx.author.id:
                            await confirm_inter.response.send_message("嘻嘻，這可不是你能送的啦～", ephemeral=True)
                            return

                        for i, item in enumerate(user_data[guild_id][user_id]["backpack"]):
                            if item["name"] == selected_item_name:
                                user_data[guild_id][user_id]["backpack"].pop(i)
                                break
                        data_manager.save_yaml("config_user.yml", user_data)

                        await confirm_inter.response.edit_message(
                            content=f"你把 **{selected_item_name}** 送給了幽幽子，她開心地說：「謝謝你哦～❤」",
                            embed=None,
                            view=None
                        )

                    async def cancel_donate(cancel_inter: discord.Interaction):
                        await cancel_inter.response.edit_message(
                            content="好吧～這次就先留著吧，幽幽子也不介意哦～", embed=None, view=None
                        )

                    confirm_button.callback = confirm_donate
                    cancel_button.callback = cancel_donate

                    confirm_view = View()
                    confirm_view.add_item(confirm_button)
                    confirm_view.add_item(cancel_button)

                    await donate_inter.response.edit_message(
                        content=f"真的要把 **{selected_item_name}** 送給幽幽子嗎？她可是很期待呢～🌸",
                        embed=None,
                        view=confirm_view
                    )

                use_button.callback = use_callback
                donate_button.callback = donate_callback

                action_view = View()
                action_view.add_item(use_button)
                action_view.add_item(donate_button)

                await interaction.response.edit_message(embed=embed, view=action_view)

        embed = discord.Embed(
            title="幽幽子的背包小天地",
            description="來看看你收集了哪些可愛的小東西吧～🌸",
            color=discord.Color.from_rgb(255, 105, 180)
        )
        embed.set_footer(text="幽幽子會一直陪著你的哦～")

        view = View()
        view.add_item(BackpackSelect())

        await ctx.respond(embed=embed, view=view, ephemeral=False)

def setup(bot):
    """
    ✿ 幽幽子優雅地將背包功能裝進 bot 裡 ✿
    """
    bot.add_cog(Backpack(bot))