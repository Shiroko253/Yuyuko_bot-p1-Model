import discord
from discord.ext import commands
from discord.ui import View, Button
import random
import logging

logger = logging.getLogger("SakuraBot.ServerInfo")


class ServerInfo(commands.Cog):
    """
    🌸 幽幽子的群組靈魂窺探 🌸
    探索伺服器的靈魂資訊,如同在冥界賞櫻般優雅
    """
    
    def __init__(self, bot):
        self.bot = bot
        logger.info("🌸 群組資訊指令已甦醒")
        
        # 幽幽子的詩意評論
        self.yuyuko_quotes = [
            "這片土地的靈魂真熱鬧…有沒有好吃的供品呀？",
            "冥界的櫻花最美，群組的靈魂也很閃耀呢～",
            "生與死的交界處，聚會最適合吃點甜點！",
            "亡魂的聚集地…要不要一起賞花、吃點心？",
            "命運的流轉，就像櫻花隨風飄落般美麗…",
            "靈魂的聚會，幽幽子最喜歡了～",
            "這裡的氛圍真不錯，適合舉辦宴會呢！"
        ]
        
        self.icon_comments = [
            "這就是群組靈魂的外貌～有點可愛吧？",
            "嘻嘻，我偷窺到了「{guild_name}」的冥界圖像！",
            "生死交界的標誌，幽幽子覺得很美味…咦？好像說錯了！",
            "這個圖示散發著靈魂的光輝呢～",
            "冥界主人認可這個美麗的標誌！"
        ]

    @discord.slash_command(
        name="server_info",
        description="窺探伺服器的靈魂資訊～幽幽子為你揭開冥界的秘密"
    )
    async def server_info(self, ctx: discord.ApplicationContext):
        """幽幽子窺探伺服器的靈魂流動"""
        
        # === 伺服器檢查 ===
        if ctx.guild is None:
            await ctx.respond(
                embed=self._create_error_embed(
                    "無法窺探靈魂",
                    "哎呀～這個地方沒有靈魂聚集，幽幽子什麼都看不到呢！\n請到伺服器中使用這個指令吧～"
                ),
                ephemeral=True
            )
            logger.info(f"❌ {ctx.user.name} 在非伺服器環境使用 server_info")
            return

        guild = ctx.guild
        
        # === 收集伺服器資訊 ===
        guild_name = guild.name
        guild_id = guild.id
        member_count = guild.member_count
        owner = guild.owner
        owner_display = f"{owner.mention} (`{owner}`)" if owner else "未知的靈魂主人"
        
        # 計算機器人數量
        if hasattr(guild, "members") and guild.members:
            bot_count = sum(1 for member in guild.members if member.bot)
            human_count = member_count - bot_count
        else:
            bot_count = "未知"
            human_count = "未知"
        
        role_count = len(guild.roles)
        emoji_count = len(guild.emojis)
        text_channels = len(guild.text_channels)
        voice_channels = len(guild.voice_channels)
        
        # 加成狀態
        boost_level = guild.premium_tier
        boost_count = guild.premium_subscription_count or 0
        boost_status = f"等級 {boost_level} ({boost_count} 次加成)" if boost_level > 0 else "無加成"
        
        # 創建時間
        created_timestamp = int(guild.created_at.timestamp())
        created_at = f"<t:{created_timestamp}:F> (<t:{created_timestamp}:R>)"
        
        # 伺服器圖示
        guild_icon_url = guild.icon.url if guild.icon else None
        
        # === 創建資訊 Embed ===
        embed = discord.Embed(
            title="🌸 幽幽子窺探的群組靈魂 🌸",
            description=(
                f"─── 西行寺幽幽子の冥界情報 ───\n\n"
                f"櫻花飄落的季節，幽幽子窺探著伺服器 **{guild_name}** 的靈魂流動…\n"
                "亡魂們的聚會會有什麼美味佳餚嗎？\n"
                "請感受冥界主人的溫柔注視吧～"
            ),
            color=discord.Color.from_rgb(205, 133, 232),  # 紫櫻色
            timestamp=discord.utils.utcnow()
        )

        # === 添加資訊欄位 ===
        embed.add_field(
            name="🌸 伺服器名稱",
            value=f"`{guild_name}`",
            inline=False
        )
        
        embed.add_field(
            name="👑 靈魂之主",
            value=owner_display,
            inline=True
        )
        
        embed.add_field(
            name="🆔 伺服器 ID",
            value=f"`{guild_id}`",
            inline=True
        )
        
        embed.add_field(
            name="👻 靈魂數量",
            value=f"總計: **{member_count}**\n人類: {human_count} | 機械: {bot_count}",
            inline=True
        )
        
        embed.add_field(
            name="📺 頻道數量",
            value=f"文字: **{text_channels}**\n語音: **{voice_channels}**",
            inline=True
        )
        
        embed.add_field(
            name="🎭 身份數量",
            value=f"**{role_count}** 個身份",
            inline=True
        )
        
        embed.add_field(
            name="😆 表情數量",
            value=f"**{emoji_count}** 個表情",
            inline=True
        )
        
        embed.add_field(
            name="✨ 加成狀態",
            value=boost_status,
            inline=True
        )
        
        embed.add_field(
            name="⏳ 創建時間",
            value=created_at,
            inline=False
        )

        # 設定縮圖
        if guild_icon_url:
            embed.set_thumbnail(url=guild_icon_url)

        embed.set_footer(text=random.choice(self.yuyuko_quotes))

        # === 創建互動按鈕 ===
        view = ServerIconView(guild, self.icon_comments, timeout=180)

        await ctx.respond(embed=embed, view=view, ephemeral=False)
        logger.info(f"✅ {ctx.user.name} 查看了伺服器 {guild_name} 的資訊")

    @staticmethod
    def _create_error_embed(title: str, description: str) -> discord.Embed:
        """創建錯誤提示 Embed"""
        return discord.Embed(
            title=f"🌸 {title}",
            description=description,
            color=discord.Color.red(),
            timestamp=discord.utils.utcnow()
        )


class ServerIconView(View):
    """伺服器圖示查看視圖"""
    
    def __init__(self, guild: discord.Guild, comments: list, timeout: int = 180):
        super().__init__(timeout=timeout)
        self.guild = guild
        self.comments = comments
        
    @discord.ui.button(
        label="窺探伺服器圖示",
        style=discord.ButtonStyle.primary,
        emoji="👻"
    )
    async def show_icon(self, button: Button, interaction: discord.Interaction):
        """顯示伺服器圖示"""
        try:
            guild_icon_url = self.guild.icon.url if self.guild.icon else None
            guild_name = self.guild.name

            if guild_icon_url:
                comment = random.choice(self.comments).format(guild_name=guild_name)
                
                embed = discord.Embed(
                    title="🌸 伺服器靈魂之影",
                    description=f"**{guild_name}** 的冥界圖像\n\n{comment}",
                    color=discord.Color.from_rgb(205, 133, 232),
                    timestamp=discord.utils.utcnow()
                )
                embed.set_image(url=guild_icon_url)
                embed.set_footer(text="幽幽子的窺探時刻")
                
                await interaction.response.send_message(
                    embed=embed,
                    ephemeral=True
                )
                logger.info(f"👻 {interaction.user.name} 查看了伺服器圖示")
            else:
                await interaction.response.send_message(
                    embed=discord.Embed(
                        title="🌸 無法窺探",
                        description="哎呀～這個伺服器沒有靈魂之影呢，下次再偷窺吧！",
                        color=discord.Color.orange(),
                        timestamp=discord.utils.utcnow()
                    ),
                    ephemeral=True
                )
                logger.info(f"⚠️ {interaction.user.name} 嘗試查看不存在的伺服器圖示")
                
        except Exception as e:
            logger.error(f"❌ 伺服器圖示按鈕錯誤: {e}")
            await interaction.response.send_message(
                "幽幽子迷路了…冥界的路太複雜，下次再來吧！",
                ephemeral=True
            )


def setup(bot):
    bot.add_cog(ServerInfo(bot))
    logger.info("✨ 群組資訊 Cog 已載入完成")
