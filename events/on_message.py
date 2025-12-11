import discord
from discord.ext import commands
import logging
import random
import asyncio
import time
from datetime import datetime, timezone, timedelta
import os
import sqlite3
import openai

logger = logging.getLogger("SakuraBot.events.on_message")

API_URL = 'https://api.chatanywhere.org/v1/'
AUTHOR_ID = int(os.getenv("AUTHOR_ID", 0))


class OnMessage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.api_keys = [
            {"key": os.getenv('CHATANYWHERE_API'), "limit": 200, "remaining": 200},
            {"key": os.getenv('CHATANYWHERE_API2'), "limit": 200, "remaining": 200}
        ]
        self.current_api_index = 0
        
        # 載入彩蛋配置
        self.easter_eggs = self._load_easter_eggs()
        
        # 檢查 API KEY
        for idx, api in enumerate(self.api_keys):
            if not api["key"]:
                logger.error(f"API {idx} 沒有設置金鑰，請設置 CHATANYWHERE_API 或 CHATANYWHERE_API2 環境變數")

    def _load_easter_eggs(self):
        """載入彩蛋配置"""
        return self.bot.data_manager._load_json(
            "config/on_message.json",
            self._get_default_config()
        )
    
    def _get_default_config(self):
        """預設彩蛋配置"""
        return {
            "simple_responses": {
                "關於機器人幽幽子": "幽幽子的創建時間是<t:1623245700:D>",
                "關於製作者": "製作者是個很好的人 雖然看上有有點怪怪的",
                "幽幽子的生日": "機器人幽幽子的生日在<t:1623245700:D>",
                "吃蛋糕嗎": "蛋糕？！ 在哪在哪？",
                "關於停雲": "停雲小姐呀"
            },
            "random_responses": {
                "關於食物": ["responses from config.responses.food_responses"],
                "對於死亡": ["responses from config.responses.death_responses"],
                "對於生死": ["responses from config.responses.life_death_responses"],
                "關於幽幽子": ["responses from config.responses.self_responses"],
                "幽幽子的朋友": ["responses from config.responses.friend_responses"],
                "關於紅魔館的女僕": ["responses from config.responses.maid_responses"],
                "關於紅魔舘的大小姐和二小姐": ["responses from config.responses.mistress_responses"],
                "關於神社的巫女": ["responses from config.responses.reimu_responses"]
            },
            "complex_responses": {
                "吃三色糰子嗎": [
                    {"text": "三色糰子啊，以前妖夢...", "delay": 3},
                    {"text": "...", "delay": 3},
                    {"text": "算了 妖夢不在 我就算不吃東西 反正我是餓不死的存在", "delay": 3},
                    {"text": "... 妖夢...你在哪...我好想你...", "delay": 3},
                    {"text": "To be continued...\n-# 妖夢機器人即將到來", "delay": 0}
                ],
                "閉嘴蜘蛛俠": [
                    {"text": "deadpool:This is Deadpool 2, not Titanic! Stop serenading me, Celine!", "delay": 3},
                    {"text": "deadpool:You're singing way too good, can you sing it like crap for me?!", "delay": 3},
                    {"text": "Celine Dion:Shut up, Spider-Man!", "delay": 3},
                    {"text": "deadpool:sh*t, I really should have gone with NSYNC!", "delay": 0}
                ],
                "星爆氣流斬": [
                    {"text": "アスナ！クライン！", "delay": 0},
                    {"text": "**頼む、十秒だけ持ち堪えてくれ！**", "delay": 2},
                    {"text": "スイッチ！", "delay": 10},
                    {"text": "# スターバースト　ストリーム！", "delay": 5},
                    {"text": "**速く…もっと速く！！**", "delay": 15},
                    {"text": "終わった…のか？", "delay": 0}
                ],
                "再見 納維萊特": [
                    {"text": "https://tenor.com/view/furina-focalors-genshin-genshin-impact-dance-gif-13263528549516779829", "delay": 0}
                ]
            },
            "jojo_time_stop": {
                "trigger": "これが最後の一撃だ！名に恥じぬ、ザ・ワールド、時よ止まれ！",
                "responses": [
                    {"text": "ザ・ワールド\nhttps://tenor.com/view/the-world-gif-18508433", "delay": 1},
                    {"text": "一秒経過だ！", "delay": 3},
                    {"text": "二秒経過だ、三秒経過だ！", "delay": 4},
                    {"text": "四秒経過だ！", "delay": 5},
                    {"text": "五秒経過だ！", "delay": 6},
                    {"text": "六秒経過だ！", "delay": 7},
                    {"text": "七秒経過した！", "delay": 8},
                    {"text": "ジョジョよ、**私のローラー**!\nhttps://tenor.com/view/dio-roada-rolla-da-dio-brando-dio-dio-jojo-dio-part3-gif-16062047", "delay": 9},
                    {"text": "遅い！逃げられないぞ！\nhttps://tenor.com/view/dio-jojo-gif-13742432", "delay": 0}
                ]
            },
            "pucci_heaven": {
                "trigger": "普奇神父",
                "delete_trigger": True,
                "responses": [
                    {"text": "引力を信じるか？", "delay": 3},
                    {"text": "私は最初にキノコを食べた者を尊敬する。毒キノコかもしれないのに。", "delay": 5},
                    {"text": "DIO…", "delay": 2},
                    {"text": "私がこの力を完全に使いこなせるようになったら、必ず君を目覚めさせるよ。", "delay": 5},
                    {"text": "人は…いずれ天国へ至るものだ。", "delay": 3},
                    {"text": "最後に言うよ…時間が加速し始める。降りてこい、DIO。", "delay": 1},
                    {"text": "螺旋階段、甲虫、廃墟の街、果物のタルト、ドロテアの道、、特異点、ジョット、天使、紫陽花、秘密の皇帝…", "delay": 2},
                    {"text": "ここまでだ。", "delay": 0},
                    {"text": "天国へのカウントダウンが始まる…", "delay": 2},
                    {"text": "# メイド・イン・ヘブン！！", "delay": 0}
                ]
            }
        }

    @staticmethod
    def record_message(user_id, message, db_path):
        """記錄用戶訊息到資料庫"""
        if not user_id or not message or not isinstance(message, str):
            return
        try:
            now_utc = datetime.now(timezone.utc).isoformat()
            with sqlite3.connect(db_path) as conn:
                c = conn.cursor()
                c.execute("""
                    SELECT id, repeat_count FROM UserMessages 
                    WHERE user_id = ? AND message = ? AND is_permanent = FALSE
                """, (user_id, message))
                row = c.fetchone()
                
                if row:
                    new_count = row[1] + 1
                    is_permanent = new_count >= 10
                    c.execute("""
                        UPDATE UserMessages 
                        SET repeat_count = ?, is_permanent = ? 
                        WHERE id = ?
                    """, (new_count, is_permanent, row[0]))
                else:
                    c.execute("""
                        INSERT INTO UserMessages (user_id, message, created_at) 
                        VALUES (?, ?, ?)
                    """, (user_id, message, now_utc))
                conn.commit()
        except sqlite3.Error as e:
            logger.error(f"記錄訊息失敗: {e}")

    @staticmethod
    def clean_old_messages(db_path, minutes=30):
        """清理舊訊息"""
        try:
            with sqlite3.connect(db_path) as conn:
                c = conn.cursor()
                time_ago = (datetime.now(timezone.utc) - timedelta(minutes=minutes)).isoformat()
                c.execute("""
                    DELETE FROM UserMessages 
                    WHERE created_at < ? AND is_permanent = FALSE
                """, (time_ago,))
                deleted_rows = c.rowcount
                conn.commit()
                if deleted_rows > 0:
                    logger.info(f"已刪除 {deleted_rows} 條舊訊息")
                return deleted_rows
        except sqlite3.Error as e:
            logger.error(f"清理舊訊息失敗: {e}")
            return 0

    @staticmethod
    def get_user_background_info(user_id, db_path):
        """獲取用戶背景資訊"""
        try:
            with sqlite3.connect(db_path) as conn:
                c = conn.cursor()
                c.execute("SELECT info FROM BackgroundInfo WHERE user_id = ?", (user_id,))
                rows = c.fetchall()
                return "\n".join([row[0] for row in rows]) if rows else None
        except sqlite3.Error as e:
            logger.error(f"獲取背景資訊失敗: {e}")
            return None

    def generate_response(self, prompt, user_id):
        """生成 AI 回應"""
        tried_all_apis = False
        original_index = self.current_api_index
        db_path = self.bot.data_manager.db_path

        while True:
            try:
                api_key = self.api_keys[self.current_api_index]["key"]
                if not api_key:
                    logger.error(f"API {self.current_api_index} 沒有設置金鑰")
                    return "伺服器金鑰未設定，請通知管理員設置環境變數 CHATANYWHERE_API 或 CHATANYWHERE_API2。"

                if self.api_keys[self.current_api_index]["remaining"] <= 0:
                    logger.warning(f"API {self.current_api_index} 已用盡")
                    self.current_api_index = (self.current_api_index + 1) % len(self.api_keys)
                    if self.current_api_index == original_index:
                        tried_all_apis = True
                    if tried_all_apis:
                        return "幽幽子今天吃太飽，先午睡一下吧～"

                openai.api_base = API_URL
                openai.api_key = api_key

                # 獲取對話歷史
                with sqlite3.connect(db_path) as conn:
                    c = conn.cursor()
                    c.execute("""
                        SELECT message FROM UserMessages 
                        WHERE user_id = ? OR user_id = 'system'
                        ORDER BY created_at DESC LIMIT 20
                    """, (user_id,))
                    context = "\n".join([f"{user_id}說: {row[0]}" for row in c.fetchall()])

                # 獲取或創建背景資訊
                user_background_info = self.get_user_background_info("西行寺 幽幽子", db_path)
                if not user_background_info:
                    updated_background_info = (
                        "我是西行寺幽幽子，白玉樓的主人，幽靈公主。"
                        "生前因擁有『操縱死亡的能力』，最終選擇自盡，被埋葬於西行妖之下，化為幽靈。"
                        "現在，我悠閒地管理著冥界，欣賞四季變換，品味美食，偶爾捉弄妖夢。"
                        "雖然我的話語總是輕飄飄的，但生與死的流轉，皆在我的掌握之中。"
                        "啊，還有，請不要吝嗇帶點好吃的來呢～"
                    )
                    with sqlite3.connect(db_path) as conn:
                        c = conn.cursor()
                        c.execute("""
                            INSERT OR REPLACE INTO BackgroundInfo (user_id, info) 
                            VALUES (?, ?)
                        """, ("西行寺 幽幽子", updated_background_info))
                        conn.commit()
                else:
                    updated_background_info = user_background_info

                # 構建訊息
                messages = [
                    {"role": "system", "content": f"你現在是西行寺幽幽子，冥界的幽靈公主，背景資訊：{updated_background_info}"},
                    {"role": "assistant", "content": f"已知對話歷史：\n{context}"},
                    {"role": "user", "content": prompt}
                ]

                # 呼叫 API (修正模型名稱)
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",  # 修正: gpt-5-mini 不存在
                    messages=messages,
                    max_tokens=500,
                    temperature=0.9
                )
                
                self.api_keys[self.current_api_index]["remaining"] -= 1
                return response['choices'][0]['message']['content'].strip()
                
            except Exception as e:
                logger.error(f"API {self.current_api_index} 發生錯誤: {str(e)}")
                self.current_api_index = (self.current_api_index + 1) % len(self.api_keys)
                if self.current_api_index == original_index:
                    return "幽幽子現在有點懶洋洋的呢～等會兒再來吧♪"

    async def handle_complex_response(self, channel, responses):
        """處理複雜回應(多條訊息+延遲)"""
        for response in responses:
            await channel.send(response["text"])
            if response.get("delay", 0) > 0:
                await asyncio.sleep(response["delay"])

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """主要訊息處理器"""
        self.bot.last_activity_time = time.time()
        
        # 忽略自己和 webhook
        if message.author == self.bot.user or message.webhook_id:
            return

        content = message.content
        content_lower = content.lower()
        channel = message.channel
        db_path = self.bot.data_manager.db_path

        # --- AI 對話處理 ---
        is_reply_to_bot = False
        is_mentioning_bot = self.bot.user.mention in content
        
        if message.reference and message.reference.message_id:
            try:
                referenced_message = await channel.fetch_message(message.reference.message_id)
                is_reply_to_bot = referenced_message.author == self.bot.user
            except discord.NotFound:
                pass
                
        if is_reply_to_bot or is_mentioning_bot:
            user_id = str(message.author.id)
            self.record_message(user_id, content, db_path)
            self.clean_old_messages(db_path)
            response = self.generate_response(content, user_id)
            await channel.send(response)
            return  # AI 回應後不再處理其他觸發

        # --- 簡單關鍵字回應 ---
        for keyword, response in self.easter_eggs.get("simple_responses", {}).items():
            if keyword in content_lower:
                await channel.send(response)
                return

        # --- 複雜多步驟回應 ---
        for keyword, responses in self.easter_eggs.get("complex_responses", {}).items():
            if keyword in content:
                await self.handle_complex_response(channel, responses)
                return

        # --- JOJO 時停 ---
        jojo = self.easter_eggs.get("jojo_time_stop", {})
        if jojo.get("trigger") in content:
            await self.handle_complex_response(channel, jojo.get("responses", []))
            return

        # --- 普奇神父 (需刪除訊息) ---
        pucci = self.easter_eggs.get("pucci_heaven", {})
        if pucci.get("trigger") in content:
            if pucci.get("delete_trigger"):
                try:
                    await message.delete()
                except (discord.Forbidden, discord.NotFound):
                    await channel.send("⚠️ 無法刪除訊息，請確認我有刪除訊息的權限。")
            await self.handle_complex_response(channel, pucci.get("responses", []))
            return

        # --- 特殊功能 ---
        if '幽幽子待機多久了' in content_lower:
            await self.handle_idle_time(channel)
            return

        if '蘿莉？' in content:
            await self.handle_lolicon(message)
            return

        if content in ["早安", "午安", "晚安"]:
            await self.handle_greetings(message)
            return

        if content.startswith('關閉機器人'):
            await self.handle_shutdown(message)
            return

        # --- 黑洞系統 ---
        if '擬態黑洞' in content:
            await self.handle_black_hole_activate(message)
            return

        if '釋放' in content:
            await self.handle_black_hole_release(message)
            return

        # --- 私訊記錄 ---
        if isinstance(channel, discord.DMChannel):
            self.record_dm_message(message)

    async def handle_idle_time(self, channel):
        """處理待機時間查詢"""
        current_time = time.time()
        idle_seconds = current_time - getattr(self.bot, "last_activity_time", current_time)
        
        idle_days = idle_seconds / 86400
        idle_hours = idle_seconds / 3600
        idle_minutes = idle_seconds / 60
        
        if idle_days >= 1:
            await channel.send(f'幽幽子目前已待機了 **{idle_days:.2f} 天**')
        elif idle_hours >= 1:
            await channel.send(f'幽幽子目前已待機了 **{idle_hours:.2f} 小時**')
        else:
            await channel.send(f'幽幽子目前已待機了 **{idle_minutes:.2f} 分鐘**')

    async def handle_lolicon(self, message):
        """處理蘿莉控彩蛋"""
        await message.channel.send("蘿莉控？")
        await asyncio.sleep(5)
        
        if message.guild:
            members = [member for member in message.guild.members if not member.bot]
            if members:
                random_member = random.choice(members)
                await message.channel.send(f"您是說 {random_member.mention} 這位用戶嗎")
            else:
                await message.channel.send("這個伺服器內沒有普通成員。")
        else:
            await message.channel.send("這個能力只能在伺服器內使用。")

    async def handle_greetings(self, message):
        """處理早午晚安"""
        # 使用 UTC+8 時區 (馬來西亞 Kuching 時間)
        from zoneinfo import ZoneInfo
        try:
            local_tz = ZoneInfo("Asia/Kuching")  # UTC+8
        except:
            # 如果 zoneinfo 不可用,使用 timedelta
            local_tz = timezone(timedelta(hours=8))
        
        current_time = datetime.now(local_tz).strftime("%H:%M")
        is_author = message.author.id == AUTHOR_ID
        
        greetings = {
            "早安": {
                "author": "早安 主人 今日的開發目標順利嗎",
                "normal": "早上好 今天有什麽事情儘早完成喲"
            },
            "午安": {
                "author": "下午好呀 今天似乎沒有什麼事情可以做呢",
                "normal": "中午好啊 看起來汝似乎無所事事的呢"
            },
            "晚安": {
                "author": f"你趕快去睡覺 現在已經是 {current_time} 了 別再熬夜了！",
                "normal": f"現在的時間是 {current_time} 汝還不就寢嗎？"
            }
        }
        
        greeting = greetings.get(message.content, {})
        response = greeting.get("author" if is_author else "normal", "...")
        await message.reply(response, mention_author=is_author)

    async def handle_shutdown(self, message):
        """處理關機指令"""
        if message.author.id == AUTHOR_ID:
            await message.channel.send("正在關閉...")
            self.bot.data_manager.save_all()
            await asyncio.sleep(2)
            await self.bot.close()
        else:
            await message.channel.send("你無權關閉我 >_<")

    async def handle_black_hole_activate(self, message):
        """啟動黑洞"""
        try:
            await message.delete()
        except (discord.Forbidden, discord.NotFound):
            await message.channel.send("⚠️ 無法刪除訊息，請確認我有刪除訊息的權限。")
            return
        
        self.bot.data_manager.black_hole_users.add(message.author.id)
        await message.channel.send("見過星辰粉碎的樣子嗎")

    async def handle_black_hole_release(self, message):
        """釋放黑洞"""
        if message.author.id not in self.bot.data_manager.black_hole_users:
            await message.channel.send("終結技能量不足")
            return
        
        try:
            await message.delete()
        except (discord.Forbidden, discord.NotFound):
            await message.channel.send("⚠️ 無法刪除訊息，請確認我有刪除訊息的權限。")
            return
        
        await message.channel.send("生存還是毀滅")
        await asyncio.sleep(3)
        await message.channel.send("你別無選擇")
        self.bot.data_manager.black_hole_users.discard(message.author.id)

    def record_dm_message(self, message):
        """記錄私訊"""
        user_id = str(message.author.id)
        dm_messages = self.bot.data_manager.dm_messages
        
        if user_id not in dm_messages:
            dm_messages[user_id] = []
        
        dm_messages[user_id].append({
            'content': message.content,
            'timestamp': message.created_at.isoformat()
        })
        
        self.bot.data_manager._save_json(
            "config/dm_messages.json",
            dm_messages
        )
        logger.info(f"私訊記錄: {message.author} - {message.content}")


def setup(bot):
    bot.add_cog(OnMessage(bot))
    logger.info("訊息處理模組已載入")
