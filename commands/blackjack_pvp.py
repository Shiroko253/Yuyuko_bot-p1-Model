def get_player_job(self, guild_id: str, user_id: str) -> str:
        """獲取玩家職業"""
        try:
            config_user = self.data_manager._load_yaml("config/config_user.yml", {})
            return config_user.get(guild_id, {}).get(user_id, {}).get("job", "普通")
        except:
            return "普通"
# Note: 這是 commands/blackjack_pvp.py 文件

import discord
from discord.ext import commands
from discord.commands import Option
import random
import logging
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

logger = logging.getLogger("SakuraBot.commands.blackjack_pvp")

# ✿ 冥界的櫻花下，玩家對決的21點遊戲 ✿

class BlackjackPVPGame:
    """雙人對戰的21點遊戲"""
    
    def __init__(self, player1_id: str, player2_id: str, bet_amount: float):
        self.deck = self.create_deck()
        self.shuffle_deck()
        self.player1_id = player1_id
        self.player2_id = player2_id
        self.bet_amount = bet_amount
        self.actual_bet_p1 = bet_amount  # 實際扣款金額
        self.actual_bet_p2 = bet_amount  # 實際扣款金額
        self.player1_cards = []
        self.player2_cards = []
        self.player1_stand = False
        self.player2_stand = False
        self.game_over = False
        self.winner = None
        
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
    
    def calculate_hand(self, cards):
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
    
    def deal_initial_cards(self):
        self.player1_cards = [self.draw_card(), self.draw_card()]
        self.player2_cards = [self.draw_card(), self.draw_card()]
        return self.player1_cards, self.player2_cards
    
    @staticmethod
    def progress_bar(value: int, max_value: int = 21) -> str:
        filled = int(value / max_value * 10)
        return "🌸" * filled + "⋯" * (10 - filled)


class BlackjackPVPManager:
    """管理所有 PVP 遊戲"""
    
    def __init__(self):
        self.active_games: Dict[str, BlackjackPVPGame] = {}  # guild_id -> game
        self.pending_challenges: Dict[str, dict] = {}  # guild_id -> challenge_data
        self.player_in_game: Dict[str, str] = {}  # user_id -> guild_id
    
    def create_challenge(self, guild_id: str, challenger_id: str, opponent_id: str, bet_amount: float):
        """創建挑戰"""
        key = f"{guild_id}:{challenger_id}:{opponent_id}"
        self.pending_challenges[key] = {
            "guild_id": guild_id,
            "challenger_id": challenger_id,
            "opponent_id": opponent_id,
            "bet_amount": bet_amount,
            "timestamp": datetime.now()
        }
        return key
    
    def accept_challenge(self, key: str) -> Optional[dict]:
        """接受挑戰"""
        return self.pending_challenges.pop(key, None)
    
    def decline_challenge(self, key: str):
        """拒絕挑戰"""
        self.pending_challenges.pop(key, None)
    
    def start_game(self, guild_id: str, player1_id: str, player2_id: str, bet_amount: float):
        """開始遊戲"""
        game = BlackjackPVPGame(player1_id, player2_id, bet_amount)
        self.active_games[guild_id] = game
        self.player_in_game[player1_id] = guild_id
        self.player_in_game[player2_id] = guild_id
        return game
    
    def get_game(self, guild_id: str) -> Optional[BlackjackPVPGame]:
        """獲取遊戲"""
        return self.active_games.get(guild_id)
    
    def end_game(self, guild_id: str):
        """結束遊戲"""
        if guild_id in self.active_games:
            game = self.active_games[guild_id]
            self.player_in_game.pop(game.player1_id, None)
            self.player_in_game.pop(game.player2_id, None)
            del self.active_games[guild_id]
    
    def is_player_in_game(self, user_id: str) -> bool:
        """檢查玩家是否在遊戲中"""
        return user_id in self.player_in_game


# 全局管理器
pvp_manager = BlackjackPVPManager()


class ChallengeView(discord.ui.View):
    """挑戰接受/拒絕介面"""
    
    def __init__(self, cog, challenge_key: str, challenger: discord.Member, opponent: discord.Member, bet_amount: float):
        super().__init__(timeout=60)
        self.cog = cog
        self.challenge_key = challenge_key
        self.challenger = challenger
        self.opponent = opponent
        self.bet_amount = bet_amount
        self.responded = False
    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.opponent.id:
            await interaction.response.send_message("這不是給你的挑戰哦！", ephemeral=True)
            return False
        return True
    
    @discord.ui.button(label="接受挑戰", style=discord.ButtonStyle.success, emoji="⚔️")
    async def accept_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        if self.responded:
            await interaction.response.send_message("挑戰已回應！", ephemeral=True)
            return
        
        self.responded = True
        await interaction.response.defer()
        
        try:
            # 檢查雙方是否都有足夠的餘額
            guild_id = str(interaction.guild.id)
            challenger_id = str(self.challenger.id)
            opponent_id = str(self.opponent.id)
            
            balance = self.cog.data_manager.balance
            challenger_balance = balance.get(guild_id, {}).get(challenger_id, 0.0)
            opponent_balance = balance.get(guild_id, {}).get(opponent_id, 0.0)
            
            # 如果對手餘額不足，提供借貸選項
            if opponent_balance < self.bet_amount:
                shortage = self.bet_amount - opponent_balance
                await self.offer_loan(interaction, shortage)
                return
            
            # 雙方都有足夠餘額，開始遊戲
            await self.start_pvp_game(interaction)
            
        except Exception as e:
            logger.error(f"❌ 接受挑戰失敗: {e}", exc_info=True)
            await interaction.followup.send("❌ 發生錯誤，請稍後再試", ephemeral=True)
    
    async def offer_loan(self, interaction: discord.Interaction, shortage: float):
        """提供借貸選項"""
        guild_id = str(interaction.guild.id)
        opponent_id = str(self.opponent.id)
        
        # 檢查國庫是否有足夠的錢
        server_vault = self.cog.data_manager._load_json("economy/server_vault.json", {})
        vault_total = server_vault.get(guild_id, {}).get("vault", {}).get("total", 0.0)
        
        if vault_total < shortage:
            embed = discord.Embed(
                title="🌸 國庫餘額不足",
                description=f"你的餘額不足 **{shortage:.2f}** 幽靈幣，但國庫也無法提供借貸...",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            self.stop()
            return
        
        # 創建借貸確認視圖
        loan_view = LoanConfirmView(self.cog, self, interaction, shortage)
        
        embed = discord.Embed(
            title="🌸 餘額不足，是否借貸？",
            description=(
                f"你的餘額不足以與 {self.challenger.mention} 對賭！\n\n"
                f"**下注金額：** {self.bet_amount:.2f} 幽靈幣\n"
                f"**你的餘額：** {self.cog.data_manager.balance.get(guild_id, {}).get(opponent_id, 0.0):.2f} 幽靈幣\n"
                f"**需要補齊：** {shortage:.2f} 幽靈幣\n\n"
                f"是否向國庫借款 **{shortage:.2f}** 幽靈幣來參與對戰？"
            ),
            color=discord.Color.orange()
        )
        embed.add_field(
            name="📋 借貸條款",
            value=(
                f"```yaml\n"
                f"借款金額: {shortage:.2f} 幽靈幣\n"
                f"利息率: 10%\n"
                f"需還款: {shortage * 1.1:.2f} 幽靈幣\n"
                f"還款期限: 5 天\n"
                f"```"
            ),
            inline=False
        )
        embed.add_field(
            name="⚠️ 風險提示",
            value="• 借貸後無論輸贏都需償還\n• 逾期未還將利息提升至20%\n• 逾期超過7天將金額×4",
            inline=False
        )
        
        await interaction.followup.send(embed=embed, view=loan_view, ephemeral=True)
    
    async def start_pvp_game(self, interaction: discord.Interaction):
        """開始 PVP 遊戲"""
        guild_id = str(interaction.guild.id)
        challenger_id = str(self.challenger.id)
        opponent_id = str(self.opponent.id)
        
        # 檢查雙方職業
        challenger_job = self.cog.get_player_job(guild_id, challenger_id)
        opponent_job = self.cog.get_player_job(guild_id, opponent_id)
        
        # 計算實際扣款（賭徒職業 ×3）
        challenger_actual_bet = self.bet_amount * 3 if challenger_job == "賭徒" else self.bet_amount
        opponent_actual_bet = self.bet_amount * 3 if opponent_job == "賭徒" else self.bet_amount
        
        # 扣除雙方賭注
        async with self.cog.data_manager.balance_lock:
            balance = self.cog.data_manager.balance
            
            # 檢查餘額是否足夠實際扣款
            if balance.get(guild_id, {}).get(challenger_id, 0.0) < challenger_actual_bet:
                await interaction.followup.send(
                    f"❌ {self.challenger.mention} 餘額不足！需要 **{challenger_actual_bet:.2f}** 幽靈幣",
                    ephemeral=True
                )
                return
            
            if balance.get(guild_id, {}).get(opponent_id, 0.0) < opponent_actual_bet:
                await interaction.followup.send(
                    f"❌ {self.opponent.mention} 餘額不足！需要 **{opponent_actual_bet:.2f}** 幽靈幣",
                    ephemeral=True
                )
                return
            
            balance[guild_id][challenger_id] -= challenger_actual_bet
            balance[guild_id][opponent_id] -= opponent_actual_bet
            self.cog.data_manager.save_all()
        
        # 開始遊戲（儲存實際扣款金額）
        game = pvp_manager.start_game(guild_id, challenger_id, opponent_id, self.bet_amount)
        game.actual_bet_p1 = challenger_actual_bet
        game.actual_bet_p2 = opponent_actual_bet
        game.deal_initial_cards()
        
        # 創建遊戲介面
        game_view = PVPGameView(self.cog, game, guild_id, self.challenger, self.opponent)
        
        embed = self.create_game_embed(game)
        
        # 編輯原始消息，添加通知
        await interaction.edit_original_response(
            content=f"🌸⚔️ **遊戲開始！** {self.challenger.mention} 輪到你操作了！",
            embed=embed,
            view=game_view
        )
        
        self.stop()
        logger.info(f"⚔️ PVP 遊戲開始: {challenger_id} vs {opponent_id}, 表面賭注: {self.bet_amount:.2f}, 實際扣款: {challenger_actual_bet:.2f} / {opponent_actual_bet:.2f}")
    
    def create_game_embed(self, game: BlackjackPVPGame) -> discord.Embed:
        """創建遊戲 embed"""
        p1_total = game.calculate_hand(game.player1_cards)
        p2_total = game.calculate_hand(game.player2_cards)
        
        embed = discord.Embed(
            title="🌸⚔️ Blackjack PVP 對戰開始！",
            description=f"賭注：**{game.bet_amount:.2f}** 幽靈幣\n勝者獨得：**{game.bet_amount * 2:.2f}** 幽靈幣",
            color=discord.Color.purple()
        )
        
        embed.add_field(
            name=f"🎴 {self.challenger.display_name} (當前回合)",
            value=(
                f"**手牌：** {' '.join(game.player1_cards)}\n"
                f"**點數：** {p1_total} {game.progress_bar(p1_total)}"
            ),
            inline=False
        )
        
        embed.add_field(
            name=f"🎴 {self.opponent.display_name}",
            value=(
                f"**手牌：** {' '.join(game.player2_cards)}\n"
                f"**點數：** {p2_total} {game.progress_bar(p2_total)}"
            ),
            inline=False
        )
        
        embed.set_footer(text=f"輪到 {self.challenger.display_name} 操作 · 幽幽子")
        return embed
    
    @discord.ui.button(label="拒絕挑戰", style=discord.ButtonStyle.danger, emoji="❌")
    async def decline_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        if self.responded:
            await interaction.response.send_message("挑戰已回應！", ephemeral=True)
            return
        
        self.responded = True
        pvp_manager.decline_challenge(self.challenge_key)
        
        embed = discord.Embed(
            title="🌸 挑戰已拒絕",
            description=f"{self.opponent.mention} 拒絕了 {self.challenger.mention} 的挑戰",
            color=discord.Color.red()
        )
        
        await interaction.response.edit_message(embed=embed, view=None)
        self.stop()
    
    async def on_timeout(self):
        """超時處理 - 視為拒絕"""
        if not self.responded:
            pvp_manager.decline_challenge(self.challenge_key)
            embed = discord.Embed(
                title="🌸 挑戰已超時",
                description=f"{self.opponent.mention} 未在時限內回應，挑戰已取消",
                color=discord.Color.orange()
            )
            try:
                # 嘗試編輯原消息
                if hasattr(self, 'message') and self.message:
                    await self.message.edit(embed=embed, view=None)
            except:
                pass


class LoanConfirmView(discord.ui.View):
    """借貸確認介面"""
    
    def __init__(self, cog, challenge_view: ChallengeView, interaction: discord.Interaction, loan_amount: float):
        super().__init__(timeout=30)
        self.cog = cog
        self.challenge_view = challenge_view
        self.interaction = interaction
        self.loan_amount = loan_amount
        self.responded = False
    
    @discord.ui.button(label="確認借貸", style=discord.ButtonStyle.success, emoji="💰")
    async def confirm_loan(self, button: discord.ui.Button, interaction: discord.Interaction):
        if self.responded:
            return
        
        self.responded = True
        await interaction.response.defer()
        
        try:
            guild_id = str(interaction.guild.id)
            user_id = str(interaction.user.id)
            
            # 執行借貸
            async with self.cog.data_manager.balance_lock:
                balance = self.cog.data_manager.balance
                personal_bank = self.cog.data_manager._load_json("economy/personal_bank.json", {})
                server_vault = self.cog.data_manager._load_json("economy/server_vault.json", {})
                
                # 從國庫扣款
                server_vault[guild_id]["vault"]["total"] -= self.loan_amount
                
                # 給玩家增加餘額
                if guild_id not in balance:
                    balance[guild_id] = {}
                if user_id not in balance[guild_id]:
                    balance[guild_id][user_id] = 0.0
                balance[guild_id][user_id] += self.loan_amount
                
                # 記錄借貸
                if guild_id not in personal_bank:
                    personal_bank[guild_id] = {}
                if user_id not in personal_bank[guild_id]:
                    personal_bank[guild_id][user_id] = {"balance": 0.0, "loan": None}
                
                tz = ZoneInfo('Asia/Taipei')
                current_time = datetime.now(tz)
                
                loan_data = personal_bank[guild_id][user_id].get("loan")
                if loan_data and not loan_data.get("repaid"):
                    # 累積借貸
                    loan_data["amount"] += self.loan_amount
                    loan_data["last_borrowed_at"] = current_time.isoformat()
                    loan_data["due_date"] = (current_time + timedelta(days=5)).isoformat()
                    loan_data["purpose"] = "blackjack_pvp"
                else:
                    # 新借貸
                    loan_data = {
                        "amount": self.loan_amount,
                        "interest_rate": 0.1,
                        "borrowed_at": current_time.isoformat(),
                        "due_date": (current_time + timedelta(days=5)).isoformat(),
                        "repaid": False,
                        "last_penalty_cycle": 0,
                        "purpose": "blackjack_pvp"
                    }
                
                personal_bank[guild_id][user_id]["loan"] = loan_data
                
                # 保存數據
                self.cog.data_manager._save_json("economy/balance.json", balance)
                self.cog.data_manager._save_json("economy/personal_bank.json", personal_bank)
                self.cog.data_manager._save_json("economy/server_vault.json", server_vault)
            
            # 借貸成功，開始遊戲
            await self.challenge_view.start_pvp_game(self.interaction)
            
            # 通知借貸成功
            embed = discord.Embed(
                title="🌸 借貸成功！",
                description=f"你已借貸 **{self.loan_amount:.2f}** 幽靈幣，遊戲即將開始！",
                color=discord.Color.gold()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            
            logger.info(f"💰 PVP 借貸: {user_id} 借貸 {self.loan_amount:.2f}")
            
        except Exception as e:
            logger.error(f"❌ 借貸失敗: {e}", exc_info=True)
            await interaction.followup.send("❌ 借貸失敗，請稍後再試", ephemeral=True)
        
        self.stop()
    
    @discord.ui.button(label="取消", style=discord.ButtonStyle.danger, emoji="❌")
    async def cancel_loan(self, button: discord.ui.Button, interaction: discord.Interaction):
        if self.responded:
            return
        
        self.responded = True
        
        embed = discord.Embed(
            title="🌸 已取消",
            description="你取消了借貸，挑戰已結束",
            color=discord.Color.red()
        )
        
        await interaction.response.edit_message(embed=embed, view=None)
        self.stop()


class PVPGameView(discord.ui.View):
    """PVP 遊戲介面"""
    
    def __init__(self, cog, game: BlackjackPVPGame, guild_id: str, player1: discord.Member, player2: discord.Member):
        super().__init__(timeout=180)
        self.cog = cog
        self.game = game
        self.guild_id = guild_id
        self.player1 = player1
        self.player2 = player2
        self.current_turn = game.player1_id  # 從玩家1開始
    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        user_id = str(interaction.user.id)
        
        # 檢查是否輪到該玩家
        if user_id != self.current_turn:
            await interaction.response.send_message("還沒輪到你哦！", ephemeral=True)
            return False
        
        # 檢查玩家是否已經 stand
        if user_id == self.game.player1_id and self.game.player1_stand:
            await interaction.response.send_message("你已經停牌了！", ephemeral=True)
            return False
        
        if user_id == self.game.player2_id and self.game.player2_stand:
            await interaction.response.send_message("你已經停牌了！", ephemeral=True)
            return False
        
        return True
    
    def update_turn(self):
        """更新回合"""
        if self.game.player1_stand and self.game.player2_stand:
            return  # 雙方都停牌，不更新回合
        
        if self.current_turn == self.game.player1_id:
            if not self.game.player2_stand:
                self.current_turn = self.game.player2_id
        else:
            if not self.game.player1_stand:
                self.current_turn = self.game.player1_id
    
    async def notify_next_player(self, interaction: discord.Interaction) -> str:
        """通知下一位玩家並返回通知文本"""
        if self.game.game_over:
            return ""
        
        next_player = self.player2 if self.current_turn == self.game.player2_id else self.player1
        current_player = self.player1 if self.current_turn == self.game.player2_id else self.player2
        
        return f"🌸 {current_player.mention} 已完成操作，{next_player.mention} 輪到你了！"
    
    async def check_game_over(self, interaction: discord.Interaction) -> bool:
        """檢查遊戲是否結束"""
        p1_total = self.game.calculate_hand(self.game.player1_cards)
        p2_total = self.game.calculate_hand(self.game.player2_cards)
        
        # 檢查是否有人爆牌
        if p1_total > 21:
            await self.end_game(interaction, self.game.player2_id, "player1_bust")
            return True
        
        if p2_total > 21:
            await self.end_game(interaction, self.game.player1_id, "player2_bust")
            return True
        
        # 檢查雙方是否都停牌
        if self.game.player1_stand and self.game.player2_stand:
            if p1_total > p2_total:
                await self.end_game(interaction, self.game.player1_id, "higher_score")
            elif p2_total > p1_total:
                await self.end_game(interaction, self.game.player2_id, "higher_score")
            else:
                await self.end_game(interaction, None, "tie")
            return True
        
        return False
    
    def get_player_job(self, user_id: str) -> str:
        """獲取玩家職業"""
        try:
            config_user = self.cog.data_manager._load_yaml("config/config_user.yml", {})
            return config_user.get(self.guild_id, {}).get(user_id, {}).get("job", "普通")
        except:
            return "普通"
    
    async def end_game(self, interaction: discord.Interaction, winner_id: Optional[str], reason: str):
        """結束遊戲"""
        self.game.game_over = True
        self.game.winner = winner_id
        
        # 獲取雙方職業
        p1_job = self.get_player_job(self.game.player1_id)
        p2_job = self.get_player_job(self.game.player2_id)
        
        # 結算金錢
        async with self.cog.data_manager.balance_lock:
            balance = self.cog.data_manager.balance
            
            if winner_id:
                winner_job = self.get_player_job(winner_id)
                loser_id = self.game.player2_id if winner_id == self.game.player1_id else self.game.player1_id
                loser_job = self.get_player_job(loser_id)
                
                # 賭徒職業特殊結算（基於實際扣款金額）
                total_pool = self.game.actual_bet_p1 + self.game.actual_bet_p2
                
                if winner_job == "賭徒" and loser_job == "賭徒":
                    # 賭徒 vs 賭徒：拿走整個總池
                    # 各扣 300 → 總池 600 → 勝者拿 600（相當於 ×4 效果）
                    payout = total_pool
                    balance[self.guild_id][winner_id] += payout
                    win_amount = payout
                elif winner_job == "賭徒" and loser_job != "賭徒":
                    # 賭徒擊敗普通職業：拿總池
                    # 賭徒扣 300，普通扣 100 → 總池 400
                    payout = total_pool
                    balance[self.guild_id][winner_id] += payout
                    win_amount = payout
                elif winner_job != "賭徒" and loser_job == "賭徒":
                    # 普通職業擊敗賭徒：總池 + 賭徒下注 ×0.5
                    # 普通扣 100，賭徒扣 300 → 總池 400 + 150 = 550
                    loser_actual_bet = self.game.actual_bet_p2 if loser_id == self.game.player2_id else self.game.actual_bet_p1
                    payout = total_pool + loser_actual_bet * 0.5
                    balance[self.guild_id][winner_id] += payout
                    win_amount = payout
                else:
                    # 普通 vs 普通：正常拿總池
                    payout = total_pool
                    balance[self.guild_id][winner_id] += payout
                    win_amount = payout
                
                self.cog.data_manager.save_all()
            else:
                # 平手：退回各自的實際扣款
                balance[self.guild_id][self.game.player1_id] += self.game.actual_bet_p1
                balance[self.guild_id][self.game.player2_id] += self.game.actual_bet_p2
                win_amount = None
                self.cog.data_manager.save_all()
        
        # 創建結算 embed
        embed = self.create_end_embed(reason, p1_job, p2_job, win_amount if winner_id else None)
        
        # 創建通知文本
        if winner_id == self.game.player1_id:
            result_text = f"🎉 {self.player1.mention} 獲勝！獲得 **{win_amount:.2f}** 幽靈幣"
        elif winner_id == self.game.player2_id:
            result_text = f"🎉 {self.player2.mention} 獲勝！獲得 **{win_amount:.2f}** 幽靈幣"
        else:
            result_text = f"🤝 平手！{self.player1.mention} 和 {self.player2.mention} 各退回 **{self.game.bet_amount:.2f}** 幽靈幣"
        
        # 禁用所有按鈕
        for item in self.children:
            item.disabled = True
        
        try:
            await interaction.edit_original_response(content=result_text, embed=embed, view=self)
        except:
            pass
        
        # 清理遊戲
        pvp_manager.end_game(self.guild_id)
        self.stop()
        
        logger.info(f"🏁 PVP 遊戲結束: {reason}, 勝者: {winner_id}")
    
    def create_end_embed(self, reason: str, p1_job: str, p2_job: str, win_amount: Optional[float]) -> discord.Embed:
        """創建結算 embed"""
        p1_total = self.game.calculate_hand(self.game.player1_cards)
        p2_total = self.game.calculate_hand(self.game.player2_cards)
        
        if reason == "player1_bust":
            title = f"🌸 {self.player2.display_name} 獲勝！"
            description = f"{self.player1.display_name} 爆牌了！"
            color = discord.Color.red()
        elif reason == "player2_bust":
            title = f"🌸 {self.player1.display_name} 獲勝！"
            description = f"{self.player2.display_name} 爆牌了！"
            color = discord.Color.gold()
        elif reason == "higher_score":
            if self.game.winner == self.game.player1_id:
                title = f"🌸 {self.player1.display_name} 獲勝！"
                description = f"點數更高：{p1_total} vs {p2_total}"
                color = discord.Color.gold()
            else:
                title = f"🌸 {self.player2.display_name} 獲勝！"
                description = f"點數更高：{p2_total} vs {p1_total}"
                color = discord.Color.gold()
        elif reason == "timeout":
            if self.game.winner == self.game.player1_id:
                title = f"🌸 {self.player1.display_name} 獲勝！"
                description = f"{self.player2.display_name} 超時棄牌"
                color = discord.Color.gold()
            else:
                title = f"🌸 {self.player2.display_name} 獲勝！"
                description = f"{self.player1.display_name} 超時棄牌"
                color = discord.Color.gold()
        else:  # tie
            title = "🌸 平手！"
            description = f"雙方點數相同：{p1_total}"
            color = discord.Color.blue()
        
        embed = discord.Embed(title=title, description=description, color=color)
        
        p1_display = f"🎰 {self.player1.display_name}" if p1_job == "賭徒" else f"🎴 {self.player1.display_name}"
        p2_display = f"🎰 {self.player2.display_name}" if p2_job == "賭徒" else f"🎴 {self.player2.display_name}"
        
        embed.add_field(
            name=p1_display,
            value=(
                f"**手牌：** {' '.join(self.game.player1_cards)}\n"
                f"**點數：** {p1_total}\n"
                f"**職業：** {p1_job}"
            ),
            inline=False
        )
        
        embed.add_field(
            name=p2_display,
            value=(
                f"**手牌：** {' '.join(self.game.player2_cards)}\n"
                f"**點數：** {p2_total}\n"
                f"**職業：** {p2_job}"
            ),
            inline=False
        )
        
        if self.game.winner:
            winner_job = p1_job if self.game.winner == self.game.player1_id else p2_job
            loser_job = p2_job if self.game.winner == self.game.player1_id else p1_job
            
            reward_text = f"獲得 **{win_amount:.2f}** 幽靈幣"
            
            if winner_job == "賭徒" and loser_job != "賭徒":
                reward_text += "\n🎰 **賭徒加成：** 實際壓注 ×3！"
            elif winner_job != "賭徒" and loser_job == "賭徒":
                reward_text += "\n⚔️ **擊敗賭徒：** 額外獲得賭徒壓注的一半！"
            elif winner_job == "賭徒" and loser_job == "賭徒":
                reward_text += "\n🎰🔥 **賭徒對決：** 雙方各壓 ×3，勝者通吃！"
            
            embed.add_field(
                name="💰 獎勵",
                value=reward_text,
                inline=False
            )
        else:
            embed.add_field(
                name="💰 退款",
                value=f"雙方各退回 **{self.game.bet_amount:.2f}** 幽靈幣",
                inline=False
            )
        
        embed.set_footer(text="遊戲結束 · 幽幽子")
        return embed
    
    def create_game_embed(self) -> discord.Embed:
        """創建遊戲狀態 embed"""
        p1_total = self.game.calculate_hand(self.game.player1_cards)
        p2_total = self.game.calculate_hand(self.game.player2_cards)
        
        # 獲取雙方職業
        p1_job = self.get_player_job(self.game.player1_id)
        p2_job = self.get_player_job(self.game.player2_id)
        
        # 確定當前玩家
        current_player_name = self.player1.display_name if self.current_turn == self.game.player1_id else self.player2.display_name
        
        embed = discord.Embed(
            title="🌸⚔️ Blackjack PVP 對戰中",
            description=f"當前回合：**{current_player_name}**\n賭注：**{self.game.bet_amount:.2f}** 幽靈幣",
            color=discord.Color.purple()
        )
        
        p1_status = "🛑 已停牌" if self.game.player1_stand else "🎴 進行中"
        p1_icon = "🎰" if p1_job == "賭徒" else "🎴"
        embed.add_field(
            name=f"{p1_status} {p1_icon} {self.player1.display_name} ({p1_job})",
            value=(
                f"**手牌：** {' '.join(self.game.player1_cards)}\n"
                f"**點數：** {p1_total} {self.game.progress_bar(p1_total)}"
            ),
            inline=False
        )
        
        p2_status = "🛑 已停牌" if self.game.player2_stand else "🎴 進行中"
        p2_icon = "🎰" if p2_job == "賭徒" else "🎴"
        embed.add_field(
            name=f"{p2_status} {p2_icon} {self.player2.display_name} ({p2_job})",
            value=(
                f"**手牌：** {' '.join(self.game.player2_cards)}\n"
                f"**點數：** {p2_total} {self.game.progress_bar(p2_total)}"
            ),
            inline=False
        )
        
        # 顯示賭徒職業特殊規則
        if p1_job == "賭徒" or p2_job == "賭徒":
            if p1_job == "賭徒" and p2_job == "賭徒":
                special_rule = "🎰🔥 雙方都是賭徒！各壓 ×3 倍，勝者通吃全部！"
            elif p1_job == "賭徒":
                special_rule = f"🎰 {self.player1.display_name} 是賭徒！實際壓注 ×3"
            else:
                special_rule = f"🎰 {self.player2.display_name} 是賭徒！實際壓注 ×3"
            
            embed.add_field(
                name="⚠️ 特殊規則",
                value=special_rule,
                inline=False
            )
        
        embed.set_footer(text=f"輪到 {current_player_name} 操作 · 幽幽子")
        return embed
    
    @discord.ui.button(label="抽牌 (Hit)", style=discord.ButtonStyle.primary, emoji="🎴")
    async def hit(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.defer()
        
        try:
            user_id = str(interaction.user.id)
            
            # 抽牌
            if user_id == self.game.player1_id:
                self.game.player1_cards.append(self.game.draw_card())
            else:
                self.game.player2_cards.append(self.game.draw_card())
            
            # 檢查遊戲是否結束
            if await self.check_game_over(interaction):
                return
            
            # 更新回合
            self.update_turn()
            
            # 獲取通知文本
            notification = self.notify_next_player(interaction)
            
            # 更新介面
            embed = self.create_game_embed()
            await interaction.edit_original_response(content=notification, embed=embed, view=self)
        
        except Exception as e:
            logger.error(f"❌ Hit 失敗: {e}", exc_info=True)
    
    @discord.ui.button(label="停牌 (Stand)", style=discord.ButtonStyle.danger, emoji="✋")
    async def stand(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.defer()
        
        try:
            user_id = str(interaction.user.id)
            
            # 停牌
            if user_id == self.game.player1_id:
                self.game.player1_stand = True
            else:
                self.game.player2_stand = True
            
            # 檢查遊戲是否結束
            if await self.check_game_over(interaction):
                return
            
            # 更新回合
            self.update_turn()
            
            # 獲取通知文本
            notification = self.notify_next_player(interaction)
            
            # 更新介面
            embed = self.create_game_embed()
            await interaction.edit_original_response(content=notification, embed=embed, view=self)
        
        except Exception as e:
            logger.error(f"❌ Stand 失敗: {e}", exc_info=True)
    
    async def on_timeout(self):
        """超時處理 - 視為當前玩家棄牌"""
        if not self.game.game_over:
            # 確定超時的玩家
            if self.current_turn == self.game.player1_id:
                winner_id = self.game.player2_id
            else:
                winner_id = self.game.player1_id
            
            # 創建一個假的 interaction 用於結算
            class FakeInteraction:
                async def edit_original_response(self, **kwargs):
                    pass
            
            fake_interaction = FakeInteraction()
            await self.end_game(fake_interaction, winner_id, "timeout")


class BlackjackPVP(commands.Cog):
    """Blackjack PVP 對戰系統"""
    
    def __init__(self, bot: discord.Bot):
        self.bot = bot
        self.data_manager = bot.data_manager
    
    @discord.slash_command(
        name="blackjack_pvp",
        description="🌸⚔️ 向其他玩家發起 Blackjack 對戰挑戰"
    )
    async def blackjack_pvp(
        self,
        ctx: discord.ApplicationContext,
        opponent: discord.Member = Option(discord.Member, "挑戰對象"),
        bet: float = Option(float, "下注金額 (幽靈幣)", min_value=1.0)
    ):
        try:
            guild_id = str(ctx.guild.id)
            challenger_id = str(ctx.author.id)
            opponent_id = str(opponent.id)
            bet = round(bet, 2)
            
            # 檢查是否挑戰自己
            if ctx.author.id == opponent.id:
                await ctx.respond(
                    embed=discord.Embed(
                        title="❌ 無法挑戰自己",
                        description="你不能和自己對戰哦！",
                        color=discord.Color.red()
                    ),
                    ephemeral=True
                )
                return
            
            # 檢查對手是否為機器人
            if opponent.bot:
                await ctx.respond(
                    embed=discord.Embed(
                        title="❌ 無法挑戰機器人",
                        description="機器人無法參與 PVP 對戰！",
                        color=discord.Color.red()
                    ),
                    ephemeral=True
                )
                return
            
            # 檢查雙方是否在遊戲中
            if pvp_manager.is_player_in_game(challenger_id):
                await ctx.respond(
                    embed=discord.Embed(
                        title="❌ 你已在遊戲中",
                        description="請先完成當前的遊戲！",
                        color=discord.Color.red()
                    ),
                    ephemeral=True
                )
                return
            
            if pvp_manager.is_player_in_game(opponent_id):
                await ctx.respond(
                    embed=discord.Embed(
                        title="❌ 對手已在遊戲中",
                        description=f"{opponent.mention} 正在進行其他遊戲！",
                        color=discord.Color.red()
                    ),
                    ephemeral=True
                )
                return
            
            # 檢查挑戰者餘額
            balance = self.data_manager.balance
            challenger_balance = balance.get(guild_id, {}).get(challenger_id, 0.0)
            
            if challenger_balance < bet:
                await ctx.respond(
                    embed=discord.Embed(
                        title="🌸 餘額不足",
                        description=f"你的餘額只有 **{challenger_balance:.2f}** 幽靈幣，無法下注 **{bet:.2f}** 幽靈幣",
                        color=discord.Color.red()
                    ),
                    ephemeral=True
                )
                return
            
            # 創建挑戰
            challenge_key = pvp_manager.create_challenge(guild_id, challenger_id, opponent_id, bet)
            
            # 創建挑戰視圖
            view = ChallengeView(self, challenge_key, ctx.author, opponent, bet)
            
            embed = discord.Embed(
                title="🌸⚔️ Blackjack PVP 挑戰！",
                description=(
                    f"{ctx.author.mention} 向 {opponent.mention} 發起挑戰！\n\n"
                    f"**賭注：** {bet:.2f} 幽靈幣\n"
                    f"**勝者獲得：** {bet * 2:.2f} 幽靈幣（基礎）"
                ),
                color=discord.Color.purple()
            )
            embed.add_field(
                name="⚔️ 規則",
                value=(
                    "• 雙方輪流操作抽牌或停牌\n"
                    "• 超過21點立即判負\n"
                    "• 雙方停牌後比較點數\n"
                    "• 點數高者獲勝\n"
                    "• 平手退回賭注\n"
                    "• 超時視為棄牌判負"
                ),
                inline=False
            )
            
            # 檢查雙方職業，顯示特殊規則
            try:
                config_user = self.data_manager._load_yaml("config/config_user.yml", {})
                challenger_job = config_user.get(guild_id, {}).get(challenger_id, {}).get("job", "普通")
                opponent_job = config_user.get(guild_id, {}).get(opponent_id, {}).get("job", "普通")
                
                if challenger_job == "賭徒" or opponent_job == "賭徒":
                    special_rules = []
                    
                    if challenger_job == "賭徒" and opponent_job == "賭徒":
                        special_rules.append("🎰🔥 **賭徒 vs 賭徒：超高風險對決！**")
                        special_rules.append(f"雙方實際壓注 **{bet * 3:.2f}** 幽靈幣（×3）")
                        special_rules.append(f"勝者通吃 **{bet * 6:.2f}** 幽靈幣（總池）")
                        special_rules.append("⚠️ 這是真正的賭徒對決，勝者拿回 ×2！")
                    else:
                        if challenger_job == "賭徒":
                            special_rules.append(f"🎰 {ctx.author.display_name} 是賭徒！實際壓注 ×3")
                        if opponent_job == "賭徒":
                            special_rules.append(f"🎰 {opponent.display_name} 是賭徒！實際壓注 ×3")
                        
                        special_rules.append("⚔️ 擊敗賭徒可獲得額外獎勵！")
                    
                    embed.add_field(
                        name="🎰 賭徒職業特殊規則",
                        value="\n".join(special_rules),
                        inline=False
                    )
            except:
                pass
            
            embed.set_footer(text=f"{opponent.display_name} 請選擇接受或拒絕 · 60秒內回應")
            
            await ctx.respond(content=f"{opponent.mention} 你收到了一個 Blackjack PVP 挑戰！", embed=embed, view=view)
            
            logger.info(f"⚔️ PVP 挑戰: {challenger_id} -> {opponent_id}, 賭注: {bet:.2f}")
        
        except Exception as e:
            logger.error(f"❌ PVP 挑戰失敗: {e}", exc_info=True)
            await ctx.respond("❌ 發生錯誤，請稍後再試", ephemeral=True)


def setup(bot: discord.Bot):
    bot.add_cog(BlackjackPVP(bot))
    logger.info("🌸⚔️ Blackjack PVP 系統已載入")
