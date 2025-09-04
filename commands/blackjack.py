import discord
from discord.ext import commands
import random
import logging
from typing import List, Tuple, Any

# ✿ 冥界的櫻花下，幽幽子的21點遊戲 ✿
class BlackjackGame:
    """
    幽幽子為你準備的21點遊戲，櫻花下的靈魂也要歡樂一番～
    """

    def __init__(self):
        # 櫻花牌堆
        self.deck: List[str] = self.create_deck()
        self.player_cards: List[str] = []
        self.dealer_cards: List[str] = []

    def create_deck(self) -> List[str]:
        # 櫻花的花語，四種花色
        suits = ["♠", "♥", "♣", "♦"]
        ranks = [2, 3, 4, 5, 6, 7, 8, 9, 10, "J", "Q", "K", "A"]
        return [f"{rank}{suit}" for suit in suits for rank in ranks]

    def shuffle_deck(self) -> None:
        # 幽幽子輕輕搖晃靈魂，把牌洗亂
        random.shuffle(self.deck)

    def draw_card(self) -> str:
        # 櫻花飄落，抽出一張命運之牌
        if not self.deck:
            self.deck = self.create_deck()
            self.shuffle_deck()
        return self.deck.pop()

    def deal_initial_cards(self) -> Tuple[List[str], List[str]]:
        # 初始發牌，靈魂的起舞
        self.player_cards = [self.draw_card(), self.draw_card()]
        self.dealer_cards = [self.draw_card(), self.draw_card()]
        return self.player_cards, self.dealer_cards

    def calculate_hand(self, cards: List[str]) -> int:
        # 計算手牌點數，冥界也有數學
        value, aces = 0, 0
        for card in cards:
            rank = card[:-1]
            if rank in ["J", "Q", "K"]:
                value += 10
            elif rank == "A":
                aces += 1
                value += 11
            else:
                value += int(rank)
        while value > 21 and aces:
            value -= 10
            aces -= 1
        return value

    def dealer_play(self) -> int:
        # 幽幽子自己抽牌，直到17點
        while self.calculate_hand(self.dealer_cards) < 17:
            self.dealer_cards.append(self.draw_card())
        return self.calculate_hand(self.dealer_cards)

    def settle_game(self, player_cards: List[str], dealer_cards: List[str], bet: float, is_gambler: bool) -> Tuple[str, float]:
        # 靈魂的勝負結算
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
        # 櫻花進度條，代表靈魂的力量
        filled = int(value / max_value * 10)
        return "🌸" * filled + "⋯" * (10 - filled)

# ✿ 幽幽子親自遞給你的按鈕，讓你選擇命運 ✿
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
            game_data = self.data_manager.blackjack_data.get(self.guild_id, {}).get(self.user_id, {})
            if game_data and game_data.get("game_status") == "ongoing":
                bet = game_data["bet"]
                self.data_manager.balance[self.guild_id][self.user_id] += bet
                self.data_manager.blackjack_data[self.guild_id][self.user_id]["game_status"] = "ended"
                self.data_manager.save_all()
                if self.message:
                    await self.message.edit(
                        embed=discord.Embed(
                            title="🌸 遊戲超時，幽幽子靈魂小憩～",
                            description=f"時間悄然流逝，幽幽子已收起櫻花。退還你的賭注 {bet:.2f} 幽靈幣，下次再來一起賞花吧！",
                            color=discord.Color.blue()
                        ).set_footer(text="如需再跳舞，請重新開始一局～"),
                        view=None
                    )
        except Exception as e:
            logging.exception(f"Timeout interaction failed: {e}")

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if str(interaction.user.id) != self.user_id:
            await interaction.response.send_message("這不是你的靈魂之舞喲～", ephemeral=True)
            return False
        return True

    async def auto_settle(self, interaction: discord.Interaction) -> bool:
        game_data = self.data_manager.blackjack_data[self.guild_id][self.user_id]
        player_cards = game_data["player_cards"]
        player_total = self.game.calculate_hand(player_cards)
        if player_total == 21:
            bet = game_data["bet"]
            is_gambler = game_data["is_gambler"]
            multiplier = 3.5 if is_gambler else 2.5
            reward = round(bet * multiplier, 2)
            self.data_manager.balance[self.guild_id][self.user_id] += reward
            self.data_manager.blackjack_data[self.guild_id][self.user_id]["game_status"] = "ended"
            self.data_manager.save_all()
            for child in self.children:
                child.disabled = True
            await interaction.edit_original_response(embed=discord.Embed(
                title="🌸 黑傑克！櫻花下靈魂舞勝利！🌸",
                description=f"你的手牌: {player_cards}\n幽幽子為你獻上 {reward:.2f} 幽靈幣的祝福～\n櫻花飄落，靈魂閃耀～",
                color=discord.Color.gold()
            ).set_footer(text="恭喜你，靈魂閃爍！"), view=None)
            return True
        return False

    @discord.ui.button(label="抽牌 (Hit)", style=discord.ButtonStyle.primary)
    async def hit(self, button: discord.ui.Button, interaction: discord.Interaction):
        try:
            await interaction.response.defer()
            game_data = self.data_manager.blackjack_data[self.guild_id][self.user_id]
            player_cards = game_data["player_cards"]
            player_cards.append(self.game.draw_card())
            player_total = self.game.calculate_hand(player_cards)
            game_data["player_cards"] = player_cards

            if player_total > 21:
                game_data["game_status"] = "ended"
                self.data_manager.save_all()
                for child in self.children:
                    child.disabled = True
                await interaction.edit_original_response(embed=discord.Embed(
                    title="🌸 哎呀，櫻花散盡，靈魂爆掉了！🌸",
                    description=f"你的手牌: {player_cards}\n點數總計: {player_total}\n下次再來跟幽幽子共舞吧～",
                    color=discord.Color.red()
                ).set_footer(text="遊戲結束，冥界等待著你～"), view=None)
                return

            if await self.auto_settle(interaction):
                return

            await interaction.edit_original_response(embed=discord.Embed(
                title="🌸 幽幽子為你送上新櫻花一片！🌸",
                description=f"你的手牌: {player_cards}\n目前點數: {player_total} {self.game.progress_bar(player_total)}",
                color=discord.Color.from_rgb(255, 182, 193)
            ).set_footer(text="要繼續舞動，還是收手？"), view=self)
        except Exception as e:
            logging.exception(f"Hit interaction failed: {e}")
            await interaction.followup.send("遊戲的櫻花散落了，請重新開始跟幽幽子共舞一局！", ephemeral=True)

    @discord.ui.button(label="停牌 (Stand)", style=discord.ButtonStyle.danger)
    async def stand(self, button: discord.ui.Button, interaction: discord.Interaction):
        try:
            await interaction.response.defer()
            game_data = self.data_manager.blackjack_data[self.guild_id][self.user_id]
            player_cards = game_data["player_cards"]
            dealer_cards = game_data["dealer_cards"]
            bet = game_data["bet"]
            is_gambler = game_data["is_gambler"]

            game_data["game_status"] = "ended"
            dealer_total = self.game.dealer_play()
            result, reward = self.game.settle_game(player_cards, dealer_cards, bet, is_gambler)
            self.data_manager.balance[self.guild_id][self.user_id] += reward
            self.data_manager.save_all()

            for child in self.children:
                child.disabled = True
            embed = discord.Embed(
                title="🌸 靈魂之舞勝利！🌸" if result == "win" else "🌸 櫻花平衡，靈魂平手～🌸" if result == "tie" else "🌸 冥界勝利，幽幽子守護～🌸",
                description=f"你的手牌: {player_cards}\n幽幽子的手牌: {dealer_cards}\n{'你贏得了' if result == 'win' else '退還賭注' if result == 'tie' else '下次再來賞櫻吧～'} {reward:.2f} 幽靈幣",
                color=discord.Color.gold() if result == "win" else discord.Color.from_rgb(255, 182, 193) if result == "tie" else discord.Color.red()
            ).set_footer(text="遊戲結束，櫻花依舊飄落～")
            await interaction.edit_original_response(embed=embed, view=None)
        except Exception as e:
            logging.exception(f"Stand interaction failed: {e}")
            await interaction.followup.send("櫻花舞失效了，請重新邀幽幽子共舞一局！", ephemeral=True)

    @discord.ui.button(label="雙倍下注 (Double Down)", style=discord.ButtonStyle.success)
    async def double_down(self, button: discord.ui.Button, interaction: discord.Interaction):
        try:
            await interaction.response.defer()
            game_data = self.data_manager.blackjack_data[self.guild_id][self.user_id]
            if game_data["double_down_used"]:
                await interaction.edit_original_response(embed=discord.Embed(
                    title="🌸 命運只能挑戰一次！🌸",
                    description="你已經用過雙倍下注了哦～幽幽子的櫻花只能為你加持一次！",
                    color=discord.Color.red()
                ).set_footer(text="每局只能一次櫻花加持"), view=self)
                return

            bet = game_data["bet"]
            is_gambler = game_data["is_gambler"]
            user_balance = self.data_manager.balance[self.guild_id][self.user_id]
            doubled_bet = bet * 2

            if user_balance < bet:
                await interaction.edit_original_response(embed=discord.Embed(
                    title="🌸 櫻花能量不足～ 🌸",
                    description=f"你的幽靈幣只有 {user_balance:.2f}，不足以挑戰雙倍 {doubled_bet:.2f} 哦～",
                    color=discord.Color.red()
                ).set_footer(text="去冥界多收集一點幽靈幣吧"), view=self)
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
            self.data_manager.save_all()

            embed = discord.Embed(
                title="🌸 櫻花雙倍加持，命運之舞！🌸",
                description=f"你的手牌: {player_cards} (總點數: {player_total} {self.game.progress_bar(player_total)})\n賭注翻倍為 {doubled_bet:.2f} 幽靈幣",
                color=discord.Color.gold()
            )

            if player_total > 21:
                embed.title = "🌸 哎呀，靈魂爆掉了！🌸"
                embed.description = f"你的手牌: {player_cards}\n總點數: {player_total}\n下次再來賞櫻跳舞吧～"
                embed.color = discord.Color.red()
                for child in self.children:
                    child.disabled = True
                await interaction.edit_original_response(embed=embed.set_footer(text="遊戲結束，櫻花謝了～"), view=None)
                return

            dealer_total = self.game.dealer_play()
            result, reward = self.game.settle_game(player_cards, dealer_cards, doubled_bet, is_gambler)
            self.data_manager.balance[self.guild_id][self.user_id] += reward
            self.data_manager.save_all()

            for child in self.children:
                child.disabled = True
            embed.title = "🌸 櫻花舞勝利！🌸" if result == "win" else "🌸 靈魂平衡～🌸" if result == "tie" else "🌸 冥界勝利，幽幽子守護～🌸"
            embed.description = f"你的手牌: {player_cards}\n幽幽子的手牌: {dealer_cards}\n{'你贏得了' if result == 'win' else '退還賭注' if result == 'tie' else '下次再來共舞吧～'} {reward:.2f} 幽靈幣"
            embed.color = discord.Color.gold() if result == "win" else discord.Color.from_rgb(255, 182, 193) if result == "tie" else discord.Color.red()
            await interaction.edit_original_response(embed=embed.set_footer(text="遊戲結束，櫻花依舊飄落～"), view=None)
        except Exception as e:
            logging.exception(f"Double down interaction failed: {e}")
            await interaction.followup.send("櫻花舞失效了，請重新邀幽幽子共舞一局！", ephemeral=True)

# ✿ 幽幽子邀你來冥界櫻花園共舞21點 ✿
class Blackjack(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @discord.slash_command(
        name="blackjack",
        description="幽幽子邀你在冥界櫻花園共舞一場21點～"
    )
    async def blackjack(self, ctx: discord.ApplicationContext, bet: float):
        try:
            data_manager = self.bot.data_manager
            bet = round(bet, 2)
            user_id = str(ctx.author.id)
            guild_id = str(ctx.guild.id)
            config = data_manager.load_yaml("config/config_user.yml")

            data_manager.balance = data_manager.load_json(f"{data_manager.economy_dir}/balance.json")
            data_manager.blackjack_data = data_manager.load_json(f"{data_manager.config_dir}/blackjack_data.json")

            if bet < 1:
                await ctx.respond(
                    embed=discord.Embed(
                        title="🌸 賭注太低，櫻花都不想飄～ 🌸",
                        description="賭注必須大於 1 幽靈幣哦～",
                        color=discord.Color.red()
                    ).set_footer(text="冥界櫻花只與認真舞者共舞"),
                    ephemeral=True
                )
                return

            if data_manager.blackjack_data.get(guild_id, {}).get(user_id, {}).get("game_status") == "ongoing":
                await ctx.respond(embed=discord.Embed(
                    title="🌸 靈魂還在跳舞！🌸",
                    description="你已經在進行一場櫻花舞了，請先完成再開新舞～",
                    color=discord.Color.red()
                ).set_footer(text="舞終花謝，才能再邀幽幽子"))
                return

            if bet <= 0:
                data_manager.invalid_bet_count.setdefault(guild_id, {}).setdefault(user_id, 0)
                data_manager.invalid_bet_count[guild_id][user_id] += 1
                data_manager.save_all()

                if data_manager.invalid_bet_count[guild_id][user_id] >= 2:
                    data_manager.balance.get(guild_id, {}).pop(user_id, None)
                    data_manager.invalid_bet_count[guild_id].pop(user_id, None)
                    data_manager.save_all()
                    await ctx.respond(embed=discord.Embed(
                        title="🌸 靈魂的代價～ 🌸",
                        description="多次用無效賭注欺騙幽幽子，幽靈幣已被櫻花吹散～",
                        color=discord.Color.red()
                    ).set_footer(text="誠實才能與幽幽子共舞"))
                    return

                await ctx.respond(embed=discord.Embed(
                    title="🌸 無效的櫻花賭注 🌸",
                    description="賭注必須大於 0 幽靈幣，櫻花不收空靈魂～",
                    color=discord.Color.red()
                ).set_footer(text="誠實遊玩，櫻花才會盛開"))
                return

            user_balance = round(data_manager.balance.get(guild_id, {}).get(user_id, 0), 2)
            if user_balance < bet:
                await ctx.respond(embed=discord.Embed(
                    title="🌸 幽靈幣不足，櫻花不開～ 🌸",
                    description=f"你的幽靈幣只有 {user_balance:.2f}，無法下注 {bet:.2f} 哦～再去冥界多收集一些吧！",
                    color=discord.Color.red()
                ).set_footer(text="櫻花園的舞者需要充足靈魂"))
                return

            game = BlackjackGame()
            game.shuffle_deck()
            player_cards, dealer_cards = game.deal_initial_cards()

            data_manager.balance.setdefault(guild_id, {})[user_id] = user_balance - bet
            is_gambler = config.get(guild_id, {}).get(user_id, {}).get('job') == '賭徒'

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
            if player_total == 21:
                multiplier = 3.5 if is_gambler else 2.5
                reward = round(bet * multiplier, 2)
                data_manager.balance[guild_id][user_id] += reward
                data_manager.blackjack_data[guild_id][user_id]["game_status"] = "ended"
                data_manager.save_all()

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
            
            msg = await ctx.respond(embed=embed, view=None)
            view = BlackjackButtons(game, data_manager, guild_id, user_id)
            view.message = await msg.original_response()
            await view.message.edit(view=view)

        except Exception as e:
            logging.exception(f"Blackjack command failed: {e}")
            await ctx.respond(embed=discord.Embed(
                title="🌸 冥界櫻花飄散了～ 🌸",
                description="哎呀，櫻花舞出了點小問題，請稍後再來邀幽幽子共舞！",
                color=discord.Color.red()
            ).set_footer(text="如有問題請找冥界管理員"), ephemeral=True)

def setup(bot: discord.Bot):
    """
    ✿ 幽幽子優雅地將櫻花21點舞功能裝進 bot 裡 ✿
    """
    bot.add_cog(Blackjack(bot))