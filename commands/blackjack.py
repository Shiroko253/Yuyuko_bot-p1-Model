import discord
from discord.ext import commands
from discord.commands import Option
import random
import logging
from typing import List, Tuple, Any

logger = logging.getLogger("SakuraBot.commands.blackjack")

# ✿ 冥界的櫻花下,幽幽子的21點遊戲 ✿
class BlackjackGame: # 21點遊戲類別
    """幽幽子為你準備的21點遊戲,櫻花下的靈魂也要歡樂一番～"""

    def __init__(self): # 初始化遊戲
        self.deck: List[str] = self.create_deck() # 建立卡組
        self.player_cards: List[str] = [] # 玩家的卡牌
        self.dealer_cards: List[str] = [] # 莊家的卡牌

    def create_deck(self) -> List[str]: # 建立卡組
        suits = ["♠", "♥", "♣", "♦"] # 花色
        ranks = [2, 3, 4, 5, 6, 7, 8, 9, 10, "J", "Q", "K", "A"] # 牌點
        return [f"{rank}{suit}" for suit in suits for rank in ranks] # 建立卡組

    def shuffle_deck(self) -> None: # 卡組
        random.shuffle(self.deck) # 洗牌

    def draw_card(self) -> str: # 抽卡
        if not self.deck: # 當沒有卡組時
            self.deck = self.create_deck() # 創建一個卡組
            self.shuffle_deck() # 返回給def shuffle_deck洗牌
        return self.deck.pop() # 抽出卡組最後一張牌

    def deal_initial_cards(self) -> Tuple[List[str], List[str]]: # 初始化卡牌
        self.player_cards = [self.draw_card(), self.draw_card()] # 抽給玩家的卡牌 一共兩張
        self.dealer_cards = [self.draw_card(), self.draw_card()] # 抽給莊家的卡牌 一共兩張
        return self.player_cards, self.dealer_cards # 回傳玩家和莊家的卡牌

    def calculate_hand(self, cards: List[str]) -> int: # 計算手牌
        value, aces = 0, 0 # 點數和A的數量
        for card in cards: # 逐張計算
            rank = card[:-1] # 取得牌的點數部分
            if rank in ["J", "Q", "K"]: # 如果牌是 J Q K
                value += 10 # 點數加10
            elif rank == "A": # 如果是 A
                aces += 1 # A的數量加1
                value += 11 # A先當11點
            else:
                value += int(rank) # 其他牌直接加點數
        while value > 21 and aces: # 如果點數超過21且有A
            value -= 10 # 將A當1點
            aces -= 1 # A的數量減1
        return value # 回傳點數

    def dealer_play(self) -> int: # 莊家行動
        while self.calculate_hand(self.dealer_cards) < 17: # 莊家點數小於17
            self.dealer_cards.append(self.draw_card()) # 莊家抽牌
        return self.calculate_hand(self.dealer_cards) # 回傳莊家點數

    def settle_game( # 結算遊戲
        self, # self參數
        player_cards: List[str], # 玩家卡牌
        dealer_cards: List[str], # 莊家卡牌
        bet: float, # 下注金額
        is_gambler: bool # 是否為賭徒職業
        # 如果是 則計算雙倍 賠率爲 3.5 否則爲 2
    ) -> Tuple[str, float]: # 回傳結果和獎勵
        player_total = self.calculate_hand(player_cards) # 計算玩家點數
        dealer_total = self.calculate_hand(dealer_cards) # 計算莊家點數
        multiplier = 3 if is_gambler else 2  # 賭徒職業賠率3 否則2
        
        if dealer_total > 21 or player_total > dealer_total: # 玩家贏的條件
            reward = round(bet * multiplier, 2) # 計算獎勵
            return "win", reward # 回傳贏和獎勵
        elif player_total == dealer_total: # 平手條件
            # 平手條件 回傳賭注
            return "tie", bet 
        else:
            return "lose", 0 # 輸了 回傳輸了和0獎勵

    @staticmethod # 靜態方法
    def progress_bar(value: int, max_value: int = 21) -> str: # 進度條
        filled = int(value / max_value * 10) # 計算填滿的格數
        return "🌸" * filled + "⋯" * (10 - filled) # 傳回進度條


class BlackjackButtons(discord.ui.View):
    def __init__(
        self,
        game: BlackjackGame,
        data_manager: Any,
        guild_id: str,
        user_id: str
    ):
        super().__init__(timeout=180)
        self.game = game
        self.data_manager = data_manager
        self.guild_id = str(guild_id)
        self.user_id = str(user_id)
        self.message = None

    async def on_timeout(self) -> None:
        try:
            async with self.data_manager.balance_lock:
                game_data = self.data_manager.blackjack_data.get(
                    self.guild_id, {}
                ).get(self.user_id, {})
                
                if game_data and game_data.get("game_status") == "ongoing":
                    bet = game_data["bet"]
                    self.data_manager.balance[self.guild_id][self.user_id] += bet
                    self.data_manager.blackjack_data[self.guild_id][self.user_id][
                        "game_status"
                    ] = "ended"
                    self.data_manager.save_all()
                    
                    if self.message:
                        await self.message.edit(
                            embed=discord.Embed(
                                title="🌸 遊戲超時,幽幽子靈魂小憩～",
                                description=(
                                    f"時間悄然流逝,幽幽子已收起櫻花。\n"
                                    f"退還你的賭注 **{bet:.2f}** 幽靈幣,下次再來一起賞花吧！"
                                ),
                                color=discord.Color.blue()
                            ).set_footer(text="如需再跳舞,請重新開始一局～"),
                            view=None
                        )
        except Exception as e:
            logger.exception(f"Timeout 處理失敗: {e}")

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if str(interaction.user.id) != self.user_id:
            await interaction.response.send_message(
                "這不是你的靈魂之舞喲～", ephemeral=True
            )
            return False
        return True

    async def auto_settle(self, interaction: discord.Interaction) -> bool:
        """自動結算 21 點"""
        async with self.data_manager.balance_lock:
            game_data = self.data_manager.blackjack_data[self.guild_id][self.user_id]
            player_cards = game_data["player_cards"]
            player_total = self.game.calculate_hand(player_cards)
            
            if player_total == 21:
                bet = game_data["bet"]
                is_gambler = game_data["is_gambler"]
                multiplier = 3.5 if is_gambler else 2.5
                reward = round(bet * multiplier, 2)
                
                self.data_manager.balance[self.guild_id][self.user_id] += reward
                self.data_manager.blackjack_data[self.guild_id][self.user_id][
                    "game_status"
                ] = "ended"
                self.data_manager.save_all()
                
                for child in self.children:
                    child.disabled = True
                
                await interaction.edit_original_response(
                    embed=discord.Embed(
                        title="🌸 黑傑克！櫻花下靈魂舞勝利！🌸",
                        description=(
                            f"**你的手牌:** {' '.join(player_cards)}\n"
                            f"**總點數:** 21 點\n\n"
                            f"幽幽子為你獻上 **{reward:.2f}** 幽靈幣的祝福～\n"
                            f"櫻花飄落,靈魂閃耀～"
                        ),
                        color=discord.Color.gold()
                    ).set_footer(text="恭喜你,靈魂閃爍！"),
                    view=None
                )
                logger.info(f"{self.user_id} 獲得 Blackjack, 贏得 {reward:.2f}")
                return True
        return False

    @discord.ui.button(label="抽牌 (Hit)", style=discord.ButtonStyle.primary, emoji="🎴")
    async def hit(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ):
        try:
            await interaction.response.defer()
            
            async with self.data_manager.balance_lock:
                game_data = self.data_manager.blackjack_data[self.guild_id][
                    self.user_id
                ]
                player_cards = game_data["player_cards"]
                player_cards.append(self.game.draw_card())
                player_total = self.game.calculate_hand(player_cards)
                game_data["player_cards"] = player_cards

                if player_total > 21:
                    game_data["game_status"] = "ended"
                    self.data_manager.save_all()
                    
                    for child in self.children:
                        child.disabled = True
                    
                    await interaction.edit_original_response(
                        embed=discord.Embed(
                            title="🌸 哎呀,櫻花散盡,靈魂爆掉了！🌸",
                            description=(
                                f"**你的手牌:** {' '.join(player_cards)}\n"
                                f"**點數總計:** {player_total}\n\n"
                                f"下次再來跟幽幽子共舞吧～"
                            ),
                            color=discord.Color.red()
                        ).set_footer(text="遊戲結束,冥界等待著你～"),
                        view=None
                    )
                    logger.info(f"{self.user_id} 爆牌, 點數: {player_total}")
                    return

            if await self.auto_settle(interaction):
                return

            await interaction.edit_original_response(
                embed=discord.Embed(
                    title="🌸 幽幽子為你送上新櫻花一片！🌸",
                    description=(
                        f"**你的手牌:** {' '.join(player_cards)}\n"
                        f"**目前點數:** {player_total} {self.game.progress_bar(player_total)}\n\n"
                        f"要繼續舞動,還是收手？"
                    ),
                    color=discord.Color.from_rgb(255, 182, 193)
                ).set_footer(text="命運在你手中～"),
                view=self
            )
        except Exception as e:
            logger.exception(f"Hit 操作失敗: {e}")
            await interaction.followup.send(
                "遊戲的櫻花散落了,請重新開始跟幽幽子共舞一局！", ephemeral=True
            )

    @discord.ui.button(label="停牌 (Stand)", style=discord.ButtonStyle.danger, emoji="✋")
    async def stand(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ):
        try:
            await interaction.response.defer()
            
            async with self.data_manager.balance_lock:
                game_data = self.data_manager.blackjack_data[self.guild_id][
                    self.user_id
                ]
                player_cards = game_data["player_cards"]
                dealer_cards = game_data["dealer_cards"]
                bet = game_data["bet"]
                is_gambler = game_data["is_gambler"]

                game_data["game_status"] = "ended"
                dealer_total = self.game.dealer_play()
                result, reward = self.game.settle_game(
                    player_cards, dealer_cards, bet, is_gambler
                )
                
                self.data_manager.balance[self.guild_id][self.user_id] += reward
                self.data_manager.save_all()

            for child in self.children:
                child.disabled = True
            
            # 根據結果設置標題和顏色
            titles = {
                "win": "🌸 靈魂之舞勝利！🌸",
                "tie": "🌸 櫻花平衡,靈魂平手～🌸",
                "lose": "🌸 冥界勝利,幽幽子守護～🌸"
            }
            colors = {
                "win": discord.Color.gold(),
                "tie": discord.Color.from_rgb(255, 182, 193),
                "lose": discord.Color.red()
            }
            results = {
                "win": f"你贏得了 **{reward:.2f}** 幽靈幣",
                "tie": f"退還賭注 **{reward:.2f}** 幽靈幣",
                "lose": "下次再來賞櫻吧～"
            }
            
            embed = discord.Embed(
                title=titles[result],
                description=(
                    f"**你的手牌:** {' '.join(player_cards)}\n"
                    f"**幽幽子的手牌:** {' '.join(dealer_cards)}\n\n"
                    f"{results[result]}"
                ),
                color=colors[result]
            ).set_footer(text="遊戲結束,櫻花依舊飄落～")
            
            await interaction.edit_original_response(embed=embed, view=None)
            logger.info(
                f"{self.user_id} Stand, 結果: {result}, 獎勵: {reward:.2f}"
            )
            
        except Exception as e:
            logger.exception(f"Stand 操作失敗: {e}")
            await interaction.followup.send(
                "櫻花舞失效了,請重新邀幽幽子共舞一局！", ephemeral=True
            )

    @discord.ui.button(
        label="雙倍 (Double)", style=discord.ButtonStyle.success, emoji="💰"
    )
    async def double_down(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ):
        try:
            await interaction.response.defer()
            
            async with self.data_manager.balance_lock:
                game_data = self.data_manager.blackjack_data[self.guild_id][
                    self.user_id
                ]
                
                if game_data["double_down_used"]:
                    await interaction.edit_original_response(
                        embed=discord.Embed(
                            title="🌸 命運只能挑戰一次！🌸",
                            description="你已經用過雙倍下注了哦～幽幽子的櫻花只能為你加持一次！",
                            color=discord.Color.red()
                        ).set_footer(text="每局只能一次櫻花加持"),
                        view=self
                    )
                    return

                bet = game_data["bet"]
                is_gambler = game_data["is_gambler"]
                user_balance = self.data_manager.balance[self.guild_id][self.user_id]
                doubled_bet = bet * 2

                if user_balance < bet:
                    await interaction.edit_original_response(
                        embed=discord.Embed(
                            title="🌸 櫻花能量不足～ 🌸",
                            description=(
                                f"你的幽靈幣只有 **{user_balance:.2f}**,\n"
                                f"不足以挑戰雙倍 **{doubled_bet:.2f}** 哦～"
                            ),
                            color=discord.Color.red()
                        ).set_footer(text="去冥界多收集一點幽靈幣吧"),
                        view=self
                    )
                    return

                game_data["bet"] = doubled_bet
                game_data["double_down_used"] = True
                self.data_manager.balance[self.guild_id][self.user_id] -= bet
                
                player_cards = game_data["player_cards"]
                dealer_cards = game_data["dealer_cards"]
                player_cards.append(self.game.draw_card())
                player_total = self.game.calculate_hand(player_cards)
                game_data["player_cards"] = player_cards
                game_data["game_status"] = "ended"

                if player_total > 21:
                    self.data_manager.save_all()
                    for child in self.children:
                        child.disabled = True
                    
                    embed = discord.Embed(
                        title="🌸 哎呀,靈魂爆掉了！🌸",
                        description=(
                            f"**你的手牌:** {' '.join(player_cards)}\n"
                            f"**總點數:** {player_total}\n\n"
                            f"下次再來賞櫻跳舞吧～"
                        ),
                        color=discord.Color.red()
                    ).set_footer(text="遊戲結束,櫻花謝了～")
                    
                    await interaction.edit_original_response(embed=embed, view=None)
                    logger.info(f"{self.user_id} Double Down 爆牌, 點數: {player_total}")
                    return

                dealer_total = self.game.dealer_play()
                result, reward = self.game.settle_game(
                    player_cards, dealer_cards, doubled_bet, is_gambler
                )
                
                self.data_manager.balance[self.guild_id][self.user_id] += reward
                self.data_manager.save_all()

            for child in self.children:
                child.disabled = True
            
            titles = {
                "win": "🌸 櫻花舞勝利！🌸",
                "tie": "🌸 靈魂平衡～🌸",
                "lose": "🌸 冥界勝利,幽幽子守護～🌸"
            }
            colors = {
                "win": discord.Color.gold(),
                "tie": discord.Color.from_rgb(255, 182, 193),
                "lose": discord.Color.red()
            }
            results = {
                "win": f"你贏得了 **{reward:.2f}** 幽靈幣",
                "tie": f"退還賭注 **{reward:.2f}** 幽靈幣",
                "lose": "下次再來共舞吧～"
            }
            
            embed = discord.Embed(
                title=titles[result],
                description=(
                    f"**你的手牌:** {' '.join(player_cards)}\n"
                    f"**幽幽子的手牌:** {' '.join(dealer_cards)}\n\n"
                    f"**雙倍賭注:** {doubled_bet:.2f}\n"
                    f"{results[result]}"
                ),
                color=colors[result]
            ).set_footer(text="遊戲結束,櫻花依舊飄落～")
            
            await interaction.edit_original_response(embed=embed, view=None)
            logger.info(
                f"{self.user_id} Double Down, 結果: {result}, 獎勵: {reward:.2f}"
            )
            
        except Exception as e:
            logger.exception(f"Double Down 操作失敗: {e}")
            await interaction.followup.send(
                "櫻花舞失效了,請重新邀幽幽子共舞一局！", ephemeral=True
            )


class Blackjack(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @discord.slash_command(
        name="blackjack",
        description="🌸 幽幽子邀你在冥界櫻花園共舞一場21點～"
    )
    async def blackjack(
        self,
        ctx: discord.ApplicationContext,
        bet: float = Option(float, "下注金額 (幽靈幣)", min_value=1.0)
    ):
        try:
            if not hasattr(self.bot, "data_manager"):
                await ctx.respond("❌ 數據管理器不存在", ephemeral=True)
                return

            data_manager = self.bot.data_manager
            bet = round(bet, 2)
            user_id = str(ctx.author.id)
            guild_id = str(ctx.guild.id)

            # 檢查是否有進行中的遊戲
            async with data_manager.balance_lock:
                if data_manager.blackjack_data.get(guild_id, {}).get(user_id, {}).get(
                    "game_status"
                ) == "ongoing":
                    await ctx.respond(
                        embed=discord.Embed(
                            title="🌸 靈魂還在跳舞！🌸",
                            description="你已經在進行一場櫻花舞了,請先完成再開新舞～",
                            color=discord.Color.red()
                        ).set_footer(text="舞終花謝,才能再邀幽幽子"),
                        ephemeral=True
                    )
                    return

                # 檢查餘額
                user_balance = round(
                    data_manager.balance.get(guild_id, {}).get(user_id, 0), 2
                )
                
                if user_balance < bet:
                    await ctx.respond(
                        embed=discord.Embed(
                            title="🌸 幽靈幣不足,櫻花不開～ 🌸",
                            description=(
                                f"你的幽靈幣只有 **{user_balance:.2f}**,\n"
                                f"無法下注 **{bet:.2f}** 哦～\n\n"
                                f"再去冥界多收集一些吧！"
                            ),
                            color=discord.Color.red()
                        ).set_footer(text="櫻花園的舞者需要充足靈魂"),
                        ephemeral=True
                    )
                    return

                # 創建遊戲
                game = BlackjackGame()
                game.shuffle_deck()
                player_cards, dealer_cards = game.deal_initial_cards()

                # 扣除賭注
                data_manager.balance.setdefault(guild_id, {})[user_id] = (
                    user_balance - bet
                )

                # 檢查是否為賭徒職業
                config = data_manager._load_yaml("config/config_user.yml", default={})
                is_gambler = (
                    config.get(guild_id, {}).get(user_id, {}).get("job") == "賭徒"
                )

                # 初始化遊戲數據
                if guild_id not in data_manager.blackjack_data:
                    data_manager.blackjack_data[guild_id] = {}
                if user_id not in data_manager.blackjack_data[guild_id]:
                    data_manager.blackjack_data[guild_id][user_id] = {}
                
                data_manager.blackjack_data[guild_id][user_id].update({
                    "player_cards": player_cards,
                    "dealer_cards": dealer_cards,
                    "bet": bet,
                    "game_status": "ongoing",
                    "double_down_used": False,
                    "is_gambler": is_gambler
                })

                player_total = game.calculate_hand(player_cards)
                
                # 檢查 Blackjack
                if player_total == 21:
                    multiplier = 3.5 if is_gambler else 2.5
                    reward = round(bet * multiplier, 2)
                    data_manager.balance[guild_id][user_id] += reward
                    data_manager.blackjack_data[guild_id][user_id][
                        "game_status"
                    ] = "ended"
                    data_manager.save_all()

                    await ctx.respond(
                        embed=discord.Embed(
                            title="🌸 黑傑克！櫻花魂閃耀！🌸",
                            description=(
                                f"**你的手牌:** {' '.join(player_cards)}\n\n"
                                f"幽幽子為你獻上 **{reward:.2f}** 幽靈幣的祝福～\n"
                                f"今晚櫻花舞更盛～"
                            ),
                            color=discord.Color.gold()
                        ).set_footer(text="恭喜！櫻花灑滿冥界")
                    )
                    logger.info(f"{user_id} 開局 Blackjack, 贏得 {reward:.2f}")
                    return

                data_manager.save_all()

            # 顯示初始狀態
            embed = discord.Embed(
                title="🌸 幽幽子的櫻花21點舞開始！🌸",
                description=(
                    f"你下注了 **{bet:.2f}** 幽靈幣,幽幽子邀你共舞～\n\n"
                    f"**你的初始手牌:** {' '.join(player_cards)}\n"
                    f"**總點數:** {player_total} {game.progress_bar(player_total)}\n\n"
                    f"**幽幽子的明牌:** {dealer_cards[0]}"
                ),
                color=discord.Color.from_rgb(255, 182, 193)
            ).set_footer(text="選擇命運吧～櫻花舞只等你來")
            
            msg = await ctx.respond(embed=embed, view=None)
            view = BlackjackButtons(game, data_manager, guild_id, user_id)
            view.message = await msg.original_response()
            await view.message.edit(view=view)
            
            logger.info(f"{user_id} 開始 Blackjack, 下注: {bet:.2f}")

        except Exception as e:
            logger.exception(f"Blackjack 指令失敗: {e}")
            await ctx.respond(
                embed=discord.Embed(
                    title="🌸 冥界櫻花飄散了～ 🌸",
                    description="哎呀,櫻花舞出了點小問題,請稍後再來邀幽幽子共舞！",
                    color=discord.Color.red()
                ).set_footer(text="如有問題請找冥界管理員"),
                ephemeral=True
            )

def setup(bot: discord.Bot):
    bot.add_cog(Blackjack(bot))
    logger.info("Blackjack 遊戲系統已載入")
