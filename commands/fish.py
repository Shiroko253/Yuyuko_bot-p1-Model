import discord
from discord.ext import commands
from discord import ApplicationContext, Interaction
import random
import asyncio
import logging

class FishingButtons(discord.ui.View):
    def __init__(self, author_id, latest_fish_data, ctx, data_manager, cog):
        super().__init__(timeout=180)
        self.author_id = author_id
        self.latest_fish_data = latest_fish_data
        self.ctx = ctx
        self.data_manager = data_manager
        self.cog = cog

    async def interaction_check(self, interaction: Interaction):
        if interaction.user.id != self.author_id:
            await interaction.response.send_message("這不是你的櫻花釣魚按鈕哦～幽幽子會阻止你！", ephemeral=True)
            return False
        return True

    async def on_timeout(self):
        try:
            await self.ctx.edit(
                content="釣魚操作已超時，幽幽子等你回來再釣一次吧～",
                embed=None,
                view=None
            )
        except discord.errors.NotFound:
            pass

    @discord.ui.button(label="🌸 再釣一次櫻花魚", style=discord.ButtonStyle.green)
    async def repeat_fishing(self, button: discord.ui.Button, interaction: Interaction):
        try:
            button.disabled = True
            button.label = "幽幽子撒櫻花中..."
            await interaction.response.edit_message(view=self)
            await asyncio.sleep(2)
            new_fish_data = self.cog.generate_fish_data(self.ctx.fish_data)
            new_embed = self.cog.create_fishing_embed(new_fish_data, self.ctx.current_rod)
            new_view = FishingButtons(self.author_id, new_fish_data, self.ctx, self.data_manager, self.cog)
            await interaction.edit_original_response(embed=new_embed, view=new_view)
        except discord.errors.NotFound:
            await interaction.followup.send("櫻花釣魚交互已失效，請重新開始湖邊釣魚！", ephemeral=True)
        except discord.errors.HTTPException as e:
            await interaction.followup.send(f"釣魚失敗，櫻花湖暫時閉合！(錯誤: {e})", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"發生小故障：{e}\n幽幽子會幫你修好！", ephemeral=True)

    @discord.ui.button(label="保存櫻花漁獲", style=discord.ButtonStyle.blurple)
    async def save_fish(self, button: discord.ui.Button, interaction: Interaction):
        try:
            button.disabled = True
            button.label = "保存櫻花漁獲中..."
            await interaction.response.edit_message(view=self)

            user_id = str(self.ctx.user.id)
            guild_id = str(self.ctx.guild.id)
            fishingpack_path = "config/fishingpack.json"
            file_lock = getattr(self.ctx.bot, "file_lock", asyncio.Lock())

            async with file_lock:
                fishingpack_data = self.data_manager.load_json(fishingpack_path) or {}
                fishingpack_data.setdefault(user_id, {}).setdefault(guild_id, {"fishes": []})
                fishingpack_data[user_id][guild_id]["fishes"].append({
                    "name": self.latest_fish_data["name"],
                    "rarity": self.latest_fish_data["rarity"],
                    "size": self.latest_fish_data["size"],
                    "rod": self.ctx.current_rod
                })
                self.data_manager.save_json(fishingpack_path, fishingpack_data)

            button.label = "已保存櫻花漁獲"
            self.remove_item(button)
            await interaction.edit_original_response(view=self)
        except discord.errors.NotFound:
            await interaction.followup.send("櫻花保存失效，幽幽子會幫你修好！", ephemeral=True)
        except discord.errors.HTTPException as e:
            await interaction.followup.send(f"保存漁獲失敗～請稍後再試！(錯誤: {e})", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"保存櫻花漁獲時發生小故障：{e}", ephemeral=True)

class Fish(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_fish_data(self):
        data_manager = self.bot.data_manager
        try:
            fish_data = data_manager.load_json("config/config.json").get("fish")
            if fish_data and isinstance(fish_data, list):
                return fish_data
        except Exception as e:
            logging.error(f"幽幽子讀取湖中魚資料時迷糊了: {e}")
        return None

    def generate_fish_data(self, fish_data):
        selected_fish = random.choice(fish_data)
        fish_name = selected_fish.get("name", "未知櫻花魚種")
        fish_rarity = selected_fish.get("rarity", "unknown")
        try:
            min_size = float(selected_fish.get("min_size", 0.1))
            max_size = float(selected_fish.get("max_size", 0.3))
            fish_size = round(random.uniform(min_size, max_size), 2)
        except Exception as e:
            logging.warning(f"幽幽子生成櫻花魚時遇到小問題: {e}")
            fish_size = 0.1
        return {"name": fish_name, "rarity": fish_rarity, "size": fish_size}

    def create_fishing_embed(self, fish_data, current_rod):
        rarity_colors = {
            "common": discord.Color.green(),
            "uncommon": discord.Color.blue(),
            "rare": discord.Color.purple(),
            "legendary": discord.Color.orange(),
            "deify": discord.Color.gold(),
            "unknown": discord.Color.dark_gray(),
        }
        color = rarity_colors.get(fish_data["rarity"], discord.Color.light_gray())
        embed = discord.Embed(
            title="🌸 幽幽子的櫻花湖釣魚結果！",
            description=f"使用的櫻花魚竿：{current_rod}\n幽幽子在湖邊為你加油～",
            color=color
        )
        embed.add_field(name="捕獲櫻花魚種", value=fish_data["name"], inline=False)
        embed.add_field(name="稀有度", value=fish_data["rarity"].capitalize(), inline=True)
        embed.add_field(name="重量", value=f"{fish_data['size']} 公斤", inline=True)
        embed.set_footer(text="幽幽子祝你天天釣到靈魂櫻花魚～不要空軍喲！")
        return embed

    @discord.slash_command(name="fish", description="幽幽子邀你到櫻花湖畔釣魚～")
    async def fish(self, ctx: ApplicationContext):
        fish_data = self.get_fish_data()
        if not fish_data:
            await ctx.respond("幽幽子迷糊了，無法正確讀取櫻花湖魚資料～請聯絡管理員！", ephemeral=True)
            return

        ctx.fish_data = fish_data
        ctx.current_rod = "櫻花魚竿"

        latest_fish_data = self.generate_fish_data(fish_data)
        embed = self.create_fishing_embed(latest_fish_data, ctx.current_rod)
        view = FishingButtons(ctx.user.id, latest_fish_data, ctx, self.bot.data_manager, self)
        await ctx.respond(embed=embed, view=view)

def setup(bot):
    bot.add_cog(Fish(bot))