import discord
from discord.ext import commands
import logging
import random
import asyncio
import time
from datetime import datetime, timezone, timedelta
import os
import json
import sqlite3
import openai
from config.responses import (
    food_responses, death_responses, life_death_responses, self_responses,
    friend_responses, maid_responses, mistress_responses, reimu_responses
)

API_URL = 'https://api.chatanywhere.org/v1/'
AUTHOR_ID = int(os.getenv("AUTHOR_ID", 0))

class OnMessage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        if not hasattr(self.bot, "black_hole_users"):
            self.bot.black_hole_users = set()
        self.api_keys = [
            {"key": os.getenv('CHATANYWHERE_API'), "limit": 200, "remaining": 200},
            {"key": os.getenv('CHATANYWHERE_API2'), "limit": 200, "remaining": 200}
        ]
        self.current_api_index = 0

    @staticmethod
    def record_message(user_id, message):
        if not user_id or not message or not isinstance(message, str):
            return
        try:
            now_utc = datetime.now(timezone.utc).isoformat()
            with sqlite3.connect("config/example.db") as conn:
                c = conn.cursor()
                c.execute("""
                    SELECT id, repeat_count, is_permanent FROM UserMessages 
                    WHERE user_id = ? AND message = ? AND is_permanent = FALSE
                """, (user_id, message))
                row = c.fetchone()
                if row:
                    new_count = row[1] + 1
                    if new_count >= 10:
                        c.execute("""
                            UPDATE UserMessages SET repeat_count = ?, is_permanent = TRUE 
                            WHERE id = ?
                        """, (new_count, row[0]))
                    else:
                        c.execute("""
                            UPDATE UserMessages SET repeat_count = ? WHERE id = ?
                        """, (new_count, row[0]))
                else:
                    c.execute("""
                        INSERT INTO UserMessages (user_id, message, created_at) 
                        VALUES (?, ?, ?)
                    """, (user_id, message, now_utc))
                conn.commit()
        except sqlite3.Error as e:
            logging.error(f"Database error: {e}")

    @staticmethod
    def clean_old_messages(minutes=30):
        try:
            with sqlite3.connect("config/example.db") as conn:
                c = conn.cursor()
                time_ago = (datetime.now(timezone.utc) - timedelta(minutes=minutes)).isoformat()
                c.execute("""
                    DELETE FROM UserMessages 
                    WHERE created_at < ? AND is_permanent = FALSE
                """, (time_ago,))
                deleted_rows = c.rowcount
                conn.commit()
                logging.info(f"已刪除 {deleted_rows} 條舊訊息")
                return deleted_rows
        except sqlite3.Error as e:
            logging.error(f"資料庫錯誤: {e}")
            return 0

    @staticmethod
    def summarize_context(context):
        return context[:1500]

    @staticmethod
    def get_user_background_info(user_id):
        conn = sqlite3.connect("config/example.db")
        c = conn.cursor()
        c.execute("""
            SELECT info FROM BackgroundInfo WHERE user_id = ?
        """, (user_id,))
        rows = c.fetchall()
        conn.close()
        return "\n".join([row[0] for row in rows]) if rows else None

    def generate_response(self, prompt, user_id):
        tried_all_apis = False
        original_index = self.current_api_index

        while True:
            try:
                if self.api_keys[self.current_api_index]["remaining"] <= 0:
                    logging.warning(f"API {self.current_api_index} 已用盡")
                    self.current_api_index = (self.current_api_index + 1) % len(self.api_keys)
                    if self.current_api_index == original_index:
                        tried_all_apis = True
                    if tried_all_apis:
                        return "幽幽子今天吃太飽，先午睡一下吧～"

                openai.api_base = API_URL
                openai.api_key = self.api_keys[self.current_api_index]["key"]

                conn = sqlite3.connect("config/example.db")
                c = conn.cursor()
                c.execute("""
                    SELECT message FROM UserMessages 
                    WHERE user_id = ? OR user_id = 'system'
                """, (user_id,))
                context = "\n".join([f"{user_id}說 {row[0]}" for row in c.fetchall()])
                conn.close()

                user_background_info = self.get_user_background_info("西行寺 幽幽子")
                if not user_background_info:
                    updated_background_info = (
                        "我是西行寺幽幽子，白玉樓的主人，幽靈公主。"
                        "生前因擁有『操縱死亡的能力』，最終選擇自盡，被埋葬於西行妖之下，化為幽靈。"
                        "現在，我悠閒地管理著冥界，欣賞四季變換，品味美食，偶爾捉弄妖夢。"
                        "雖然我的話語總是輕飄飄的，但生與死的流轉，皆在我的掌握之中。"
                        "啊，還有，請不要吝嗇帶點好吃的來呢～"
                    )
                    conn = sqlite3.connect("config/example.db")
                    c = conn.cursor()
                    c.execute("""
                        INSERT INTO BackgroundInfo (user_id, info) VALUES (?, ?)
                    """, ("西行寺 幽幽子", updated_background_info))
                    conn.commit()
                    conn.close()
                else:
                    updated_background_info = user_background_info

                if len(context.split()) > 3000:
                    context = self.summarize_context(context)

                messages = [
                    {"role": "system", "content": f"你現在是西行寺幽幽子，冥界的幽靈公主，背景資訊：{updated_background_info}"},
                    {"role": "user", "content": f"{user_id}說 {prompt}"},
                    {"role": "assistant", "content": f"已知背景資訊：\n{context}"}
                ]

                response = openai.ChatCompletion.create(
                    model="gpt-4o-mini",
                    messages=messages
                )
                self.api_keys[self.current_api_index]["remaining"] -= 1
                return response['choices'][0]['message']['content'].strip()
            except Exception as e:
                logging.error(f"API {self.current_api_index} 發生錯誤: {str(e)}")
                self.current_api_index = (self.current_api_index + 1) % len(self.api_keys)
                if self.current_api_index == original_index:
                    return "幽幽子現在有點懶洋洋的呢～等會兒再來吧♪"

    def load_json(self, file, default={}):
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
        try:
            os.makedirs(os.path.dirname(file), exist_ok=True)
            with open(file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            logging.error(f"Failed to save JSON file {file}: {e}")

    def get_random_response(self, response_list):
        return random.choice(response_list.get("responses", ["幽幽子有點迷糊，沒找到合適的回應～"]))

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        self.bot.last_activity_time = time.time()
        if message.author == self.bot.user or message.webhook_id:
            return

        content = message.content.lower()
        channel = message.channel
        
        is_reply_to_bot = message.reference and message.reference.message_id
        is_mentioning_bot = self.bot.user.mention in message.content
        
        if is_reply_to_bot:
            try:
                referenced_message = await message.channel.fetch_message(message.reference.message_id)
                if referenced_message.author == self.bot.user:
                    is_reply_to_bot = True
                else:
                    is_reply_to_bot= False
            except discord.NotFound:
                is_reply_to_bot = False
                
        if is_reply_to_bot or is_mentioning_bot:
            user_message = message.content
            user_id = str(message.author.id)
            self.record_message(user_id, user_message)
            self.clean_old_messages()
            response = self.generate_response(user_message, user_id)
            await message.channel.send(response)

        # --- 彩蛋/關鍵詞自動回復 ---
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
                await channel.send(f'幽幽子目前已待機了 **{idle_hours:.2f} 小時**')
            else:
                await channel.send(f'幽幽子目前已待機了 **{idle_minutes:.2f} 分鐘**')

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
            await channel.send("螺旋階段、甲虫、廃墟の街、果物のタルト、ドロテアの道、、特異点、ジョット、天使、紫陽花、秘密の皇帝…")
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
                    await message.reply("下午好呀 今天似乎沒有什麼事情可以做呢")
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
            self.bot.black_hole_users.add(message.author.id)
            await channel.send("見過星辰粉碎的樣子嗎")
        elif '釋放' in content:
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
        elif '再見 納維萊特' in content:
            await channel.send("https://tenor.com/view/furina-focalors-genshin-genshin-impact-dance-gif-13263528549516779829")
            

def setup(bot):
    bot.add_cog(OnMessage(bot))