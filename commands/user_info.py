import discord
from discord.ext import commands
from datetime import timedelta
import random
import logging

logger = logging.getLogger("SakuraBot.UserInfo")


class UserInfo(commands.Cog):
    """
    🌸 幽幽子的靈魂窺探術 🌸
    窺探用戶的靈魂資訊，揭示命運的軌跡～
    """

    def __init__(self, bot: discord.Bot):
        self.bot = bot
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
            description="要查詢的用戶（留空則查詢自己）",
            required=False,
            default=None
        )
    ):
        try:
            await ctx.defer()

            user = user or ctx.author
            guild_id = str(ctx.guild.id) if ctx.guild else "DM"
            user_id = str(user.id)

            # 直接讀取記憶體中的 user_config
            data_manager = getattr(self.bot, "data_manager", None)
            user_config_data = data_manager.user_config if data_manager else {}

            if not user.bot:
                user_info_dict = user_config_data.get(guild_id, {}).get(user_id, {})
                work_cooldown = user_info_dict.get("work_cooldown", "未工作")
                job = user_info_dict.get("job", "無職業")
                
                # 向下相容 Stamina (體力值) 系統
                stamina = user_info_dict.get("stamina", user_info_dict.get("MP", 0))
                max_stamina = user_info_dict.get("max_stamina", 200)
            else:
                work_cooldown, job, stamina, max_stamina = "N/A", "N/A", 0, 200

            # 獲取橫幅 (Banner)
            banner_url = None
            if not user.bot:
                try:
                    fetched_user = await self.bot.fetch_user(user.id)
                    if fetched_user.banner:
                        banner_url = fetched_user.banner.url
                except Exception:
                    pass

            avatar_type = (
                "伺服器專屬頭像"
                if isinstance(user, discord.Member) and user.guild_avatar
                else "全局頭像"
            )
            avatar_url = (
                user.guild_avatar.url
                if isinstance(user, discord.Member) and user.guild_avatar
                else user.display_avatar.url
            )

            # [附加要求] 檢查是否為 4 週內創立的近期新帳號
            account_age = discord.utils.utcnow() - user.created_at
            is_new_account = account_age < timedelta(weeks=4)
            
            # 移除過時的 #discriminator，改用 global_name
            display_name = user.global_name or user.name

            embed = discord.Embed(
                title="🌸 幽幽子窺探的靈魂資訊 🌸",
                description=(
                    f"我是西行寺幽幽子，亡魂之主～\n"
                    f"現在為你揭示 {user.mention} 的靈魂!\n"
                    "亡魂的命運在櫻花下閃耀，讓我們來看看這位旅人的故事吧…"
                ),
                color=discord.Color.from_rgb(255, 182, 193),
                timestamp=discord.utils.utcnow()
            )
            embed.set_thumbnail(url=avatar_url)

            # 基本資訊 (包含新帳號詳細警告)
            basic_info = (
                f"```yaml\n"
                f"名稱: {display_name} ({user.name})\n"
                f"ID: {user.id}\n"
                f"是否為機器人: {'是' if user.bot else '否'}\n"
                f"```"
            )
            
            # [更新] 擴充新帳號警告內容，列出危險帳號類型
            if is_new_account and not user.bot:
                basic_info += (
                    "\n\n🚨 **高風險警告：近期新帳號 (未滿4週)**\n"
                    "此靈魂剛降臨冥界不久，請管理員加強監管，\n"
                    "確認是否為以下危險帳號：\n"
                    "• `Spam Bot` (垃圾訊息機器人)\n"
                    "• `病毒/木馬帳號`\n"
                    "• `Spam Link Bot` (惡意連結機器人)\n"
                    "• `Spam commands Bot` (濫用指令機器人)"
                )
            
            embed.add_field(name="👤 基本資訊", value=basic_info, inline=False)

            # 使用 Discord 原生時間戳記 <t:...>，自動適配觀看者時區
            time_value = (
                f"```yaml\n"
                f"帳號創建: <t:{int(user.created_at.timestamp())}:F>\n"
                f"加入伺服器: <t:{int(user.joined_at.timestamp())}:F>\n"
                f"```" if user.joined_at else f"```yaml\n帳號創建: <t:{int(user.created_at.timestamp())}:F>\n```"
            )
            embed.add_field(name="⏰ 時間軌跡", value=time_value, inline=False)

            if isinstance(user, discord.Member):
                embed.add_field(
                    name="🏰 伺服器資訊",
                    value=(
                        f"```yaml\n"
                        f"暱稱: {user.nick or '無'}\n"
                        f"最高角色: {user.top_role.name}\n"
                        f"角色數量: {len(user.roles) - 1}\n"
                        f"```"
                    ),
                    inline=False
                )

            embed.add_field(
                name="🎨 視覺資訊",
                value=(
                    f"```yaml\n"
                    f"頭像類型: {avatar_type}\n"
                    f"個人橫幅: {'已設置 (Nitro)' if banner_url else '未設置'}\n"
                    f"```"
                ),
                inline=False
            )

            yuyuko_quotes = [
                "靈魂的軌跡真是美麗啊…有沒有好吃的供品呢?",
                "生與死不過一線之隔，珍惜當下吧～",
                "這靈魂的顏色…嗯，適合配一朵櫻花!",
                "願你的靈魂在冥界櫻花下閃耀～"
            ]
            embed.set_footer(
                text=random.choice(yuyuko_quotes) + " · 幽幽子",
                icon_url=self.bot.user.display_avatar.url
            )

            embeds = [embed]

            # 命運狀態 (職業與體力值)
            if not user.bot:
                work_embed = discord.Embed(
                    title="💼 幽幽子觀察到的命運軌跡",
                    color=discord.Color.from_rgb(255, 182, 193)
                )
                bar_length = 10
                filled = int(bar_length * min(stamina, max_stamina) / max_stamina) if max_stamina > 0 else 0
                bar = "█" * filled + "░" * (bar_length - filled)
                percentage = (stamina / max_stamina) * 100 if max_stamina > 0 else 0

                work_embed.add_field(
                    name="🎭 命運狀態",
                    value=(
                        f"```yaml\n"
                        f"職業: {job}\n"
                        f"冷卻狀態: {work_cooldown}\n"
                        f"體力值: {stamina}/{max_stamina} ({percentage:.1f}%)\n"
                        f"```"
                        f"{bar} `{stamina}/{max_stamina}`"
                    ),
                    inline=False
                )
                work_embed.set_footer(
                    text="工作狀態由幽幽子持續觀察 · 幽幽子",
                    icon_url=self.bot.user.display_avatar.url
                )
                embeds.append(work_embed)

            # Link button View
            view = discord.ui.View(timeout=None)
            view.add_item(discord.ui.Button(label="查看頭像", style=discord.ButtonStyle.link, emoji="🖼️", url=avatar_url))
            
            if banner_url:
                view.add_item(discord.ui.Button(label="查看橫幅", style=discord.ButtonStyle.link, emoji="🎨", url=banner_url))

            view.add_item(discord.ui.Button(
                label="Discord 個人資料",
                style=discord.ButtonStyle.link,
                emoji="👤",
                url=f"discord://-/users/{user.id}"
            ))

            await ctx.followup.send(embeds=embeds, view=view)
            logger.info(f"👤 {ctx.author.name} 查詢了 {user.name} 的資訊")

        except Exception as e:
            logger.exception(f"❌ 用戶資訊查詢失敗: {e}")
            error_embed = discord.Embed(
                title="❌ 靈魂窺探失敗",
                description="哎呀，幽幽子在窺探靈魂時遇到了障礙...\n請稍後再試或使用 `/feedback` 回報～",
                color=discord.Color.dark_red()
            ).set_footer(text="靈魂太神秘了 · 幽幽子")
            try:
                if not ctx.response.is_done():
                    await ctx.respond(embed=error_embed, ephemeral=True)
                else:
                    await ctx.followup.send(embed=error_embed, ephemeral=True)
            except Exception:
                logger.exception("❌ 無法發送錯誤訊息")


def setup(bot: discord.Bot):
    bot.add_cog(UserInfo(bot))
    logger.info("🌸 用戶資訊模組已於櫻花樹下綻放完成")
