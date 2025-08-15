import discord
from discord.ext import commands
import logging
import random
import asyncio
import time
from datetime import datetime
from dotenv import load_dotenv
import os
import json
from config.responses import (
    food_responses,
    death_responses,
    life_death_responses,
    self_responses,
    friend_responses,
    maid_responses,
    mistress_responses,
    reimu_responses
)

# 設定日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

load_dotenv()
AUTHOR_ID = int(os.getenv("AUTHOR_ID", 0))

class OnMessage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def load_json(self, file, default={}):
        """載入 JSON 檔案"""
        try:
            with open(file, "r", encoding="utf-8") as f:
                return json.load(f) or default
        except FileNotFoundError:
            logging.info(f"Creating empty JSON file: {file}")
            os.makedirs(os.path.dirname(file), exist_ok=True)
            with open(file, "w", encoding="utf-8") as f:
                json.dump(default, f, indent=4, ensure_ascii=False)
            return default
        except Exception as e:
            logging.error(f"Failed to load JSON file {file}: {e}")
            return default

    def save_json(self, file, data):
        """儲存 JSON 檔案"""
        try:
            os.makedirs(os.path.dirname(file), exist_ok=True)
            with open(file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            logging.error(f"Failed to save JSON file {file}: {e}")

    def get_random_response(self, response_list):
        """從回應列表中隨機選擇一個"""
        return random.choice(response_list.get("responses", ["幽幽子有點迷糊，沒找到合適的回應～"]))

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author == self.bot.user or message.webhook_id:
            return

        content = message.content.lower()
        channel = message.channel

        # 彩蛋回應
        if '關於機器人幽幽子' in content:
            await channel.send('幽幽子的創建時間是<t:1623245700:D>')
        elif '關於製作者' in content:
            await channel.send('製作者是個很好的人 雖然看上有有點怪怪的')
        elif '幽幽子的生日' in content:
            await channel.send('機器人幽幽子的生日在<t:1623245700:D>')
        elif '幽幽子待機多久了' in content:
            current_time = time.time()
            idle_seconds = current_time - getattr(self.bot, "last_activity_time", current_time)
            idle_minutes = idle_seconds / 60
            idle_hours = idle_seconds / 3600
            idle_days = idle_seconds / 86400
            if idle_days >= 1:
                await channel.send(f'幽幽子目前已待機了 **{idle_days:.2f} 天**')
            elif idle_hours >= 1:
                await channel.send(f'幽幽子目前已待機了 **{idle_hours:.2f} 小时**')
            else:
                await channel.send(f'幽幽子目前已待機了 **{idle_minutes:.2f} 分钟**')

        # 私訊記錄
        if isinstance(message.channel, discord.DMChannel):
            user_id = str(message.author.id)
            dm_messages = self.load_json('config/dm_messages.json')
            if user_id not in dm_messages:
                dm_messages[user_id] = []
            dm_messages[user_id].append({
                'content': message.content,
                'timestamp': message.created_at.isoformat()
            })
            self.save_json('config/dm_messages.json', dm_messages)
            logging.info(f"Message from {message.author}: {message.content}")

        # JOJO 彩蛋
        if 'これが最後の一撃だ！名に恥じぬ、ザ・ワールド、時よ止まれ！' in content:
            await channel.send('ザ・ワールド\nhttps://tenor.com/view/the-world-gif-18508433')
            await asyncio.sleep(1)
            await channel.send('一秒経過だ！')
            await asyncio.sleep(3)
            await channel.send('二秒経過だ、三秒経過だ！')
            await asyncio.sleep(4)
            await channel.send('四秒経過だ！')
            await asyncio.sleep(5)
            await channel.send('五秒経過だ！')
            await asyncio.sleep(6)
            await channel.send('六秒経過だ！')
            await asyncio.sleep(7)
            await channel.send('七秒経過した！')
            await asyncio.sleep(8)
            await channel.send('ジョジョよ、**私のローラー**!\nhttps://tenor.com/view/dio-roada-rolla-da-dio-brando-dio-dio-jojo-dio-part3-gif-16062047')
            await asyncio.sleep(9)
            await channel.send('遅い！逃げられないぞ！\nhttps://tenor.com/view/dio-jojo-gif-13742432')

        # SAO 彩蛋
        if '星爆氣流斬' in content:
            await channel.send('アスナ！クライン！')
            await channel.send('**頼む、十秒だけ持ち堪えてくれ！**')
            await asyncio.sleep(2)
            await channel.send('スイッチ！')
            await asyncio.sleep(10)
            await channel.send('# スターバースト　ストリーム！')
            await asyncio.sleep(5)
            await channel.send('**速く…もっと速く！！**')
            await asyncio.sleep(15)
            await channel.send('終わった…のか？')

        # 其他彩蛋
        if '關於食物' in content:
            await channel.send(self.get_random_response(food_responses))
        elif '對於死亡' in content:
            await channel.send(self.get_random_response(death_responses))
        elif '對於生死' in content:
            await channel.send(self.get_random_response(life_death_responses))
        elif '關於幽幽子' in content:
            await channel.send(self.get_random_response(self_responses))
        elif '幽幽子的朋友' in content:
            await channel.send(self.get_random_response(friend_responses))
        elif '關於紅魔館的女僕' in content:
            await channel.send(self.get_random_response(maid_responses))
        elif '關於紅魔舘的大小姐和二小姐' in content:
            await channel.send(self.get_random_response(mistress_responses))
        elif '關於神社的巫女' in content:
            await channel.send(self.get_random_response(reimu_responses))
        elif '吃蛋糕嗎' in content:
            await channel.send('蛋糕？！ 在哪在哪？')
            await asyncio.sleep(3)
            await channel.send('妖夢 蛋糕在哪裏？')
            await asyncio.sleep(3)
            await channel.send('原來是個夢呀')
        elif '吃三色糰子嗎' in content:
            await channel.send('三色糰子啊，以前妖夢...')
            await asyncio.sleep(3)
            await channel.send('...')
            await asyncio.sleep(3)
            await channel.send('算了 妖夢不在 我就算不吃東西 反正我是餓不死的存在')
            await asyncio.sleep(3)
            await channel.send('... 妖夢...你在哪...我好想你...')
            await asyncio.sleep(3)
            await channel.send('To be continued...\n-# 妖夢機器人即將到來')
        elif '閉嘴蜘蛛俠' in content:
            await channel.send('deadpool:This is Deadpool 2, not Titanic! Stop serenading me, Celine!')
            await asyncio.sleep(3)
            await channel.send('deadpool:You’re singing way too good, can you sing it like crap for me?!')
            await asyncio.sleep(3)
            await channel.send('Celine Dion:Shut up, Spider-Man!')
            await asyncio.sleep(3)
            await channel.send('deadpool:sh*t, I really should have gone with NSYNC!')
        elif '普奇神父' in content:
            try:
                await message.delete()
            except discord.Forbidden:
                await channel.send("⚠️ 無法刪除訊息，請確認我有刪除訊息的權限。")
                return
            except discord.NotFound:
                pass
            await channel.send("引力を信じるか？")
            await asyncio.sleep(3)
            await channel.send("私は最初にキノコを食べた者を尊敬する。毒キノコかもしれないのに。")
            await asyncio.sleep(5)
            await channel.send("DIO…")
            await asyncio.sleep(2)
            await channel.send("私がこの力を完全に使いこなせるようになったら、必ず君を目覚めさせるよ。")
            await asyncio.sleep(5)
            await channel.send("人は…いずれ天国へ至るものだ。")
            await asyncio.sleep(3)
            await channel.send("最後に言うよ…時間が加速し始める。降りてこい、DIO。")
            await asyncio.sleep(1)
            await channel.send("螺旋階段、甲虫、廃墟の街、果物のタルト、ドロテアの道、特異点、ジョット、天使、紫陽花、秘密の皇帝…")
            await asyncio.sleep(2)
            await channel.send("ここまでだ。")
            await channel.send("天国へのカウントダウンが始まる…")
            await asyncio.sleep(2)
            await channel.send("# メイド・イン・ヘブン！！")
        elif '關於停雲' in content:
            await channel.send("停雲小姐呀")
            await asyncio.sleep(3)
            await channel.send("我記的是一位叫yan的開發者製作的一個discord bot 吧~")
            await asyncio.sleep(3)
            await channel.send("汝 是否是想説 “我爲何知道的呢” 呵呵")
            await asyncio.sleep(3)
            await channel.send("那是我的主人告訴我滴喲~ 欸嘿~")
        elif '蘿莉？' in content:
            await channel.send("蘿莉控？")
            await asyncio.sleep(5)
            if message.guild:
                members = [member.id for member in message.guild.members if not member.bot]
                if members:
                    random_user_id = random.choice(members)
                    await channel.send(f"您是說 {random_user_id} 這位用戶嗎")
                else:
                    await channel.send("這個伺服器內沒有普通成員。")
            else:
                await channel.send("這個能力只能在伺服器內使用。")
        elif message.content in ["早安", "午安", "晚安"]:
            current_time = datetime.now().strftime("%H:%M")
            if message.content == "早安":
                if message.author.id == AUTHOR_ID:
                    await message.reply("早安 主人 今日的開發目標順利嗎")
                else:
                    await message.reply("早上好 今天有什麽事情儘早完成喲", mention_author=False)
            elif message.content == "午安":
                if message.author.id == AUTHOR_ID:
                    await message.reply("下午好呀 今天似乎沒有什麽事情可以做呢")
                else:
                    await message.reply("中午好啊 看起來汝似乎無所事事的呢", mention_author=False)
            elif message.content == "晚安":
                if message.author.id == AUTHOR_ID:
                    await message.reply(f"你趕快去睡覺 現在已經是 {current_time} 了 別再熬夜了！")
                else:
                    await message.reply(f"現在的時間是 {current_time} 汝還不就寢嗎？", mention_author=False)
        elif message.content.startswith('關閉機器人'):
            if message.author.id == AUTHOR_ID:
                await channel.send("正在關閉...")
                await asyncio.sleep(5)
                await self.bot.close()
            else:
                await channel.send("你無權關閉我 >_<")
        elif '擬態黑洞' in content:
            try:
                await message.delete()
            except discord.Forbidden:
                await channel.send("⚠️ 無法刪除訊息，請確認我有刪除訊息的權限。")
                return
            except discord.NotFound:
                pass
            if not hasattr(self.bot, "black_hole_users"):
                self.bot.black_hole_users = set()
            self.bot.black_hole_users.add(message.author.id)
            await channel.send("見過星辰粉碎的樣子嗎")
        elif '釋放' in content:
            if not hasattr(self.bot, "black_hole_users"):
                self.bot.black_hole_users = set()
            if message.author.id not in self.bot.black_hole_users:
                await channel.send("終結技能量不足")
                return
            try:
                await message.delete()
            except discord.Forbidden:
                await channel.send("⚠️ 無法刪除訊息，請確認我有刪除訊息的權限。")
                return
            except discord.NotFound:
                pass
            await channel.send("生存還是毀滅")
            await asyncio.sleep(3)
            await channel.send("你別無選擇")
            self.bot.black_hole_users.discard(message.author.id)

def setup(bot):
    bot.add_cog(OnMessage(bot))
