import discord
from discord.ext import commands
import random
import logging

class BlackjackGame:
    def __init__(self):
        self.deck = self.create_deck()
        self.player_cards = []
        self.dealer_cards = []

    def create_deck(self):
        suits = ["♠", "♥", "♣", "♦"]
        ranks = [2, 3, 4, 5, 6, 7, 8, 9, 10, "J", "Q", "K", "A"]
        return [f"{rank}{suit}" for suit in suits for rank in ranks]

    def shuffle_deck(self):
        random.shuffle(self.deck)

    def draw_card(self):
        if not self.deck:
            self.deck = self.create_deck()
            self.shuffle_deck()
        return self.deck.pop()

    def deal_initial_cards(self):
        self.player_cards = [self.draw_card(), self.draw_card()]
        self.dealer_cards = [self.draw_card(), self.draw_card()]
        return self.player_cards, self.dealer_cards

    def calculate_hand(self, cards):
        value = 0
        aces = 0
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

    def dealer_play(self):
        while self.calculate_hand(self.dealer_cards) < 17:
            self.dealer_cards.append(self.draw_card())
        return self.calculate_hand(self.dealer_cards)

    def settle_game(self, player_cards, dealer_cards, bet, is_gambler):
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
    def progress_bar(value, max_value=21):
        filled = int(value / max_value * 10)
        return "█" * filled + "▒" * (10 - filled)

class BlackjackButtons(discord.ui.View):
    def __init__(self, game, data_manager, interaction, guild_id, user_id):
        super().__init__(timeout=180)
        self.game = game
        self.data_manager = data_manager
        self.interaction = interaction
        self.guild_id = guild_id
        self.user_id = user_id

    async def on_timeout(self):
        try:
            if self.data_manager.blackjack_data[self.guild_id][self.user_id]["game_status"] == "ongoing":
                bet = self.data_manager.blackjack_data[self.guild_id][self.user_id]["bet"]
                self.data_manager.balance[self.guild_id][self.user_id] += bet
                self.data_manager.blackjack_data[self.guild_id][self.user_id]["game_status"] = "ended"
                self.data_manager.save_all()
                await self.interaction.edit_original_response(
                    embed=discord.Embed(
                        title="🌸 遊戲超時，靈魂休息了～🌸",
                        description=f"時間到了，遊戲已結束。退還你的賭注 {bet:.2f} 幽靈幣，下次再來挑戰幽幽子吧！",
                        color=discord.Color.blue()
                    ),
                    view=None
                )
        except discord.errors.HTTPException as e:
            logging.error(f"Timeout interaction failed: {e}")

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != int(self.user_id):
            await interaction.response.send_message("這不是你的遊戲哦～", ephemeral=True)
            return False
        return True

    async def auto_settle(self, interaction):
        player_cards = self.data_manager.blackjack_data[self.guild_id][self.user_id]["player_cards"]
        player_total = self.game.calculate_hand(player_cards)
        if player_total == 21:
            bet = self.data_manager.blackjack_data[self.guild_id][self.user_id]["bet"]
            is_gambler = self.data_manager.blackjack_data[self.guild_id][self.user_id]["is_gambler"]
            multiplier = 3.5 if is_gambler else 2.5
            reward = round(bet * multiplier, 2)
            self.data_manager.balance[self.guild_id][self.user_id] += reward
            self.data_manager.blackjack_data[self.guild_id][self.user_id]["game_status"] = "ended"
            self.data_manager.save_all()

            for child in self.children:
                child.disabled = True
            await interaction.edit_original_response(embed=discord.Embed(
                title="🌸 黑傑克！靈魂的勝利！🌸",
                description=f"你的手牌: {player_cards}\n幽幽子為你獻上 {reward:.2f} 幽靈幣的祝福～",
                color=discord.Color.gold()
            ), view=None)
            return True
        return False

    @discord.ui.button(label="抽牌 (Hit)", style=discord.ButtonStyle.primary)
    async def hit(self, button: discord.ui.Button, interaction: discord.Interaction):
        try:
            await interaction.response.defer()
            player_cards = self.data_manager.blackjack_data[self.guild_id][self.user_id]["player_cards"]
            player_cards.append(self.game.draw_card())
            player_total = self.game.calculate_hand(player_cards)

            self.data_manager.blackjack_data[self.guild_id][self.user_id]["player_cards"] = player_cards
            if player_total > 21:
                self.data_manager.blackjack_data[self.guild_id][self.user_id]["game_status"] = "ended"
                self.data_manager.save_all()
                for child in self.children:
                    child.disabled = True
                await interaction.edit_original_response(embed=discord.Embed(
                    title="🌸 哎呀，靈魂爆掉了！🌸",
                    description=f"你的手牌: {player_cards}\n點數總計: {player_total}\n下次再來挑戰幽幽子吧～",
                    color=discord.Color.red()
                ), view=None)
                return

            if await self.auto_settle(interaction):
                return

            await interaction.edit_original_response(embed=discord.Embed(
                title="🌸 你抽了一張牌！🌸",
                description=f"你的手牌: {player_cards}\n目前點數: {player_total} {self.game.progress_bar(player_total)}",
                color=discord.Color.from_rgb(255, 182, 193)
            ), view=self)
        except discord.errors.HTTPException as e:
            logging.error(f"Hit interaction failed: {e}")
            await interaction.followup.send("遊戲交互已失效，請重新開始一局！", ephemeral=True)

    @discord.ui.button(label="停牌 (Stand)", style=discord.ButtonStyle.danger)
    async def stand(self, button: discord.ui.Button, interaction: discord.Interaction):
        try:
            await interaction.response.defer()
            player_cards = self.data_manager.blackjack_data[self.guild_id][self.user_id]["player_cards"]
            dealer_cards = self.data_manager.blackjack_data[self.guild_id][self.user_id]["dealer_cards"]
            bet = self.data_manager.blackjack_data[self.guild_id][self.user_id]["bet"]
            is_gambler = self.data_manager.blackjack_data[self.guild_id][self.user_id]["is_gambler"]

            self.data_manager.blackjack_data[self.guild_id][self.user_id]["game_status"] = "ended"
            dealer_total = self.game.dealer_play()
            result, reward = self.game.settle_game(player_cards, dealer_cards, bet, is_gambler)
            self.data_manager.balance[self.guild_id][self.user_id] += reward
            self.data_manager.save_all()

            for child in self.children:
                child.disabled = True
            embed = discord.Embed(
                title="🌸 靈魂的勝利！🌸" if result == "win" else "🌸 平手，靈魂的平衡～🌸" if result == "tie" else "🌸 殞念，幽幽子贏了！🌸",
                description=f"你的手牌: {player_cards}\n幽幽子的手牌: {dealer_cards}\n{'你贏得了' if result == 'win' else '退還賭注' if result == 'tie' else '下次再來挑戰吧～'} {reward:.2f} 幽靈幣",
                color=discord.Color.gold() if result == "win" else discord.Color.from_rgb(255, 182, 193) if result == "tie" else discord.Color.red()
            )
            await interaction.edit_original_response(embed=embed, view=None)
        except discord.errors.HTTPException as e:
            logging.error(f"Stand interaction failed: {e}")
            await interaction.followup.send("遊戲交互已失效，請重新開始一局！", ephemeral=True)

    @discord.ui.button(label="雙倍下注 (Double Down)", style=discord.ButtonStyle.success)
    async def double_down(self, button: discord.ui.Button, interaction: discord.Interaction):
        try:
            await interaction.response.defer()
            if self.data_manager.blackjack_data[self.guild_id][self.user_id]["double_down_used"]:
                await interaction.edit_original_response(embed=discord.Embed(
                    title="🌸 無法再次挑戰命運！🌸",
                    description="你已經使用過雙倍下注了哦～",
                    color=discord.Color.red()
                ), view=self)
                return

            bet = self.data_manager.blackjack_data[self.guild_id][self.user_id]["bet"]
            is_gambler = self.data_manager.blackjack_data[self.guild_id][self.user_id]["is_gambler"]
            user_balance = self.data_manager.balance[self.guild_id][self.user_id]
            doubled_bet = bet * 2

            if user_balance < bet:
                await interaction.edit_original_response(embed=discord.Embed(
                    title="🌸 嘻嘻，靈魂不夠喲～ 🌸",
                    description=f"你的幽靈幣只有 {user_balance:.2f}，不足以讓幽幽子給你雙倍下注 {doubled_bet:.2f} 哦～再去收集一些吧！",
                    color=discord.Color.red()
                ), view=self)
                return

            self.data_manager.blackjack_data[self.guild_id][self.user_id]["bet"] = doubled_bet
            self.data_manager.blackjack_data[self.guild_id][self.user_id]["double_down_used"] = True
            self.data_manager.balance[self.guild_id][self.user_id] -= bet
            player_cards = self.data_manager.blackjack_data[self.guild_id][self.user_id]["player_cards"]
            dealer_cards = self.data_manager.blackjack_data[self.guild_id][self.user_id]["dealer_cards"]
            player_cards.append(self.game.draw_card())
            player_total = self.game.calculate_hand(player_cards)

            self.data_manager.blackjack_data[self.guild_id][self.user_id]["player_cards"] = player_cards
            self.data_manager.blackjack_data[self.guild_id][self.user_id]["game_status"] = "ended"
            self.data_manager.save_all()

            embed = discord.Embed(
                title="🌸 雙倍下注，挑戰命運！🌸",
                description=f"你的手牌: {player_cards} (總點數: {player_total} {self.game.progress_bar(player_total)})\n賭注翻倍為 {doubled_bet:.2f} 幽靈幣",
                color=discord.Color.gold()
            )

            if player_total > 21:
                embed.title = "🌸 哎呀，靈魂爆掉了！🌸"
                embed.description = f"你的手牌: {player_cards}\n總點數: {player_total}\n下次再來挑戰幽幽子吧～"
                embed.color = discord.Color.red()
                for child in self.children:
                    child.disabled = True
                await interaction.edit_original_response(embed=embed, view=None)
                return

            dealer_total = self.game.dealer_play()
            result, reward = self.game.settle_game(player_cards, dealer_cards, doubled_bet, is_gambler)
            self.data_manager.balance[self.guild_id][self.user_id] += reward
            self.data_manager.save_all()

            for child in self.children:
                child.disabled = True
            embed.title = "🌸 靈魂的勝利！🌸" if result == "win" else "🌸 平手，靈魂的平衡～🌸" if result == "tie" else "🌸 殞念，幽幽子贏了！🌸"
            embed.description = f"你的手牌: {player_cards}\n幽幽子的手牌: {dealer_cards}\n{'你贏得了' if result == 'win' else '退還賭注' if result == 'tie' else '下次再來挑戰吧～'} {reward:.2f} 幽靈幣"
            embed.color = discord.Color.gold() if result == "win" else discord.Color.from_rgb(255, 182, 193) if result == "tie" else discord.Color.red()
            await interaction.edit_original_response(embed=embed, view=None)
        except discord.errors.HTTPException as e:
            logging.error(f"Double down interaction failed: {e}")
            await interaction.followup.send("遊戲交互已失效，請重新開始一局！", ephemeral=True)

class Blackjack(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="blackjack", description="幽幽子與你共舞一場21點遊戲～")
    async def blackjack(self, ctx: discord.ApplicationContext, bet: float):
        try:
            data_manager = self.bot.data_manager
            bet = round(bet, 2)
            user_id = str(ctx.author.id)
            guild_id = str(ctx.guild.id)
            config = data_manager.load_yaml("config/config_user.yml")

            # 檢查是否有正在進行的遊戲
            if data_manager.blackjack_data.get(guild_id, {}).get(user_id, {}).get("game_status") == "ongoing":
                await ctx.respond(embed=discord.Embed(
                    title="🌸 靈魂尚未休息！🌸",
                    description="你已經在進行一局遊戲了，請先完成當前遊戲！",
                    color=discord.Color.red()
                ))
                return

            # 檢查無效賭注
            if bet <= 0:
                data_manager.invalid_bet_count.setdefault(guild_id, {}).setdefault(user_id, 0)
                data_manager.invalid_bet_count[guild_id][user_id] += 1
                data_manager.save_all()

                if data_manager.invalid_bet_count[guild_id][user_id] >= 2:
                    data_manager.balance.get(guild_id, {}).pop(user_id, None)
                    data_manager.invalid_bet_count[guild_id].pop(user_id, None)
                    data_manager.save_all()
                    await ctx.respond(embed=discord.Embed(
                        title="🌸 靈魂的代價 🌸",
                        description="哎呀～你多次試圖用無效的賭注欺騙幽幽子，你的幽靈幣已被清空了哦！",
                        color=discord.Color.red()
                    ))
                    return

                await ctx.respond(embed=discord.Embed(
                    title="🌸 無效的賭注 🌸",
                    description="嘻嘻，賭注必須大於 0 哦～別想騙過幽幽子的眼睛！",
                    color=discord.Color.red()
                ))
                return

            # 檢查餘額
            user_balance = round(data_manager.balance.get(guild_id, {}).get(user_id, 0), 2)
            if user_balance < bet:
                await ctx.respond(embed=discord.Embed(
                    title="🌸 幽靈幣不足 🌸",
                    description=f"你的幽靈幣只有 {user_balance:.2f}，無法下注 {bet:.2f} 哦～再去收集一些吧！",
                    color=discord.Color.red()
                ))
                return

            # 初始化遊戲
            game = BlackjackGame()
            game.shuffle_deck()
            player_cards, dealer_cards = game.deal_initial_cards()

            data_manager.balance.setdefault(guild_id, {})[user_id] = user_balance - bet
            is_gambler = config.get(guild_id, {}).get(user_id, {}).get('job') == '賭徒'

            data_manager.blackjack_data.setdefault(guild_id, {})[user_id] = {
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
                data_manager.balance[guild_id][user_id] += reward
                data_manager.blackjack_data[guild_id][user_id]["game_status"] = "ended"
                data_manager.save_all()

                await ctx.respond(embed=discord.Embed(
                    title="🌸 黑傑克！靈魂的勝利！🌸",
                    description=f"你的手牌: {player_cards}\n幽幽子為你獻上 {reward:.2f} 幽靈幣的祝福～",
                    color=discord.Color.gold()
                ))
                return

            embed = discord.Embed(
                title="🌸 幽幽子的21點遊戲開始！🌸",
                description=(
                    f"你下注了 **{bet:.2f} 幽靈幣**，讓我們共舞一場吧～\n\n"
                    f"你的初始手牌: {player_cards} (總點數: {player_total} {game.progress_bar(player_total)})\n"
                    f"幽幽子的明牌: {dealer_cards[0]}"
                ),
                color=discord.Color.from_rgb(255, 182, 193)
            )
            embed.set_footer(text="選擇你的命運吧～")

            interaction = await ctx.respond(embed=embed)
            view = BlackjackButtons(game, data_manager, interaction, guild_id, user_id)
            await interaction.edit_original_response(view=view)

        except Exception as e:
            logging.error(f"Blackjack command failed: {e}")
            await ctx.respond(embed=discord.Embed(
                title="🌸 靈魂飄散了！🌸",
                description="哎呀，遊戲出了點問題，請稍後再試！",
                color=discord.Color.red()
            ), ephemeral=True)

def setup(bot):
    bot.add_cog(Blackjack(bot))