import discord
from discord.ext import commands
from datetime import timezone
from zoneinfo import ZoneInfo
import random
import logging

logger = logging.getLogger("SakuraBot.UserInfo")


class UserInfo(commands.Cog):
    """
    🌸 幽幽子的靈魂窺探術 🌸
    窺探用戶的靈魂資訊,揭示命運的軌跡～
    """
    
    def __init__(self, bot: discord.Bot):
        self.bot = bot
        self.tz = ZoneInfo('Asia/Taipei')
        logger.info("🌸 靈魂窺探術已於櫻花樹下甦醒")

    @discord.slash_command(
        name="user_info",
        description="🌸 幽幽子為你窺探用戶的靈魂資訊～"
    )
    async def user_info(
        self,
        ctx: discord.ApplicationContext,
        user: discord.Member = discord.Option(
            discord.Member,
            name="用戶",
            description="要查詢的用戶(留空則查詢自己)",
            required=False,
            default=None
        )
    ):
        """
        查詢用戶的詳細資訊
        
        包含:
        - 基本資訊 (ID、創建日期等)
        - 伺服器資訊 (加入日期、角色等)
        - 工作狀態 (職業、冷卻時間等)
        - 頭像和橫幅
        """
        try:
            await ctx.defer()
            
            user = user or ctx.author
            guild_id = str(ctx.guild.id) if ctx.guild else "DM"
            user_id = str(user.id)

            # ----------- 載入用戶數據 -----------
            data_manager = getattr(self.bot, "data_manager", None)
            if data_manager:
                try:
                    user_data = data_manager._load_yaml("config/config_user.yml", {})
                except Exception:
                    user_data = {}
            else:
                user_data = {}

            # ----------- 獲取工作信息 -----------
            if not user.bot:
                guild_config = user_data.get(guild_id, {})
                user_config = guild_config.get(user_id, {})
                work_cooldown = user_config.get('work_cooldown', '未工作')
                job = user_config.get('job', '無職業')
                mp = user_config.get('MP', 0)
            else:
                work_cooldown, job, mp = 'N/A', 'N/A', 0

            # ----------- 獲取橫幅 -----------
            banner_url = None
            if not user.bot:
                try:
                    fetched_user = await self.bot.fetch_user(user.id)
                    if fetched_user.banner:
                        banner_url = fetched_user.banner.url
                except Exception:
                    banner_url = None

            # ----------- 頭像類型 -----------
            avatar_type = "伺服器專屬頭像" if isinstance(user, discord.Member) and user.guild_avatar else "全局頭像"
            avatar_url = user.guild_avatar.url if isinstance(user, discord.Member) and user.guild_avatar else user.display_avatar.url

            # ----------- 主要資訊 Embed -----------
            embed = discord.Embed(
                title="🌸 幽幽子窺探的靈魂資訊 🌸",
                description=(
                    f"我是西行寺幽幽子,亡魂之主～\n"
                    f"現在為你揭示 {user.mention} 的靈魂!\n"
                    "亡魂的命運在櫻花下閃耀,讓我們來看看這位旅人的故事吧…"
                ),
                color=discord.Color.from_rgb(255, 182, 193),
                timestamp=discord.utils.utcnow()
            )
            embed.set_thumbnail(url=avatar_url)

            # ----------- 基本資訊 -----------
            embed.add_field(
                name="👤 基本資訊",
                value=(
                    f"```yaml\n"
                    f"名稱: {user.name}#{user.discriminator}\n"
                    f"ID: {user.id}\n"
                    f"是否為機器人: {'是' if user.bot else '否'}\n"
                    f"```"
                ),
                inline=False
            )

            # ----------- 時間資訊 -----------
            created_at = user.created_at.replace(tzinfo=timezone.utc).astimezone(self.tz)
            time_value = f"```yaml\n創建時間: {created_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
            
            if isinstance(user, discord.Member) and user.joined_at:
                joined_at = user.joined_at.replace(tzinfo=timezone.utc).astimezone(self.tz)
                time_value += f"加入時間: {joined_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
            
            time_value += "```"
            embed.add_field(name="⏰ 時間軌跡", value=time_value, inline=False)

            # ----------- 伺服器資訊 -----------
            if isinstance(user, discord.Member):
                server_info = f"```yaml\n"
                server_info += f"暱稱: {user.nick or '無'}\n"
                server_info += f"最高角色: {user.top_role.name}\n"
                server_info += f"角色數量: {len(user.roles) - 1}\n"  # -1 排除 @everyone
                server_info += f"```"
                embed.add_field(name="🏰 伺服器資訊", value=server_info, inline=False)

            # ----------- 頭像和橫幅 -----------
            visual_info = f"```yaml\n"
            visual_info += f"頭像類型: {avatar_type}\n"
            visual_info += f"個人橫幅: {'已設置 (Nitro)' if banner_url else '未設置'}\n"
            visual_info += f"```"
            embed.add_field(name="🎨 視覺資訊", value=visual_info, inline=False)

            # ----------- 幽幽子的評語 -----------
            yuyuko_quotes = [
                "靈魂的軌跡真是美麗啊…有沒有好吃的供品呢?",
                "生與死不過一線之隔,珍惜當下吧～",
                "這靈魂的顏色…嗯,適合配一朵櫻花!",
                "願你的靈魂在冥界櫻花下閃耀～"
            ]
            embed.set_footer(
                text=random.choice(yuyuko_quotes) + " · 幽幽子",
                icon_url=self.bot.user.avatar.url if self.bot.user.avatar else None
            )

            # ----------- 工作狀態 Embed (非機器人) -----------
            embeds = [embed]
            if not user.bot:
                work_embed = discord.Embed(
                    title="💼 幽幽子觀察到的命運軌跡",
                    color=discord.Color.from_rgb(255, 182, 193)
                )
                
                # MP 狀態條
                mp_percentage = (mp / 200) * 100
                mp_bar_length = 10
                filled = int(mp_bar_length * (mp / 200))
                mp_bar = "█" * filled + "░" * (mp_bar_length - filled)
                
                work_embed.add_field(
                    name="🎭 命運狀態",
                    value=(
                        f"```yaml\n"
                        f"職業: {job}\n"
                        f"冷卻狀態: {work_cooldown}\n"
                        f"靈魂壓力 (MP): {mp}/200 ({mp_percentage:.1f}%)\n"
                        f"```"
                        f"{mp_bar} `{mp}/200`"
                    ),
                    inline=False
                )
                
                work_embed.set_footer(
                    text="工作狀態由幽幽子持續觀察 · 幽幽子",
                    icon_url=self.bot.user.avatar.url if self.bot.user.avatar else None
                )
                embeds.append(work_embed)

            # ----------- 創建按鈕 (網頁跳轉) -----------
            view = discord.ui.View(timeout=None)  # ✅ 不會超時!
            
            # 頭像按鈕 (直接跳轉)
            avatar_button = discord.ui.Button(
                label="查看頭像",
                style=discord.ButtonStyle.link,
                emoji="🖼️",
                url=avatar_url
            )
            view.add_item(avatar_button)
            
            # 橫幅按鈕 (如果有的話)
            if banner_url:
                banner_button = discord.ui.Button(
                    label="查看橫幅",
                    style=discord.ButtonStyle.link,
                    emoji="🎨",
                    url=banner_url
                )
                view.add_item(banner_button)
            
            # 個人資料按鈕 (Discord 個人資料頁面)
            profile_button = discord.ui.Button(
                label="Discord 個人資料",
                style=discord.ButtonStyle.link,
                emoji="👤",
                url=f"discord://-/users/{user.id}"  # Discord 內部連結
            )
            view.add_item(profile_button)

            await ctx.followup.send(embeds=embeds, view=view)
            logger.info(f"👤 {ctx.author.name} 查詢了 {user.name} 的資訊")

        except Exception as e:
            logger.exception(f"❌ 用戶資訊查詢失敗: {e}")
            error_embed = discord.Embed(
                title="❌ 靈魂窺探失敗",
                description=(
                    "哎呀,幽幽子在窺探靈魂時遇到了障礙...\n"
                    "請稍後再試或使用 `/feedback` 回報給幽幽子的主人～"
                ),
                color=discord.Color.dark_red()
            )
            error_embed.set_footer(text="靈魂太神秘了 · 幽幽子")
            
            try:
                if not ctx.interaction.response.is_done():
                    await ctx.respond(embed=error_embed, ephemeral=True)
                else:
                    await ctx.followup.send(embed=error_embed, ephemeral=True)
            except Exception:
                logger.exception("❌ 無法發送錯誤訊息")


def setup(bot: discord.Bot):
    """將靈魂窺探術註冊於幽幽子的靈魂"""
    bot.add_cog(UserInfo(bot))
    logger.info("🌸 用戶資訊模組已於櫻花樹下綻放完成")
