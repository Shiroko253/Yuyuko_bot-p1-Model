import discord
from discord.ext import commands
from discord.ui import View, Select
import random
import logging
import os

logger = logging.getLogger("SakuraBot.Help")

AUTHOR_ID = int(os.getenv("AUTHOR_ID", 0))


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

        embed_dict = {
            "test": discord.Embed(
                title="⚠️ 幽幽子的祕密測試員樂園 ⚠️",
                description=(
                    "這一區是特別為測試員準備的隱藏指令哦～\n"
                    "> `shutdown` - 讓白玉樓暫時闔上大門，幽幽子要休息囉～\n"
                    "> `restart` - 再次點燃靈魂的篝火，重新召喚幽幽子！\n"
                    "> `addmoney` - 為某位靈魂加添些許幽靈幣～\n"
                    "> `removemoney` - 偷偷減少幽靈的財富...唔，也許會被發現哦！"
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
                    "> `untimeout` - 時間結束，讓熱鬧聲音再次回來！\n"
                    "> `tax` - 向靈魂徵稅，增添國庫，豐盛櫻花宴會～"
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
                    "> `blackjack` - 來一場21點決勝，聰明與運氣也能齊飛喲～\n"
                    "> `blackjack_pvp` - 向其他玩家發起21點對決，勝者通吃！"
                ),
                color=discord.Color.from_rgb(251, 178, 218)
            ),
        }
        for embed in embed_dict.values():
            embed.set_footer(text=footer_comment)

        is_admin = (
            ctx.author.guild_permissions.administrator
            if hasattr(ctx.author, "guild_permissions")
            else False
        )
        is_author = (AUTHOR_ID != 0 and ctx.author.id == AUTHOR_ID)

        options = [
            discord.SelectOption(label="日常小確幸", description="大家都能用的歡樂指令", value="common", emoji="🎉"),
            discord.SelectOption(label="幽靈幣世界", description="賺錢消費指令都在這裡", value="economy", emoji="💸"),
            discord.SelectOption(label="管理權杖", description="只有管理員能用的命令唷", value="admin", emoji="🔒"),
            discord.SelectOption(label="釣魚娛樂", description="放鬆心情，釣魚好運來", value="fishing", emoji="🎣"),
            discord.SelectOption(label="賭場遊戲", description="挑戰運氣和膽識！", value="gambling", emoji="🎰"),
        ]
        if is_author or is_admin:
            options.append(
                discord.SelectOption(label="測試員密語", description="超級隱藏測試指令", value="test", emoji="⚠️")
            )

        yuyuko_timeout_comments = [
            "櫻花雨下完了，選單也飄遠囉～再輸入 `/help` 讓幽幽子繼續指引妳！",
            "靈魂的舞步停下來，小選單先休息一下，再來找幽幽子聊天唷～",
            "時間咻地過去，選單消逝在春風裡…重新使用 `/help` 喚醒我吧～",
            "白玉樓的風鈴安靜下來，幽幽子也準備小憩一下，快再叫醒我唄！",
            "迷路的靈魂也會累，選單要睡個小覺，再試一次 `/help` 歡迎回來唷！"
        ]

        # [Debug 修復 #2] 將 HelpSelect 獨立出來，並接收 parent_view 參照
        class HelpSelect(discord.ui.Select):
            def __init__(self, parent_view):
                self.parent_view = parent_view
                super().__init__(
                    placeholder="請選擇一個指令分類，幽幽子隨時等妳開口哦～",
                    options=options
                )

            async def callback(self, interaction: discord.Interaction):
                value = self.values[0]
                
                # [Debug 修復 #2] 創建一個全新的 TimeoutView 來重置 60 秒倒數計時器！
                # 原版只更新 embed，timeout 不會重置，導致使用者看久了選單還是會突然消失。
                new_view = TimeoutView(timeout=60)
                
                await interaction.response.edit_message(
                    embed=embed_dict[value], 
                    view=new_view
                )
                
                # 將當前訊息的參照交給新 View，確保它超時時能正確編輯
                new_view.message = interaction.message

        class TimeoutView(View):
            def __init__(self, timeout=60):
                super().__init__(timeout=timeout)
                self.message = None
                # [Debug 修復 #2] 實例化 HelpSelect 時傳入 self
                self.add_item(HelpSelect(self))

            async def on_timeout(self):
                for child in self.children:
                    if isinstance(child, discord.ui.Select):
                        child.disabled = True
                try:
                    if self.message:
                        await self.message.edit(
                            content=random.choice(yuyuko_timeout_comments),
                            view=self
                        )
                except discord.NotFound:
                    logger.warning("原始訊息未找到，可能已被刪除。")
                except Exception as e:
                    logger.error(f"help on_timeout 失敗: {e}")

        view = TimeoutView()
        
        # [Debug 修復 #1] 徹底修正 Pycord 的 Message 獲取方式！
        # 在 Pycord 中，defer 後的 ctx.respond() 直接回傳 discord.Message 物件。
        # 原版使用 response.original_response() 是 discord.py 的語法，在 Pycord 會拋出 AttributeError 導致崩潰！
        response_message = await ctx.respond(
            content="🌸 歡迎來到白玉樓，幽幽子在這裡守候妳的提問唷～快來選一類指令探索吧！",
            embed=embed_dict["common"],
            view=view
        )
        
        # 直接將回傳的 Message 物件賦給 view.message
        view.message = response_message


def setup(bot: discord.Bot):
    bot.add_cog(HelpCog(bot))
    logger.info("Help Cog 已載入，白玉樓的指引等待著迷路的靈魂～")
