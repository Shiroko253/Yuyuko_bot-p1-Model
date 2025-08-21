import discord
from discord.ext import commands
from discord import ApplicationContext, Interaction
import random
import asyncio

class FishingButtons(discord.ui.View):
    def __init__(self, author_id, latest_fish_data, ctx, data_manager):
        super().__init__(timeout=180)
        self.author_id = author_id
        self.latest_fish_data = latest_fish_data
        self.ctx = ctx
        self.data_manager = data_manager

    async def interaction_check(self, interaction: Interaction):
        if interaction.user.id != self.author_id:
            await interaction.response.send_message("這不是你的按鈕哦！", ephemeral=True)
            return False
        return True

    async def on_timeout(self):
        try:
            await self.ctx.edit(
                content="釣魚操作已超時，請重新開始！",
                embed=None,
                view=None
            )
        except discord.errors.NotFound:
            pass

    @discord.ui.button(label="重複釣魚", style=discord.ButtonStyle.green)
    async def repeat_fishing(self, button: discord.ui.Button, interaction: Interaction):
        try:
            button.disabled = True
            button.label = "釣魚中..."
            await interaction.response.edit_message(view=self)
            await asyncio.sleep(2)
            new_fish_data = self.ctx.cog.generate_fish_data(self.ctx.fish_data)
            new_embed = self.ctx.cog.create_fishing_embed(new_fish_data, self.ctx.current_rod)
            new_view = FishingButtons(self.author_id, new_fish_data, self.ctx, self.data_manager)
            await interaction.edit_original_response(embed=new_embed, view=new_view)
        except discord.errors.NotFound:
            await interaction.followup.send("交互已失效，請重新開始釣魚！", ephemeral=True)
        except discord.errors.HTTPException as e:
            await interaction.followup.send(f"釣魚失敗，請稍後重試！(錯誤: {e})", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"發生錯誤：{e}", ephemeral=True)

    @discord.ui.button(label="保存漁獲", style=discord.ButtonStyle.blurple)
    async def save_fish(self, button: discord.ui.Button, interaction: Interaction):
        try:
            button.disabled = True
            button.label = "保存中..."
            await interaction.response.edit_message(view=self)

            user_id = str(self.ctx.user.id)
            guild_id = str(self.ctx.guild.id)
            fishingpack_path = "config/fishingpack.json"

            # 如果 main 有 bot.file_lock，這裡用它；否則 fallback 本地 asyncio.Lock
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

            button.label = "已保存漁獲"
            self.remove_item(button)
            await interaction.edit_original_response(view=self)
        except discord.errors.NotFound:
            await interaction.followup.send("交互已失效，無法保存漁獲！", ephemeral=True)
        except discord.errors.HTTPException as e:
            await interaction.followup.send(f"保存漁獲失敗，請稍後重試！(錯誤: {e})", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"保存漁獲時發生錯誤：{e}", ephemeral=True)

class Fish(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # 從 config/config.json 讀取 fish 種類
    def get_fish_data(self):
        data_manager = self.bot.data_manager
        try:
            fish_data = data_manager.load_json("config/config.json").get("fish")
            if fish_data and isinstance(fish_data, list):
                return fish_data
        except Exception as e:
            print(f"讀取 fish 資料時發生錯誤: {e}")
        return None

    def generate_fish_data(self, fish_data):
        selected_fish = random.choice(fish_data)
        fish_name = selected_fish.get("name", "未知魚種")
        fish_rarity = selected_fish.get("rarity", "unknown")
        try:
            min_size = float(selected_fish.get("min_size", 0.1))
            max_size = float(selected_fish.get("max_size", 0.3))
            fish_size = round(random.uniform(min_size, max_size), 2)
        except Exception:
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
            title="釣魚結果！",
            description=f"使用魚竿：{current_rod}",
            color=color
        )
        embed.add_field(name="捕獲魚種", value=fish_data["name"], inline=False)
        embed.add_field(name="稀有度", value=fish_data["rarity"].capitalize(), inline=True)
        embed.add_field(name="重量", value=f"{fish_data['size']} 公斤", inline=True)
        embed.set_footer(text="釣魚協會祝您 天天釣到大魚\n祝你每次都空軍")
        return embed

    @discord.slash_command(name="fish", description="進行一次釣魚")
    async def fish(self, ctx: ApplicationContext):
        fish_data = self.get_fish_data()
        if not fish_data:
            await ctx.respond("無法正確讀取魚資料，請聯絡管理員。", ephemeral=True)
            return

        ctx.fish_data = fish_data
        ctx.current_rod = "魚竿"
        ctx.cog = self  # 給View內部使用

        latest_fish_data = self.generate_fish_data(fish_data)
        embed = self.create_fishing_embed(latest_fish_data, ctx.current_rod)
        view = FishingButtons(ctx.user.id, latest_fish_data, ctx, self.bot.data_manager)
        await ctx.respond(embed=embed, view=view)

def setup(bot):
    bot.add_cog(Fish(bot))
