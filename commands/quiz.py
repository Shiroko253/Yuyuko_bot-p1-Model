import discord
from discord.ext import commands
import random
import logging

logger = logging.getLogger("SakuraBot.Quiz")


class QuizView(discord.ui.View):
    """幽幽子的問答視圖,如櫻花般優雅又帶著冥界的惡意"""
    
    def __init__(self, ctx, question_data):
        super().__init__(timeout=30)
        self.ctx = ctx
        self.question = question_data.get("question", "")
        self.correct_answer = question_data.get("correct", "")
        self.difficulty = question_data.get("difficulty", "medium")
        self.reward = question_data.get("reward", 50)
        self.answered = False
        
        # 打亂選項
        options = [self.correct_answer] + question_data.get("incorrect", [])
        random.shuffle(options)
        
        # 為每個選項添加按鈕
        for option in options:
            self.add_item(QuizButton(option, self))

    async def on_timeout(self):
        """時間到時的處理,幽幽子會帶著遺憾飄走"""
        if self.answered:
            return
        
        timeout_messages = [
            "⏳ 時間到了呢～幽幽子都等到櫻花凋零了！",
            "⏰ 太慢了...幽幽子的耐心比櫻花瓣還短呢～",
            "⌛ 猶豫的靈魂注定迷失在冥界...時間到！",
            "⏳ 嘻嘻，連冥界的幽靈都比你快呢～時間到！"
        ]
        
        embed = discord.Embed(
            title="🪭 幽幽子的問答時間結束",
            description=(
                f"**題目**: {self.question}\n\n"
                f"{random.choice(timeout_messages)}\n"
                f"**正確答案**: `{self.correct_answer}`\n"
                f"**錯失獎勵**: `{self.reward:,}` 幽靈幣\n\n"
                f"*下次動作快一點,不要讓幽幽子等太久哦～*"
            ),
            color=discord.Color.dark_grey(),
            timestamp=discord.utils.utcnow()
        )
        embed.set_footer(text="幽靈的謎題只有 30 秒 · 猶豫就會敗北")
        
        # 禁用所有按鈕
        for child in self.children:
            child.disabled = True
        
        try:
            await self.message.edit(embed=embed, view=self)
            logger.info(f"⏰ 問答超時: {self.ctx.user.name} 未能在時間內作答")
        except Exception as e:
            logger.warning(f"⚠️ QuizView 超時編輯訊息失敗: {e}")


class QuizButton(discord.ui.Button):
    """問答按鈕,承載著幽幽子的惡趣味與獎勵"""
    
    def __init__(self, label, quiz_view):
        super().__init__(label=label, style=discord.ButtonStyle.secondary)
        self.quiz_view = quiz_view
        self.is_correct = label == quiz_view.correct_answer
        
        # 幽幽子的嘲諷語錄 (答錯時使用)
        self.wrong_messages = [
            "呵呵...這麼簡單都答錯？幽幽子都替你的智商感到悲哀呢～",
            "哎呀呀，這種程度的題目都不會嗎？連冥界的迷途靈魂都比你聰明呢！",
            "嘻嘻...錯得如此離譜，幽幽子都忍不住笑出聲了～",
            "真是可悲的選擇啊，你的靈魂似乎需要在冥界修煉一番了呢～",
            "哈？這都能選錯？你是故意逗幽幽子笑的嗎？",
            "唉，看來你的智慧就像凋零的櫻花，早已隨風而逝了～",
            "這答案...幽幽子懷疑你是不是故意來送死的？",
            "啊啦啦～這麼蠢的選擇，就連冥界的餓鬼都搖頭了呢！",
            "呼呼...錯到讓幽幽子都不忍心繼續看下去了～",
            "這智商...幽幽子建議你去冥界重修一下腦子吧～"
        ]
        
        # 幽幽子的讚美語錄 (答對時使用)
        self.correct_messages = [
            "嘻嘻，答對了呢～看來你的靈魂還算聰慧嘛！",
            "呵呵，不錯嘛～幽幽子為你的智慧鼓掌！",
            "哎呀，居然答對了？幽幽子還以為你會錯呢～",
            "聰明的靈魂值得櫻花的祝福～答對啦！",
            "嗯～這次表現不錯，幽幽子很滿意呢！",
            "呼呼...看來你的智慧配得上冥界的認可～",
            "正確！你的靈魂閃耀著智慧之光呢～",
            "答對了！幽幽子都為你感到驕傲了～"
        ]

    async def callback(self, interaction: discord.Interaction):
        """按鈕點擊回調,幽幽子的審判與獎勵時刻"""
        
        # === 權限檢查 ===
        if interaction.user != self.quiz_view.ctx.author:
            return await interaction.response.send_message(
                "❌ 哎呀，這是給別人的謎題哦～不要搶答呢！",
                ephemeral=True
            )

        if self.quiz_view.answered:
            return await interaction.response.send_message(
                "⏳ 這題已經解開啦，幽靈不會重複問哦！",
                ephemeral=True
            )

        # === 標記已作答並停止計時 ===
        self.quiz_view.answered = True
        self.quiz_view.stop()

        # === 更新按鈕狀態 ===
        for child in self.quiz_view.children:
            child.disabled = True
            if isinstance(child, discord.ui.Button):
                if child.label == self.quiz_view.correct_answer:
                    child.style = discord.ButtonStyle.success  # 正確答案標綠
                else:
                    child.style = discord.ButtonStyle.danger   # 其他答案標紅

        # === 獲取數據管理器 ===
        data_manager = getattr(self.quiz_view.ctx.bot, "data_manager", None)
        
        # === 根據答案生成回應與獎勵 ===
        if self.is_correct:
            # 答對了! 給予獎勵
            reward_amount = self.quiz_view.reward
            
            # 添加獎勵加成 (隨機 0-20%)
            bonus_multiplier = random.uniform(1.0, 1.2)
            final_reward = int(reward_amount * bonus_multiplier)
            bonus_text = f" (含 {int((bonus_multiplier - 1) * 100)}% 加成)" if bonus_multiplier > 1.0 else ""
            
            # 更新餘額
            if data_manager:
                guild_id = str(self.quiz_view.ctx.guild.id)
                user_id = str(interaction.user.id)
                
                async with data_manager.balance_lock:
                    if guild_id not in data_manager.balance:
                        data_manager.balance[guild_id] = {}
                    if user_id not in data_manager.balance[guild_id]:
                        data_manager.balance[guild_id][user_id] = 0
                    
                    old_balance = data_manager.balance[guild_id][user_id]
                    data_manager.balance[guild_id][user_id] += final_reward
                    new_balance = data_manager.balance[guild_id][user_id]
                
                await data_manager.save_all_async()
                
                balance_info = (
                    f"\n\n💰 **獎勵發放**\n"
                    f"獲得: `+{final_reward:,}` 幽靈幣{bonus_text}\n"
                    f"餘額: `{old_balance:,}` → `{new_balance:,}` 幽靈幣"
                )
            else:
                balance_info = f"\n\n💰 **理論獎勵**: `{final_reward:,}` 幽靈幣 (未連接數據庫)"
            
            description = (
                f"**題目**: {self.quiz_view.question}\n\n"
                f"✅ **{random.choice(self.correct_messages)}** 🎉\n\n"
                f"*你的靈魂在冥界閃耀著智慧之光～*"
                f"{balance_info}"
            )
            color = discord.Color.green()
            footer_text = "幽幽子的讚許 · 聰明的靈魂值得獎勵"
            
            logger.info(f"✅ {interaction.user.name} 答對題目，獲得 {final_reward:,} 幽靈幣")
        else:
            # 答錯了...接受嘲諷但沒有懲罰
            description = (
                f"**題目**: {self.quiz_view.question}\n\n"
                f"❌ **{random.choice(self.wrong_messages)}**\n\n"
                f"**正確答案**: `{self.quiz_view.correct_answer}`\n"
                f"**你的答案**: `{self.label}`\n\n"
                f"💔 **錯失獎勵**: `{self.quiz_view.reward:,}` 幽靈幣\n\n"
                f"*幽幽子建議你多讀點書再來挑戰哦～*"
            )
            color = discord.Color.red()
            footer_text = "幽幽子的嘲諷 · 錯誤的靈魂需要修煉"
            
            logger.info(f"❌ {interaction.user.name} 答錯題目 (選擇: {self.label})")

        # === 發送結果 Embed ===
        embed = discord.Embed(
            title="🪭 幽幽子的問答結果",
            description=description,
            color=color,
            timestamp=discord.utils.utcnow()
        )
        embed.set_footer(text=footer_text)
        
        await interaction.response.edit_message(embed=embed, view=self.quiz_view)


class QuizCog(commands.Cog):
    """
    🌸 幽幽子的靈魂問答 🌸
    挑戰幽幽子的謎題,測試你的靈魂智慧～答對有獎勵,答錯被嘲諷
    """
    
    def __init__(self, bot):
        self.bot = bot
        logger.info("🌸 問答挑戰指令已甦醒")
        
        # 難度對應的獎勵範圍 (已更新)
        self.difficulty_rewards = {
            "easy": (10, 50),           # 簡單題: 10-50 幽靈幣
            "medium": (70, 500),        # 中等題: 70-500 幽靈幣
            "hard": (1000, 10000),      # 困難題: 1000-10000 幽靈幣
            "extreme": (6000, 700000)   # 超困難題: 6000-700000 幽靈幣
        }

    @discord.slash_command(
        name="quiz",
        description="挑戰幽幽子的靈魂謎題～答對有獎勵,答錯會被嘲諷哦"
    )
    async def quiz(self, ctx: discord.ApplicationContext):
        """幽幽子出題考驗你的智慧,如同在櫻花樹下的靈魂試煉"""
        
        data_manager = getattr(ctx.bot, "data_manager", None)
        
        # === 載入題庫 ===
        try:
            if data_manager:
                quiz_data = data_manager._load_json("config/quiz.json", default=[])
            else:
                logger.warning("⚠️ 未找到 data_manager,使用備用載入方式")
                import json
                with open("config/quiz.json", "r", encoding="utf-8") as f:
                    quiz_data = json.load(f) or []
        except FileNotFoundError:
            logger.error("❌ quiz.json 檔案不存在")
            return await ctx.respond(
                embed=self._create_error_embed(
                    "題庫遺失",
                    "哎呀，題庫檔案消失了...就像幽靈一樣！\n請聯絡管理員確認 `config/quiz.json` 是否存在。"
                ),
                ephemeral=True
            )
        except Exception as e:
            logger.error(f"❌ 讀取 quiz.json 失敗: {e}")
            return await ctx.respond(
                embed=self._create_error_embed(
                    "題庫讀取失敗",
                    f"幽幽子在讀取題庫時遇到了障礙...\n錯誤: `{str(e)}`"
                ),
                ephemeral=True
            )

        # === 檢查題庫是否為空 ===
        if not quiz_data:
            logger.warning("⚠️ quiz.json 題庫為空")
            return await ctx.respond(
                embed=self._create_error_embed(
                    "題庫空空如也",
                    "哎呀，題庫空空的...就像幽幽子的肚子一樣！\n請管理員添加題目到 `config/quiz.json`。"
                ),
                ephemeral=True
            )

        # === 隨機選擇題目並自動判定難度 ===
        question_data = random.choice(quiz_data)
        
        # 自動判定難度 (如果未設定)
        if "difficulty" not in question_data:
            question_data["difficulty"] = self._auto_detect_difficulty(question_data)
        
        # 根據難度設定獎勵 (如果未設定)
        if "reward" not in question_data:
            difficulty = question_data["difficulty"]
            reward_range = self.difficulty_rewards.get(difficulty, (70, 500))
            question_data["reward"] = random.randint(reward_range[0], reward_range[1])
        
        question = question_data.get("question", "")
        correct_answer = question_data.get("correct", "")
        incorrect_answers = question_data.get("incorrect", [])
        difficulty = question_data["difficulty"]
        reward = question_data["reward"]

        # === 驗證題目格式 ===
        if not question or not correct_answer or len(incorrect_answers) != 3:
            logger.warning(f"⚠️ quiz.json 題目格式錯誤: {question_data}")
            return await ctx.respond(
                embed=self._create_error_embed(
                    "題目格式錯誤",
                    "這道題目的格式有問題呢...\n請檢查 `quiz.json` 格式是否正確:\n"
                    "```json\n{\n  \"question\": \"題目\",\n  \"correct\": \"正確答案\",\n  "
                    "\"incorrect\": [\"錯誤1\", \"錯誤2\", \"錯誤3\"],\n  "
                    "\"difficulty\": \"easy/medium/hard/extreme\",\n  \"reward\": 50\n}\n```"
                ),
                ephemeral=True
            )

        # === 難度標示 (已更新) ===
        difficulty_display = {
            "easy": "🟢 簡單",
            "medium": "🟡 中等",
            "hard": "🔴 困難",
            "extreme": "💀 超困難"
        }

        # === 創建問答 Embed ===
        embed = discord.Embed(
            title="🪭 幽幽子的靈魂問答挑戰",
            description=(
                f"**{question}**\n\n"
                f"📊 **難度**: {difficulty_display.get(difficulty, '🟡 中等')}\n"
                f"💰 **獎勵**: `{reward:,}` 幽靈幣 (答對可獲得獎勵加成!)\n\n"
                f"嘻嘻，這可不是簡單的謎題呢～\n"
                f"快選一個答案吧！答錯的話...呵呵呵..."
            ),
            color=discord.Color.from_rgb(255, 182, 193),
            timestamp=discord.utils.utcnow()
        )
        embed.set_footer(text="⏰ 幽靈的謎題只有 30 秒 · 猶豫就會敗北")

        # === 創建問答視圖並發送 ===
        view = QuizView(ctx, question_data)
        message = await ctx.respond(embed=embed, view=view)
        
        # === 設定 message 引用以便超時編輯 ===
        try:
            if hasattr(message, "original_response"):
                view.message = await message.original_response()
            else:
                view.message = message
        except Exception as e:
            logger.warning(f"⚠️ QuizCog 設定 view.message 失敗: {e}")

        logger.info(f"📝 已為 {ctx.user.name} 出題 [{difficulty}]: {question} (獎勵: {reward:,})")

    def _auto_detect_difficulty(self, question_data: dict) -> str:
        """根據題目內容自動判定難度"""
        question = question_data.get("question", "").lower()
        
        # 超困難題關鍵字
        extreme_keywords = [
            "quantum", "qubit", "grover", "np-complete", "byzantine", "paxos",
            "zero-knowledge", "merkle", "cap 定理", "raft", "crdt", "lamport",
            "vector clock", "2pc", "bloom filter", "consistent hashing",
            "mapreduce", "gossip protocol", "chord dht", "clock tree synthesis",
            "amdahl", "量子", "分散式", "共識", "區塊鏈"
        ]
        
        # 困難題關鍵字
        hard_keywords = [
            "mosfet", "cmos", "ttl", "fpga", "ofdm", "mimo", "傅立葉", 
            "麥克斯韋", "shannon", "rayleigh", "metastability", "jk 觸發器",
            "卡諾圖", "時序約束", "波導", "匹配網路", "setup time", "hold time",
            "clock skew", "verilog", "dynamic power"
        ]
        
        # 簡單題關鍵字
        easy_keywords = [
            "cat", "apple", "thank you", "good morning", "bonjour",
            "hola", "danke", "arigato", "幽靈幣", "櫻花", "貓咪",
            "一天", "太陽", "水", "一年", "彩虹", "地球", "冰"
        ]
        
        # 檢查超困難關鍵字
        if any(keyword in question for keyword in extreme_keywords):
            return "extreme"
        
        # 檢查困難關鍵字
        if any(keyword in question for keyword in hard_keywords):
            return "hard"
        
        # 檢查簡單關鍵字
        if any(keyword in question for keyword in easy_keywords):
            return "easy"
        
        # 默認中等
        return "medium"

    @staticmethod
    def _create_error_embed(title: str, description: str) -> discord.Embed:
        """創建錯誤提示 Embed"""
        return discord.Embed(
            title=f"🌸 {title}",
            description=description,
            color=discord.Color.red(),
            timestamp=discord.utils.utcnow()
        )


def setup(bot):
    bot.add_cog(QuizCog(bot))
    logger.info("✨ 問答挑戰 Cog 已載入完成")
