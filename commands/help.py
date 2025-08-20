import discord
from discord.ext import commands
from discord.ui import View, Select
import random
import logging

class HelpCog(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @discord.slash_command(name="help", description="幽幽子為你介紹白玉樓的指令哦～")
    async def help(self, ctx: discord.ApplicationContext):
        await ctx.defer(ephemeral=False)

        yuyuko_comments = [
            "嘻嘻，這些指令很有趣吧？快來試試看～",
            "靈魂的指引就在這裡，選擇你喜歡的吧～",
            "櫻花飄落時，指令的秘密也會顯現哦～",
            "這些指令，都是幽幽子精心準備的呢～",
            "來吧，讓我們一起探索這些指令的樂趣～",
            "白玉樓的風鈴響起，指令的旋律也隨之而來～",
            "靈魂的舞步，與這些指令共鳴吧～"
        ]
        footer_comment = random.choice(yuyuko_comments)

        embed_dict = {
            "test": discord.Embed(
                title="⚠️ 幽幽子的測試員密語 ⚠️",
                description=(
                    "這些是給測試員的特別指令，靈魂的試驗場哦～\n\n"
                    "> `shutdown` - 讓白玉樓的燈火暫時 關閉機器人，讓幽幽子休息一下吧～\n"
                    "> `restart` - 重啟機器人，靈魂需要一點新鮮空氣呢～\n"
                    "> `addmoney` - 為用戶添加幽靈幣，靈魂的財富增加啦！\n"
                    "> `removemoney` - 移除用戶的幽靈幣，哎呀，靈魂的財富減少了呢～\n"
                    "> `tax` = 讓幽幽子的主人幫助國庫增長一些國稅"
                ),
                color=discord.Color.from_rgb(255, 182, 193)
            ),
            "economy": discord.Embed(
                title="💸 幽幽子的幽靈幣經濟 💸",
                description=(
                    "在白玉樓，幽靈幣可是很重要的哦～快來賺取你的財富吧！\n\n"
                    "> `balance` - 讓幽幽子幫你窺探你的幽靈幣餘額～\n"
                    "> `choose_job` - 選擇一份職業，靈魂也需要工作哦～\n"
                    "> `work` - 努力工作，賺取更多的幽靈幣吧！\n"
                    "> `pay` - 轉賬給其他靈魂，分享你的財富吧～\n"
                    "> `reset_job` - 重置你的職業，換個新身份吧～\n"
                    "> `leaderboard` - 查看經濟排行榜，看看誰是白玉樓最富有的靈魂！\n"
                    "> `shop` - 在工作之餘也別忘了補充體力呀~\n"
                    "> `backpack` - 可以看看靈魂的背包裏面有什麽好吃的~"
                ),
                color=discord.Color.from_rgb(255, 182, 193)
            ),
            "admin": discord.Embed(
                title="🔒 幽幽子的管理權杖 🔒",
                description=(
                    "這些是指令是給管理員的，靈魂的秩序由你來維護哦～\n\n"
                    "> `ban` - 封鎖用戶，讓他們離開白玉樓吧！\n"
                    "> `kick` - 踢出用戶，給他們一點小教訓～\n"
                    "> `start_giveaway` - 開啟抽獎，靈魂們都期待著呢！\n"
                    "> `timeout` - 禁言某位成員，讓他們安靜一會兒～\n"
                    "> `untimeout` - 解除禁言，讓靈魂的聲音再次響起吧～"
                ),
                color=discord.Color.from_rgb(255, 182, 193)
            ),
            "common": discord.Embed(
                title="🎉 幽幽子的日常樂趣 🎉",
                description=(
                    "這些是給所有靈魂的日常指令，快來一起玩吧～\n\n"
                    "> `time` - 查看待機時間，靈魂的悠閒時光有多少呢？\n"
                    "> `ping` - 測試與靈界的通訊延遲，靈魂的波動有多快？\n"
                    "> `server_info` - 獲取伺服器資訊，白玉樓的秘密都在這裡～\n"
                    "> `user_info` - 窺探其他靈魂的資訊，嘻嘻～\n"
                    "> `feedback` - 回報錯誤，幫幽幽子改進哦～\n"
                    "> `quiz` - 挑戰問題，靈魂的智慧有多深呢？"
                ),
                color=discord.Color.from_rgb(255, 182, 193)
            ),
            "fishing": discord.Embed(
                title="🎣 幽幽子的悠閒釣魚時光 🎣",
                description=(
                    "在白玉樓的湖邊釣魚，享受悠閒時光吧～\n\n"
                    "> `fish` - 開始釣魚，會釣到什麼魚呢？\n"
                    "> `fish_back` - 打開釣魚背包，看看你的收穫吧～\n"
                    "> `fish_shop` - 販售魚或購買魚具，準備好下次釣魚吧！\n"
                    "> `fish_rod` - 切換漁具，用更好的魚竿釣大魚哦～"
                ),
                color=discord.Color.from_rgb(255, 182, 193)
            ),
            "gambling": discord.Embed(
                title="🎰 幽幽子的賭博遊戲 🎰",
                description=(
                    "用幽靈幣來挑戰運氣吧，靈魂的賭局開始啦～\n\n"
                    "> `blackjack` - 與幽幽子玩一場21點遊戲，賭上你的幽靈幣吧！"
                ),
                color=discord.Color.from_rgb(255, 182, 193)
            ),
        }
        for embed in embed_dict.values():
            embed.set_footer(text=footer_comment)

        # 動態顯示管理員/測試員選項
        is_admin = ctx.author.guild_permissions.administrator
        is_tester = getattr(ctx.author, "bot_owner", False) or getattr(ctx.author, "is_tester", False)
        options = [
            discord.SelectOption(label="日常樂趣", description="查看普通指令", value="common", emoji="🎉"),
            discord.SelectOption(label="幽靈幣經濟", description="查看經濟系統指令", value="economy", emoji="💸"),
            discord.SelectOption(label="管理權杖", description="查看管理員指令", value="admin", emoji="🔒"),
            discord.SelectOption(label="悠閒釣魚", description="查看釣魚相關指令", value="fishing", emoji="🎣"),
            discord.SelectOption(label="賭博遊戲", description="查看賭博指令", value="gambling", emoji="🎰"),
        ]
        if is_tester or is_admin:
            options.append(discord.SelectOption(label="測試員密語", description="查看測試員指令", value="test", emoji="⚠️"))

        yuyuko_timeout_comments = [
            "櫻花已凋謝，選單也休息了哦～請重新輸入 `/help` 吧！",
            "靈魂的舞步停下了，選單也過期啦～再來一次吧！",
            "嘻嘻，時間到了，選單已經飄走了～重新輸入 `/help` 哦！",
            "白玉樓的風鈴停了，選單也休息了呢～再試一次吧～",
            "靈魂的波動消失了，選單也過期啦～請重新輸入 `/help`！"
        ]

        class HelpSelect(discord.ui.Select):
            def __init__(self):
                super().__init__(
                    placeholder="選擇指令分類吧，靈魂的指引在等你～",
                    options=options
                )

            async def callback(self, interaction: discord.Interaction):
                value = self.values[0]
                await interaction.response.edit_message(embed=embed_dict[value])

        class TimeoutView(View):
            def __init__(self, timeout=60):
                super().__init__(timeout=timeout)
                self.message = None
                self.add_item(HelpSelect())

            async def on_timeout(self):
                for child in self.children:
                    if isinstance(child, discord.ui.Select):
                        child.disabled = True
                try:
                    if self.message:
                        embed = self.message.embeds[0]
                        embed.color = discord.Color.dark_grey()
                        await self.message.edit(
                            content=random.choice(yuyuko_timeout_comments),
                            embed=embed,
                            view=self
                        )
                except discord.NotFound:
                    logging.warning("原始訊息未找到，可能已被刪除。")

        view = TimeoutView()
        message = await ctx.respond(
            content="🌸 歡迎來到白玉樓，我是西行寺幽幽子～請選擇指令分類吧！",
            embed=embed_dict["common"],
            view=view
        )
        # 直接設為 message，不要用 original_response()
        view.message = message

def setup(bot: discord.Bot):
    bot.add_cog(HelpCog(bot))
