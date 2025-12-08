import discord
from discord.ext import commands
from discord.ui import View, Select
import random
import logging

class HelpCog(commands.Cog):
    """
    ✿ 幽幽子的白玉樓指令小冊子 ✿
    靈魂在櫻花紛飛的白玉樓中迷失了嗎？幽幽子給妳最溫柔的指引哦～
    """
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @discord.slash_command(name="help", description="幽幽子親自為您講解白玉樓的所有祕密指令～")
    async def help(self, ctx: discord.ApplicationContext):
        await ctx.defer(ephemeral=False)

        # 幽幽子的溫柔評語，隨機抽選一條添加在embed尾部
        yuyuko_comments = [
            "嘻嘻，這些指令幽幽子都很喜歡呢，一起玩吧？",
            "靈魂迷失時，不妨試試這些神秘的指令唷～",
            "櫻花落下的時刻，也是妳學會新指令的時刻呢～",
            "指令的秘密，等妳一層層揭曉喔，幽幽子最樂意陪在身邊～",
            "來吧！和幽幽子一起發現生活的小樂趣～",
            "白玉樓的風鈴為妳響起，也許今天能碰上意想不到的驚喜唷～",
            "指令如幽靈跳舞，快來一起共鳴吧！"
        ]
        footer_comment = random.choice(yuyuko_comments)

        # 各分類指令集美化展示
        embed_dict = {
            "test": discord.Embed(
                title="⚠️ 幽幽子的祕密測試員樂園 ⚠️",
                description=(
                    "這一區是特別為測試員準備的隱藏指令哦～\n"
                    "> `shutdown` - 讓白玉樓暫時闔上大門，幽幽子要休息囉～\n"
                    "> `restart` - 再次點燃靈魂的篝火，重新召喚幽幽子！\n"
                    "> `addmoney` - 為某位靈魂加添些許幽靈幣～\n"
                    "> `removemoney` - 偷偷減少幽靈的財富...唔，也許會被發現哦！\n"
                    "> `tax` - 主人來收稅囉，增添國庫，豐盛櫻花宴會～"
                ),
                color=discord.Color.from_rgb(251, 178, 218)
            ),
            "economy": discord.Embed(
                title="💸 幽幽子的幽靈幣世界 💸",
                description=(
                    "想在白玉樓變得富有嗎？努力和幽幽子一起賺取幽靈幣吧！\n"
                    "> `balance` - 查閱妳的荷包，幽幽子替妳數幽靈幣～\n"
                    "> `choose_job` - 選擇一份靈魂職業，看看何去何從～\n"
                    "> `work` - 用心工作，報酬也許正在悄悄靠近唷～\n"
                    "> `pay` - 分享幽靈幣給朋友，財富和歡樂倍增～\n"
                    "> `reset_job` - 重選人生道路，換個新身分！\n"
                    "> `leaderboard` - 富豪榜在此，誰才是最閃耀明星？\n"
                    "> `shop` - 補充體力，換些神奇的小道具吧～\n"
                    "> `backpack` - 打開背包，看看幽幽子幫妳收集了什麼好東西！"
                ),
                color=discord.Color.from_rgb(251, 178, 218)
            ),
            "admin": discord.Embed(
                title="🔒 幽幽子的管理權杖 🔒",
                description=(
                    "維護白玉樓安寧的責任，就交給管理員與幽幽子了～\n"
                    "> `ban` - 封印搗蛋鬼，白玉樓需要安靜唷～\n"
                    "> `kick` - 請不守秩序的靈魂離開吧，大家才好歡樂～\n"
                    "> `start_giveaway` - 開啟一場歡樂抽獎，白玉樓準備驚喜大放送！\n"
                    "> `timeout` - 讓愛說話的靈魂靜一靜，沉澱一下唷。\n"
                    "> `untimeout` - 時間結束，讓熱鬧聲音再次回來！"
                ),
                color=discord.Color.from_rgb(251, 178, 218)
            ),
            "common": discord.Embed(
                title="🎉 幽幽子的日常小確幸 🎉",
                description=(
                    "生活無聊嗎？和幽幽子常來這裡輕鬆一下吧！\n"
                    "> `time` - 查看伺服器待機時長，悠閒的時光像落櫻一樣長～\n"
                    "> `ping` - 測試連結，幽幽子的邀請總是不會遲到！\n"
                    "> `server_info` - 白玉樓的祕密資料都在這裡，來窺探一下吧～\n"
                    "> `user_info` - 查詢成員資料，妳會被誰吸引注意呢？\n"
                    "> `feedback` - 發現bug快告訴幽幽子，妳的心聲幽幽子都收到！\n"
                    "> `quiz` - 挑戰知識問答，和幽幽子一起變聰明～"
                ),
                color=discord.Color.from_rgb(251, 178, 218)
            ),
            "fishing": discord.Embed(
                title="🎣 幽幽子的釣魚娛樂室 🎣",
                description=(
                    "放鬆下來，到白玉樓的湖邊和幽幽子一起釣魚吧～\n"
                    "> `fish` - 揮動魚竿，也許下一秒妳就有好收穫～\n"
                    "> `fish_back` - 檢查妳的漁獲，曬曬今天的收成～\n"
                    "> `fish_shop` - 買魚具賣漁獲，讓下次釣魚更順利！\n"
                    "> `fish_rates` - 查查看你的釣魚機率，今天會有好運嗎？～"
                ),
                color=discord.Color.from_rgb(251, 178, 218)
            ),
            "gambling": discord.Embed(
                title="🎰 幽幽子的賭場遊戲間 🎰",
                description=(
                    "想試試手氣嗎？用幽靈幣和幽幽子對賭一場吧！\n"
                    "> `blackjack` - 來一場21點決勝，聰明與運氣也能齊飛喲～"
                ),
                color=discord.Color.from_rgb(251, 178, 218)
            ),
        }
        for embed in embed_dict.values():
            embed.set_footer(text=footer_comment)

        # 權限判斷：測試員 or 管理員才顯示密語類選項
        is_admin = ctx.author.guild_permissions.administrator if hasattr(ctx.author, "guild_permissions") else False
        is_tester = getattr(ctx.author, "bot_owner", False) or getattr(ctx.author, "is_tester", False)
        options = [
            discord.SelectOption(label="日常小確幸", description="大家都能用的歡樂指令", value="common", emoji="🎉"),
            discord.SelectOption(label="幽靈幣世界", description="賺錢消費指令都在這裡", value="economy", emoji="💸"),
            discord.SelectOption(label="管理權杖", description="只有管理員能用的命令唷", value="admin", emoji="🔒"),
            discord.SelectOption(label="釣魚娛樂", description="放鬆心情，釣魚好運來", value="fishing", emoji="🎣"),
            discord.SelectOption(label="賭場遊戲", description="挑戰運氣和膽識！", value="gambling", emoji="🎰"),
        ]
        if is_tester or is_admin:
            options.append(discord.SelectOption(label="測試員密語", description="超級隱藏測試指令", value="test", emoji="⚠️"))

        # 選單過期時的小幽默
        yuyuko_timeout_comments = [
            "櫻花雨下完了，選單也飄遠囉～再輸入 `/help` 讓幽幽子繼續指引妳！",
            "靈魂的舞步停下來，小選單先休息一下，再來找幽幽子聊天唷～",
            "時間咻地過去，選單消逝在春風裡…重新使用 `/help` 喚醒我吧～",
            "白玉樓的風鈴安靜下來，幽幽子也準備小憩一下，快再叫醒我唄！",
            "迷路的靈魂也會累，選單要睡個小覺，再試一次 `/help` 歡迎回來唷！"
        ]

        class HelpSelect(discord.ui.Select):
            def __init__(self):
                super().__init__(
                    placeholder="請選擇一個指令分類，幽幽子隨時等妳開口哦～",
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
                # 選單過期會disable掉，下方文字也會溫柔提醒
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
            content="🌸 歡迎來到白玉樓，幽幽子在這裡守候妳的提問唷～快來選一類指令探索吧！",
            embed=embed_dict["common"],
            view=view
        )
        view.message = message

def setup(bot: discord.Bot):
    bot.add_cog(HelpCog(bot))
