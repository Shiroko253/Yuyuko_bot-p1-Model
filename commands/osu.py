import discord
from discord.ext import commands
from discord import app_commands
import os

OSU_CLIENT_ID = os.getenv("OSU_CLIENT_ID")
OSU_CLIENT_SECRET = os.getenv("OSU_CLIENT_SECRET")
OSU_TOKEN_URL = "https://osu.ppy.sh/oauth/token"
OSU_API_BASE = "https://osu.ppy.sh/api/v2"
OSU_DATA_PATH = "config/osu_player.json"

# 支援模式及映射
OSU_MODE_MAP = {
    "std": 0,
    "taiko": 1,
    "mania": 3,
    "cbt": 2,  # std=0, taiko=1, ctb=2, mania=3
}
OSU_MODE_NAMES = {
    "std": "osu!standard",
    "taiko": "osu!taiko",
    "cbt": "osu!catch",
    "mania": "osu!mania"
}

class OsuCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def get_osu_token(self):
        payload = {
            "client_id": OSU_CLIENT_ID,
            "client_secret": OSU_CLIENT_SECRET,
            "grant_type": "client_credentials",
            "scope": "public"
        }
        async with self.bot.session.post(OSU_TOKEN_URL, json=payload) as resp:
            data = await resp.json()
            return data["access_token"]

    async def get_osu_user_data(self, username_or_id, token, mode=0):
        headers = {"Authorization": f"Bearer {token}"}
        async with self.bot.session.get(f"{OSU_API_BASE}/users/{username_or_id}/{mode}", headers=headers) as resp:
            return await resp.json()

    async def get_osu_recent(self, osu_id, token, mode=0, limit=1):
        headers = {"Authorization": f"Bearer {token}"}
        url = f"{OSU_API_BASE}/users/{osu_id}/scores/recent?mode={mode}&limit={limit}"
        async with self.bot.session.get(url, headers=headers) as resp:
            return await resp.json()

    async def get_osu_top(self, osu_id, token, mode=0, limit=1):
        headers = {"Authorization": f"Bearer {token}"}
        url = f"{OSU_API_BASE}/users/{osu_id}/scores/best?mode={mode}&limit={limit}"
        async with self.bot.session.get(url, headers=headers) as resp:
            return await resp.json()

    def load_osu_data(self):
        return self.bot.data_manager.load_json(OSU_DATA_PATH)
    
    def save_osu_data(self, data):
        self.bot.data_manager.save_json(OSU_DATA_PATH, data)

    # /osu_bind 主指令
    @app_commands.command(name="osu_bind", description="綁定你的 osu! 帳號")
    async def osu_bind(self, interaction: discord.Interaction, osu_username: str):
        await interaction.response.defer()
        token = await self.get_osu_token()
        user_data = await self.get_osu_user_data(osu_username, token, mode=0)
        if user_data.get("error"):
            await interaction.followup.send(f"綁定失敗，找不到 osu! 用戶 `{osu_username}`。")
            return
        osu_id = str(user_data["id"])
        osu_name = user_data["username"]
        osu_data = self.load_osu_data()
        osu_data[str(interaction.user.id)] = {
            "osu_name": osu_name,
            "osu_id": osu_id
        }
        self.save_osu_data(osu_data)
        await interaction.followup.send(f"已將你的 Discord 帳號綁定至 osu! 用戶 `{osu_name}` (id: {osu_id})！")

    # /osu_profile 主指令
    @app_commands.command(name="osu_profile", description="查詢 osu! profile（可查自己或@他人）")
    async def osu_profile(self, interaction: discord.Interaction, user: discord.User = None):
        await interaction.response.defer()
        user = user or interaction.user
        osu_data = self.load_osu_data()
        udata = osu_data.get(str(user.id))
        if not udata:
            await interaction.followup.send(f"{user.mention} 尚未綁定 osu! 帳號。請先用 `/osu_bind <osu用戶名>` 綁定。")
            return
        token = await self.get_osu_token()
        profile = await self.get_osu_user_data(udata["osu_id"], token, mode=0)
        if profile.get("error"):
            await interaction.followup.send("查詢 osu! profile 時發生錯誤。")
            return
        stats = profile.get("statistics", {})
        embed = discord.Embed(
            title=f"osu! profile - {profile['username']}",
            url=f"https://osu.ppy.sh/users/{profile['id']}",
            color=discord.Color.purple()
        )
        embed.set_thumbnail(url=profile["avatar_url"])
        embed.add_field(name="模式", value="osu!standard", inline=True)
        embed.add_field(name="全球排名", value=f"#{stats.get('global_rank', 'N/A')}", inline=True)
        embed.add_field(name="pp", value=stats.get("pp", "N/A"), inline=True)
        embed.add_field(name="等級", value=stats.get("level", {}).get("current", 'N/A'), inline=True)
        embed.add_field(name="遊玩次數", value=stats.get("play_count", "N/A"), inline=True)
        await interaction.followup.send(embed=embed)

    # /osu_recent 群組及子指令
    osu_recent = app_commands.Group(name="osu_recent", description="查詢 osu! 最近遊玩紀錄")

    @osu_recent.command(name="rs", description="查詢 osu!standard 的最近遊玩")
    async def osu_recent_rs(self, interaction: discord.Interaction, user: discord.User = None):
        await self._osu_recent_mode(interaction, user, "std")

    @osu_recent.command(name="rt", description="查詢 osu!taiko 的最近遊玩")
    async def osu_recent_rt(self, interaction: discord.Interaction, user: discord.User = None):
        await self._osu_recent_mode(interaction, user, "taiko")

    @osu_recent.command(name="rm", description="查詢 osu!mania 的最近遊玩")
    async def osu_recent_rm(self, interaction: discord.Interaction, user: discord.User = None):
        await self._osu_recent_mode(interaction, user, "mania")

    @osu_recent.command(name="rc", description="查詢 osu!catch 的最近遊玩")
    async def osu_recent_rc(self, interaction: discord.Interaction, user: discord.User = None):
        await self._osu_recent_mode(interaction, user, "cbt")

    async def _osu_recent_mode(self, interaction, user, mode_key):
        await interaction.response.defer()
        user = user or interaction.user
        osu_data = self.load_osu_data()
        udata = osu_data.get(str(user.id))
        if not udata:
            await interaction.followup.send(f"{user.mention} 尚未綁定 osu! 帳號。請先用 `/osu_bind <osu用戶名>` 綁定。")
            return
        token = await self.get_osu_token()
        mode = OSU_MODE_MAP[mode_key]
        data = await self.get_osu_recent(udata["osu_id"], token, mode=mode, limit=1)
        if not data:
            await interaction.followup.send(f"{user.mention} 在 {OSU_MODE_NAMES[mode_key]} 沒有最近遊玩紀錄。")
            return
        play = data[0]
        beatmap = play.get("beatmap", {})
        embed = discord.Embed(
            title=f"最近遊玩 - {beatmap.get('title', '未知譜面')} [{beatmap.get('version', '')}]",
            url=f"https://osu.ppy.sh/b/{beatmap.get('id', '')}",
            color=discord.Color.teal()
        )
        embed.add_field(name="分數", value=play.get("score", "N/A"), inline=True)
        embed.add_field(name="等級", value=play.get("rank", "N/A"), inline=True)
        embed.add_field(name="準確率", value=f"{play.get('accuracy', 0)*100:.2f}%", inline=True)
        embed.add_field(name="Combo", value=play.get("max_combo", "N/A"), inline=True)
        embed.add_field(name="Mods", value=" ".join(play.get("mods", [])) or "None", inline=True)
        embed.set_footer(text=OSU_MODE_NAMES[mode_key])
        await interaction.followup.send(embed=embed)

    # /osu_top 主指令 + mode 參數
    @app_commands.command(name="osu_top", description="查詢 osu! 最佳紀錄（可選模式）")
    @app_commands.describe(mode="osu! 模式", user="指定查詢的 Discord 帳號")
    @app_commands.choices(mode=[
        app_commands.Choice(name="standard", value="std"),
        app_commands.Choice(name="taiko", value="taiko"),
        app_commands.Choice(name="mania", value="mania"),
        app_commands.Choice(name="catch", value="cbt"),
    ])
    async def osu_top(
        self,
        interaction: discord.Interaction,
        mode: app_commands.Choice[str] = None,
        user: discord.User = None
    ):
        await interaction.response.defer()
        user = user or interaction.user
        osu_data = self.load_osu_data()
        udata = osu_data.get(str(user.id))
        if not udata:
            await interaction.followup.send(f"{user.mention} 尚未綁定 osu! 帳號。請先用 `/osu_bind <osu用戶名>` 綁定。")
            return
        token = await self.get_osu_token()
        mode_key = mode.value if mode else "std"
        mode_val = OSU_MODE_MAP[mode_key]
        data = await self.get_osu_top(udata["osu_id"], token, mode=mode_val, limit=1)
        if not data:
            await interaction.followup.send(f"{user.mention} 在 {OSU_MODE_NAMES[mode_key]} 沒有 Top 紀錄。")
            return
        play = data[0]
        beatmap = play.get("beatmap", {})
        embed = discord.Embed(
            title=f"最佳紀錄 - {beatmap.get('title', '未知譜面')} [{beatmap.get('version', '')}]",
            url=f"https://osu.ppy.sh/b/{beatmap.get('id', '')}",
            color=discord.Color.orange()
        )
        embed.add_field(name="分數", value=play.get("score", "N/A"), inline=True)
        embed.add_field(name="等級", value=play.get("rank", "N/A"), inline=True)
        embed.add_field(name="準確率", value=f"{play.get('accuracy', 0)*100:.2f}%", inline=True)
        embed.add_field(name="Combo", value=play.get("max_combo", "N/A"), inline=True)
        embed.add_field(name="Mods", value=" ".join(play.get("mods", [])) or "None", inline=True)
        embed.set_footer(text=OSU_MODE_NAMES[mode_key])
        await interaction.followup.send(embed=embed)

    async def cog_load(self):
        self.bot.tree.add_command(self.osu_recent)

async def setup(bot):
    await bot.add_cog(OsuCog(bot))
