import discord
from discord.ext import commands
import random
import logging
from typing import List, Tuple, Any
import asyncio
from datetime import datetime

# ✿ 冥界的櫻花下，幽幽子的21點遊戲 ✿
class BlackjackGame:
    """
    幽幽子為你準備的21點遊戲，櫻花下的靈魂也要歡樂一番～
    """

    def __init__(self):
        self.deck: List[str] = self.create_deck()
        self.player_cards: List[str] = []
        self.dealer_cards: List[str] = []

    def create_deck(self) -> List[str]:
        suits = ["♠", "♥", "♣", "♦"]
        ranks = [2, 3, 4, 5, 6, 7, 8, 9, 10, "J", "Q", "K", "A"]
        return [f"{rank}{suit}" for suit in suits for rank in ranks]

    def shuffle_deck(self) -> None:
        random.shuffle(self.deck)

    def draw_card(self) -> str:
        if not self.deck:
            self.deck = self.create_deck()
            self.shuffle_deck()
        return self.deck.pop()

    def calculate_hand(self, cards: List[str]) -> int:
        value, aces = 0, 0
        for card in cards:
            rank = card[:-1]
            if rank in ["J", "Q", "K"]:
                value += 10
            elif rank == "A":
                aces += 1
                value += 11
            else:
                try:
                    value += int(rank)
                except ValueError:
                    logging.warning(f"Invalid card rank: {rank}")
                    value += 0
        while value > 21 and aces:
            value -= 10
            aces -= 1
        return value

    def deal_initial_cards(self) -> Tuple[List[str], List[str]]:
        """發初始牌"""
        self.player_cards = [self.draw_card(), self.draw_card()]
        self.dealer_cards = [self.draw_card(), self.draw_card()]
        return self.player_cards.copy(), self.dealer_cards.copy()

    def dealer_play(self) -> int:
        while self.calculate_hand(self.dealer_cards) < 17:
            self.dealer_cards.append(self.draw_card())
        return self.calculate_hand(self.dealer_cards)

    def settle_game(self, player_cards: List[str], dealer_cards: List[str], bet: float, is_gambler: bool) -> Tuple[str, float]:
        player_total = self.calculate_hand(player_cards)
        dealer_total = self.calculate_hand(dealer_cards)
        multiplier = 3 if is_gambler else 2
        if dealer_total > 21 or player_total > dealer_total:
            reward = round(bet * multiplier, 2)
            return "win", reward
        elif player_total == dealer_total:
            return "tie", bet
        else:
            return "lose", 0

    @staticmethod
    def progress_bar(value: int, max_value: int = 21) -> str:
        filled = min(int(value / max_value * 10), 10)
        return "🌸" * filled + "⋯" * (10 - filled)


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
        self.logger = logging.getLogger("SakuraBot.commands.blackjack")

    async def on_timeout(self) -> None:
        try:
            if self.guild_id not in self.data_manager.blackjack_data or self.user_id not in self.data_manager.blackjack_data[self.guild_id]:
                return
                
            game_data = self.data_manager.blackjack_data[self.guild_id][self.user_id]
            if game_data and game_data.get("game_status") == "ongoing":
                bet = game_data["bet"]
                if self.guild_id not in self.data_manager.balance:
                    self.data_manager.balance[self.guild_id] = {}
                current_balance = self.data_manager.balance[self.guild_id].get(self.user_id, 0)
                # ✅ 修正：使用 self.user_id 而不是 user_id
                self.data_manager.balance[self.guild_id][self.user_id] = current_balance + bet
                self.data_manager.blackjack_data[self.guild_id][self.user_id]["game_status"] = "ended"
                self.data_manager.save_all()
        except Exception as e:
            self.logger.error(f"Timeout handling failed: {e}")

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if str(interaction.user.id) != self.user_id:
            await interaction.response.send_message("這不是你的靈魂之舞喲～", ephemeral=True)
            return False
        return True

    async def auto_settle(self, interaction: discord.Interaction) -> bool:
        try:
            if self.guild_id not in self.data_manager.blackjack_data or self.user_id not in self.data_manager.blackjack_data[self.guild_id]:
                return False
                
            game_data = self.data_manager.blackjack_data[self.guild_id][self.user_id]
            player_cards = game_data["player_cards"]
            player_total = self.game.calculate_hand(player_cards)
            if player_total == 21:
                bet = game_data["bet"]
                is_gambler = game_data["is_gambler"]
                multiplier = 3.5 if is_gambler else 2.5
                reward = round(bet * multiplier, 2)
                if self.guild_id not in self.data_manager.balance:
                    self.data_manager.balance[self.guild_id] = {}
                current_balance = self.data_manager.balance[self.guild_id].get(self.user_id, 0)
                self.data_manager.balance[self.guild_id][self.user_id] = current_balance + reward
                self.data_manager.blackjack_data[self.guild_id][self.user_id]["game_status"] = "ended"
                self.data_manager.save_all()
                for child in self.children:
                    child.disabled = True
                await interaction.response.edit_message(
                    embed=discord.Embed(
                        title="🌸 黑傑克！櫻花下靈魂舞勝利！🌸",
                        description=f"你的手牌: {player_cards}\n幽幽子為你獻上 {reward:.2f} 幽靈幣的祝福～\n櫻花飄落，靈魂閃耀～",
                        color=discord.Color.gold()
                    ).set_footer(text="恭喜你，靈魂閃爍！"),
                    view=self
                )
                return True
        except Exception as e:
            self.logger.error(f"Auto settle failed: {e}")
        return False

    @discord.ui.button(label="抽牌 (Hit)", style=discord.ButtonStyle.primary)
    async def hit(self, button: discord.ui.Button, interaction: discord.Interaction):
        try:
            if self.guild_id not in self.data_manager.blackjack_data or self.user_id not in self.data_manager.blackjack_data[self.guild_id]:
                await interaction.response.edit_message(
                    content="遊戲資料遺失，請重新開始！",
                    embed=None,
                    view=None
                )
                return

            game_data = self.data_manager.blackjack_data[self.guild_id][self.user_id]
            if game_data.get("game_status") != "ongoing":
                await interaction.response.edit_message(
                    content="遊戲已結束，請重新開始！",
                    embed=None,
                    view=None
                )
                return

            player_cards = game_data["player_cards"]
            player_cards.append(self.game.draw_card())
            player_total = self.game.calculate_hand(player_cards)
            game_data["player_cards"] = player_cards

            if player_total > 21:
                game_data["game_status"] = "ended"
                self.data_manager.save_all()
                for child in self.children:
                    child.disabled = True
                await interaction.response.edit_message(
                    embed=discord.Embed(
                        title="🌸 哎呀，櫻花散盡，靈魂爆掉了！🌸",
                        description=f"你的手牌: {player_cards}\n點數總計: {player_total}\n下次再來跟幽幽子共舞吧～",
                        color=discord.Color.red()
                    ).set_footer(text="遊戲結束，冥界等待著你～"),
                    view=self
                )
                return

            if await self.auto_settle(interaction):
                return

            await interaction.response.edit_message(
                embed=discord.Embed(
                    title="🌸 幽幽子為你送上新櫻花一片！🌸",
                    description=f"你的手牌: {player_cards}\n目前點數: {player_total} {self.game.progress_bar(player_total)}",
                    color=discord.Color.from_rgb(255, 182, 193)
                ).set_footer(text="要繼續舞動，還是收手？"),
                view=self
            )
        except Exception as e:
            self.logger.error(f"Hit interaction failed: {e}")
            await interaction.response.send_message("遊戲的櫻花散落了，請重新開始跟幽幽子共舞一局！", ephemeral=True)

    @discord.ui.button(label="停牌 (Stand)", style=discord.ButtonStyle.danger)
    async def stand(self, button: discord.ui.Button, interaction: discord.Interaction):
        try:
            if self.guild_id not in self.data_manager.blackjack_data or self.user_id not in self.data_manager.blackjack_data[self.guild_id]:
                await interaction.response.edit_message(
                    content="遊戲資料遺失，請重新開始！",
                    embed=None,
                    view=None
                )
                return

            game_data = self.data_manager.blackjack_data[self.guild_id][self.user_id]
            if game_data.get("game_status") != "ongoing":
                await interaction.response.edit_message(
                    content="遊戲已結束，請重新開始！",
                    embed=None,
                    view=None
                )
                return

            player_cards = game_data["player_cards"]
            dealer_cards = game_data["dealer_cards"]
            bet = game_data["bet"]
            is_gambler = game_data["is_gambler"]

            game_data["game_status"] = "ended"
            dealer_total = self.game.dealer_play()
            result, reward = self.game.settle_game(player_cards, dealer_cards, bet, is_gambler)
            
            if self.guild_id not in self.data_manager.balance:
                self.data_manager.balance[self.guild_id] = {}
            current_balance = self.data_manager.balance[self.guild_id].get(self.user_id, 0)
            self.data_manager.balance[self.guild_id][self.user_id] = current_balance + reward
            self.data_manager.save_all()

            for child in self.children:
                child.disabled = True
            embed = discord.Embed(
                title="🌸 靈魂之舞勝利！🌸" if result == "win" else "🌸 櫻花平衡，靈魂平手～🌸" if result == "tie" else "🌸 冥界勝利，幽幽子守護～🌸",
                description=f"你的手牌: {player_cards}\n幽幽子的手牌: {dealer_cards}\n{'你贏得了' if result == 'win' else '退還賭注' if result == 'tie' else '下次再來賞櫻吧～'} {reward:.2f} 幽靈幣",
                color=discord.Color.gold() if result == "win" else discord.Color.from_rgb(255, 182, 193) if result == "tie" else discord.Color.red()
            ).set_footer(text="遊戲結束，櫻花依舊飄落～")
            await interaction.response.edit_message(embed=embed, view=self)
        except Exception as e:
            self.logger.error(f"Stand interaction failed: {e}")
            await interaction.response.send_message("櫻花舞失效了，請重新邀幽幽子共舞一局！", ephemeral=True)

    @discord.ui.button(label="雙倍下注 (Double Down)", style=discord.ButtonStyle.success)
    async def double_down(self, button: discord.ui.Button, interaction: discord.Interaction):
        try:
            if self.guild_id not in self.data_manager.blackjack_data or self.user_id not in self.data_manager.blackjack_data[self.guild_id]:
                await interaction.response.edit_message(
                    content="遊戲資料遺失，請重新開始！",
                    embed=None,
                    view=None
                )
                return

            game_data = self.data_manager.blackjack_data[self.guild_id][self.user_id]
            if game_data.get("game_status") != "ongoing":
                await interaction.response.edit_message(
                    content="遊戲已結束，請重新開始！",
                    embed=None,
                    view=None
                )
                return

            if game_data["double_down_used"]:
                await interaction.response.edit_message(
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
            
            if self.guild_id not in self.data_manager.balance:
                self.data_manager.balance[self.guild_id] = {}
            user_balance = self.data_manager.balance[self.guild_id].get(self.user_id, 0)
            doubled_bet = bet * 2

            if user_balance < bet:
                await interaction.response.edit_message(
                    embed=discord.Embed(
                        title="🌸 櫻花能量不足～ 🌸",
                        description=f"你的幽靈幣只有 {user_balance:.2f}，不足以挑戰雙倍 {doubled_bet:.2f} 哦～",
                        color=discord.Color.red()
                    ).set_footer(text="去冥界多收集一點幽靈幣吧"),
                    view=self
                )
                return

            game_data["bet"] = doubled_bet
            game_data["double_down_used"] = True
            current_balance = self.data_manager.balance[self.guild_id].get(self.user_id, 0)
            self.data_manager.balance[self.guild_id][self.user_id] = current_balance - bet
            player_cards = game_data["player_cards"]
            dealer_cards = game_data["dealer_cards"]
            player_cards.append(self.game.draw_card())
            player_total = self.game.calculate_hand(player_cards)
            game_data["player_cards"] = player_cards
            game_data["game_status"] = "ended"
            self.data_manager.save_all()

            if player_total > 21:
                for child in self.children:
                    child.disabled = True
                await interaction.response.edit_message(
                    embed=discord.Embed(
                        title="🌸 哎呀，靈魂爆掉了！🌸",
                        description=f"你的手牌: {player_cards}\n總點數: {player_total}\n下次再來賞櫻跳舞吧～",
                        color=discord.Color.red()
                    ).set_footer(text="遊戲結束，櫻花謝了～"),
                    view=self
                )
                return

            dealer_total = self.game.dealer_play()
            result, reward = self.game.settle_game(player_cards, dealer_cards, doubled_bet, is_gambler)
            
            if self.guild_id not in self.data_manager.balance:
                self.data_manager.balance[self.guild_id] = {}
            current_balance = self.data_manager.balance[self.guild_id].get(self.user_id, 0)
            self.data_manager.balance[self.guild_id][self.user_id] = current_balance + reward
            self.data_manager.save_all()

            for child in self.children:
                child.disabled = True
            embed_title = "🌸 櫻花舞勝利！🌸" if result == "win" else "🌸 靈魂平衡～🌸" if result == "tie" else "🌸 冥界勝利，幽幽子守護～🌸"
            embed_desc = f"你的手牌: {player_cards}\n幽幽子的手牌: {dealer_cards}\n{'你贏得了' if result == 'win' else '退還賭注' if result == 'tie' else '下次再來共舞吧～'} {reward:.2f} 幽靈幣"
            embed_color = discord.Color.gold() if result == "win" else discord.Color.from_rgb(255, 182, 193) if result == "tie" else discord.Color.red()
            await interaction.response.edit_message(
                embed=discord.Embed(
                    title=embed_title,
                    description=embed_desc,
                    color=embed_color
                ).set_footer(text="遊戲結束，櫻花依舊飄落～"),
                view=self
            )
        except Exception as e:
            self.logger.error(f"Double down interaction failed: {e}")
            await interaction.response.send_message("櫻花舞失效了，請重新邀幽幽子共舞一局！", ephemeral=True)


class Blackjack(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot
        self.logger = logging.getLogger("SakuraBot.commands.blackjack")
        self.game_locks = {}

    def _get_game_lock(self, user_id: str) -> asyncio.Lock:
        if user_id not in self.game_locks:
            self.game_locks[user_id] = asyncio.Lock()
        return self.game_locks[user_id]

    @discord.slash_command(
        name="blackjack",
        description="幽幽子邀你在冥界櫻花園共舞一場21點～"
    )
    async def blackjack(self, ctx: discord.ApplicationContext, bet: float):
        try:
            user_id = str(ctx.author.id)
            guild_id = str(ctx.guild.id)
            
            data_manager = getattr(self.bot, "data_manager", None)
            if not data_manager:
                await ctx.respond(
                    embed=discord.Embed(
                        title="🌸 系統錯誤 🌸",
                        description="幽幽子的資料管理員暫時不在，請稍後再來～",
                        color=discord.Color.red()
                    ).set_footer(text="如有問題請找管理員"),
                    ephemeral=True  # ✅ 錯誤訊息：私訊
                )
                return

            user_lock = self._get_game_lock(user_id)
            async with user_lock:
                bet = round(bet, 2)
                
                if bet < 1:
                    await ctx.respond(
                        embed=discord.Embed(
                            title="🌸 賭注太低，櫻花都不想飄～ 🌸",
                            description="賭注必須大於 1 幽靈幣哦～",
                            color=discord.Color.red()
                        ).set_footer(text="冥界櫻花只與認真舞者共舞"),
                        ephemeral=True  # ✅ 錯誤訊息：私訊
                    )
                    return

                # 檢查是否有進行中的遊戲
                if (data_manager.blackjack_data.get(guild_id, {}).get(user_id, {}).get("game_status") == "ongoing"):
                    await ctx.respond(embed=discord.Embed(
                        title="🌸 靈魂還在跳舞！🌸",
                        description="你已經在進行一場櫻花舞了，請先完成再開新舞～",
                        color=discord.Color.red()
                    ).set_footer(text="舞終花謝，才能再邀幽幽子"), ephemeral=True)  # ✅ 錯誤訊息：私訊
                    return

                if bet <= 0:
                    # 確保結構存在
                    if guild_id not in data_manager.invalid_bet_count:
                        data_manager.invalid_bet_count[guild_id] = {}
                    invalid_count_guild = data_manager.invalid_bet_count[guild_id]
                    invalid_count_guild[user_id] = invalid_count_guild.get(user_id, 0) + 1
                    data_manager.save_all()

                    if data_manager.invalid_bet_count[guild_id][user_id] >= 2:
                        # 確保結構存在
                        if guild_id in data_manager.balance and user_id in data_manager.balance[guild_id]:
                            del data_manager.balance[guild_id][user_id]
                        if guild_id in data_manager.invalid_bet_count and user_id in data_manager.invalid_bet_count[guild_id]:
                            del data_manager.invalid_bet_count[guild_id][user_id]
                        data_manager.save_all()
                        await ctx.respond(embed=discord.Embed(
                            title="🌸 靈魂的代價～ 🌸",
                            description="多次用無效賭注欺騙幽幽子，幽靈幣已被櫻花吹散～",
                            color=discord.Color.red()
                        ).set_footer(text="誠實才能與幽幽子共舞"), ephemeral=True)  # ✅ 錯誤訊息：私訊
                        return

                    await ctx.respond(embed=discord.Embed(
                        title="🌸 無效的櫻花賭注 🌸",
                        description="賭注必須大於 0 幽靈幣，櫻花不收空靈魂～",
                        color=discord.Color.red()
                    ).set_footer(text="誠實遊玩，櫻花才會盛開"), ephemeral=True)  # ✅ 錯誤訊息：私訊
                    return

                # === 關鍵修復：確保餘額結構存在 ===
                if guild_id not in data_manager.balance:
                    data_manager.balance[guild_id] = {}
                user_balance = round(data_manager.balance[guild_id].get(user_id, 0), 2)
                # === 結束修復 ===

                if user_balance < bet:
                    await ctx.respond(embed=discord.Embed(
                        title="🌸 幽靈幣不足，櫻花不開～ 🌸",
                        description=f"你的幽靈幣只有 {user_balance:.2f}，無法下注 {bet:.2f} 哦～再去冥界多收集一些吧！",
                        color=discord.Color.red()
                    ).set_footer(text="櫻花園的舞者需要充足靈魂"), ephemeral=True)  # ✅ 錯誤訊息：私訊
                    return

                # 載入配置
                try:
                    config = data_manager._load_yaml(f"{data_manager.config_dir}/config_user.yml")
                except Exception:
                    config = {}

                game = BlackjackGame()
                game.shuffle_deck()
                player_cards, dealer_cards = game.deal_initial_cards()

                # === 關鍵修復：扣除賭注 ===
                data_manager.balance[guild_id][user_id] = user_balance - bet
                # === 結束修復 ===

                is_gambler = config.get(guild_id, {}).get(user_id, {}).get('job') == '賭徒'

                # 初始化遊戲資料
                if guild_id not in data_manager.blackjack_data:
                    data_manager.blackjack_data[guild_id] = {}
                data_manager.blackjack_data[guild_id][user_id] = {
                    "player_cards": player_cards,
                    "dealer_cards": dealer_cards,
                    "bet": bet,
                    "game_status": "ongoing",
                    "double_down_used": False,
                    "is_gambler": is_gambler
                }

                player_total = game.calculate_hand(player_cards)
                if player_total == 21:
                    multiplier = 3.5 if is_gambler else 2.5
                    reward = round(bet * multiplier, 2)
                    # === 關鍵修復：贏錢 ===
                    current_balance = data_manager.balance[guild_id].get(user_id, 0)
                    data_manager.balance[guild_id][user_id] = current_balance + reward
                    # === 結束修復 ===
                    data_manager.blackjack_data[guild_id][user_id]["game_status"] = "ended"
                    data_manager.save_all()

                    # ✅ 黑傑克結果：公開顯示（不加 ephemeral）
                    await ctx.respond(embed=discord.Embed(
                        title="🌸 黑傑克！櫻花魂閃耀！🌸",
                        description=f"你的手牌: {player_cards}\n幽幽子為你獻上 {reward:.2f} 幽靈幣的祝福～\n今晚櫻花舞更盛～",
                        color=discord.Color.gold()
                    ).set_footer(text="恭喜！櫻花灑滿冥界"))
                    return

                embed = discord.Embed(
                    title="🌸 幽幽子的櫻花21點舞開始！🌸",
                    description=(
                        f"你下注了 **{bet:.2f} 幽靈幣**，幽幽子邀你共舞～\n\n"
                        f"你的初始手牌: {player_cards} (總點數: {player_total} {game.progress_bar(player_total)})\n"
                        f"幽幽子的明牌: {dealer_cards[0]}"
                    ),
                    color=discord.Color.from_rgb(255, 182, 193)
                ).set_footer(text="選擇命運吧～櫻花舞只等你來")
                
                # ✅ 遊戲開始：公開顯示（不加 ephemeral）
                view = BlackjackButtons(game, data_manager, guild_id, user_id)
                await ctx.respond(embed=embed, view=view)

        except Exception as e:
            self.logger.error(f"Blackjack command failed: {e}")
            await ctx.respond(embed=discord.Embed(
                title="🌸 冥界櫻花飄散了～ 🌸",
                description="哎呀，櫻花舞出了點小問題，請稍後再來邀幽幽子共舞！",
                color=discord.Color.red()
            ).set_footer(text="如有問題請找冥界管理員"), ephemeral=True)  # ✅ 錯誤訊息：私訊

def setup(bot: discord.Bot):
    bot.add_cog(Blackjack(bot))
    
