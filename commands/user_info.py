import discord
from discord.ext import commands
from datetime import timezone
from zoneinfo import ZoneInfo
import random
import os

class UserInfo(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @discord.slash_command(name="user_info", description="幽幽子為你窺探用戶的靈魂資訊～")
    async def user_info(self, ctx: discord.ApplicationContext, user: discord.Member = None):
        user = user or ctx.author
        guild_id = str(ctx.guild.id) if ctx.guild else "DM"
        user_id = str(user.id)
        tz = ZoneInfo('Asia/Taipei')

        data_manager = getattr(self.bot, "data_manager", None)
        if data_manager and hasattr(data_manager, "load_yaml"):
            user_data = data_manager.load_yaml("config/config_user.yml")
        else:
            user_data = {}

        if not user.bot:
            guild_config = user_data.get(guild_id, {})
            user_config = guild_config.get(user_id, {})
            work_cooldown = user_config.get('work_cooldown', '未工作')
            job = user_config.get('job', '無職業')
            mp = user_config.get('MP', 0)
        else:
            work_cooldown, job, mp = 'N/A', 'N/A', 0

        banner_url = None
        if not user.bot:
            try:
                fetched_user = await ctx.bot.fetch_user(user.id)
                if fetched_user.banner:
                    banner_url = fetched_user.banner.url
            except Exception:
                banner_url = None

        avatar_type = "伺服器專屬頭像" if isinstance(user, discord.Member) and user.guild_avatar else "全局頭像"
        avatar_url = user.guild_avatar.url if isinstance(user, discord.Member) and user.guild_avatar else user.display_avatar.url

        embed = discord.Embed(
            title="🌸 幽幽子窺探的靈魂資訊 🌸",
            description=(
                f"我是西行寺幽幽子，亡魂之主，現在為你揭示 {user.mention} 的靈魂～\n"
                "亡魂的命運在櫻花下閃耀，讓我們來看看這位旅人的故事吧…"
            ),
            color=discord.Color.from_rgb(255, 182, 193)
        )
        embed.set_thumbnail(url=avatar_url)
        embed.add_field(name="名稱", value=f"{user.name}#{user.discriminator}", inline=True)
        embed.add_field(name="靈魂編號", value=user.id, inline=True)
        embed.add_field(
            name="靈魂誕生之日",
            value=user.created_at.replace(tzinfo=timezone.utc).astimezone(tz).strftime("%Y-%m-%d %H:%M:%S"),
            inline=True
        )
        embed.add_field(name="頭像類型", value=avatar_type, inline=True)

        if isinstance(user, discord.Member):
            embed.add_field(name="伺服器化名", value=user.nick or "無", inline=True)
            embed.add_field(
                name="加入此地之日",
                value=user.joined_at.replace(tzinfo=timezone.utc).astimezone(tz).strftime("%Y-%m-%d %H:%M:%S") if user.joined_at else "無法窺見",
                inline=True
            )
            embed.add_field(name="最高身份", value=user.top_role.mention if user.top_role else "無", inline=True)
            embed.add_field(name="是機械之魂？", value="是" if user.bot else "否", inline=True)
        else:
            embed.add_field(name="伺服器化名", value="此魂不在當前之地", inline=True)

        embed.add_field(name="個人橫幅", value="已設置個人橫幅（Nitro 專屬）" if banner_url else "未設置橫幅", inline=True)

        embeds = [embed]
        if not user.bot:
            work_embed = discord.Embed(
                title="💼 幽幽子觀察到的命運軌跡",
                color=discord.Color.from_rgb(255, 182, 193)
            )
            work_embed.add_field(
                name="命運狀態",
                value=(f"💼 職業: {job}\n⏳ 冷卻之時: {work_cooldown}\n📊 靈魂壓力 (MP): {mp}/200"),
                inline=False
            )
            embeds.append(work_embed)

        yuyuko_quotes = [
            "靈魂的軌跡真是美麗啊…有沒有好吃的供品呢？",
            "生與死不過一線之隔，珍惜當下吧～",
            "這靈魂的顏色…嗯，適合配一朵櫻花！",
            "幽幽子：願你的靈魂在冥界櫻花下閃耀～"
        ]
        embed.set_footer(text=random.choice(yuyuko_quotes))

        class UserInfoView(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=180)
                self.author_id = ctx.author.id

            async def interaction_check(self, interaction: discord.Interaction) -> bool:
                if interaction.user.bot:
                    return False
                if interaction.user.id != self.author_id:
                    await interaction.response.send_message("幽幽子：這不是你的靈魂資訊哦～只有你才能窺探自己的命運！", ephemeral=True)
                    return False
                return True

            async def on_timeout(self):
                for item in self.children:
                    item.disabled = True
                try:
                    await ctx.edit(embeds=embeds, view=self)
                except Exception:
                    pass

            @discord.ui.button(label="獲取頭像", style=discord.ButtonStyle.primary, emoji="🖼️")
            async def avatar_button(self, button: discord.ui.Button, interaction: discord.Interaction):
                yuyuko_comments = [
                    f"這就是 {user.name} 的靈魂之影～很美吧？",
                    f"嘻嘻，{user.name} 的頭像被幽幽子抓到啦！",
                    f"這是 {user.name} 的模樣，生與死的交界處真是迷人呢～",
                    f"{user.name} 的靈魂之影，配上櫻花一定很美味！"
                ]
                await interaction.response.send_message(
                    f"{avatar_url}\n\n{random.choice(yuyuko_comments)}",
                    ephemeral=True
                )

            @discord.ui.button(label="獲取橫幅", style=discord.ButtonStyle.primary, emoji="🎨", disabled=not bool(banner_url))
            async def banner_button(self, button: discord.ui.Button, interaction: discord.Interaction):
                if banner_url:
                    yuyuko_comments = [
                        f"這是 {user.name} 的靈魂橫幅，華麗得像彼岸花！",
                        f"嘻嘻，{user.name} 的橫幅被幽幽子發現啦～",
                        f"這橫幅承載了 {user.name} 的靈魂色彩，真是耀眼！",
                        f"幽幽子：{user.name} 的橫幅很適合做冥界的裝飾呢～"
                    ]
                    await interaction.response.send_message(
                        f"{banner_url}\n\n{random.choice(yuyuko_comments)}",
                        ephemeral=True
                    )
                else:
                    await interaction.response.send_message(
                        f"{user.name} 尚未設置個人橫幅哦～幽幽子等你來裝飾冥界！",
                        ephemeral=True
                    )

        view = UserInfoView()
        await ctx.respond(embeds=embeds, view=view)

def setup(bot: discord.Bot):
    bot.add_cog(UserInfo(bot))