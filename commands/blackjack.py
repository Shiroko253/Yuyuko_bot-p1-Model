import discord
from discord.ext import commands
import random
import logging
from typing import List

logger = logging.getLogger("SakuraBot.commands.blackjack")


class BlackjackGame:
    def __init__(self):
        self.deck: List[str] = self.create_deck()
        self.player_cards: List[str] = []
        self.dealer_cards: List[str] = []

    def create_deck(self):
        suits = ["♠","♥","♣","♦"]
        ranks = [2,3,4,5,6,7,8,9,10,"J","Q","K","A"]
        return [f"{r}{s}" for s in suits for r in ranks]

    def shuffle_deck(self):
        random.shuffle(self.deck)

    def draw_card(self):
        if not self.deck:
            self.deck = self.create_deck(); self.shuffle_deck()
        return self.deck.pop()

    def deal_initial_cards(self):
        self.player_cards = [self.draw_card(), self.draw_card()]
        self.dealer_cards = [self.draw_card(), self.draw_card()]
        return self.player_cards, self.dealer_cards

    def calculate_hand(self, cards):
        value, aces = 0, 0
        for card in cards:
            rank = card[:-1]
            if rank in ["J","Q","K"]: value += 10
            elif rank == "A": aces += 1; value += 11
            else: value += int(rank)
        while value > 21 and aces:
            value -= 10; aces -= 1
        return value

    def dealer_play(self):
        while self.calculate_hand(self.dealer_cards) < 17:
            self.dealer_cards.append(self.draw_card())
        return self.calculate_hand(self.dealer_cards)

    def settle_game(self, player_cards, dealer_cards, bet, is_gambler):
        pt = self.calculate_hand(player_cards)
        dt = self.calculate_hand(dealer_cards)
        m = 3 if is_gambler else 2
        if dt > 21 or pt > dt: return "win", round(bet * m, 2)
        elif pt == dt: return "tie", bet
        else: return "lose", 0

    @staticmethod
    def progress_bar(value, max_value=21):
        filled = int(value / max_value * 10)
        return "🌸" * filled + "⋯" * (10 - filled)


class BlackjackButtons(discord.ui.View):
    def __init__(self, game, data_manager, guild_id, user_id):
        super().__init__(timeout=180)
        self.game = game
        self.data_manager = data_manager
        self.guild_id = str(guild_id)
        self.user_id = str(user_id)
        self.message = None

    async def on_timeout(self):
        try:
            bet = None
            async with self.data_manager.balance_lock:
                gd = self.data_manager.blackjack_data.get(self.guild_id,{}).get(self.user_id,{})
                if gd and gd.get("game_status") == "ongoing":
                    bet = gd["bet"]
                    self.data_manager.balance[self.guild_id][self.user_id] += bet
                    self.data_manager.blackjack_data[self.guild_id][self.user_id]["game_status"] = "ended"
            if bet is not None:
                await self.data_manager.save_all_async()
                if self.message:
                    await self.message.edit(embed=discord.Embed(
                        title="🌸 遊戲超時，幽幽子靈魂小憩～",
                        description=f"退還你的賭注 **{bet:.2f}** 幽靈幣，下次再來一起賞花吧！",
                        color=discord.Color.blue()
                    ).set_footer(text="如需再跳舞，請重新開始一局～"), view=None)
        except Exception as e:
            logger.exception(f"Timeout 處理失敗: {e}")

    async def interaction_check(self, interaction):
        if str(interaction.user.id) != self.user_id:
            await interaction.response.send_message("這不是你的靈魂之舞喲～", ephemeral=True)
            return False
        return True

    async def auto_settle(self, interaction, player_cards, bet, is_gambler):
        pt = self.game.calculate_hand(player_cards)
        if pt != 21:
            return False
        m = 3.5 if is_gambler else 2.5
        reward = round(bet * m, 2)
        async with self.data_manager.balance_lock:
            self.data_manager.balance[self.guild_id][self.user_id] += reward
            self.data_manager.blackjack_data[self.guild_id][self.user_id]["game_status"] = "ended"
        await self.data_manager.save_all_async()
        for c in self.children: c.disabled = True
        await interaction.edit_original_response(embed=discord.Embed(
            title="🌸 黑傑克！櫻花下靈魂舞勝利！🌸",
            description=f"**你的手牌:** {' '.join(player_cards)}\n**總點數:** 21 點\n\n幽幽子為你獻上 **{reward:.2f}** 幽靈幣的祝福～",
            color=discord.Color.gold()
        ).set_footer(text="恭喜你，靈魂閃爍！"), view=None)
        logger.info(f"{self.user_id} Blackjack, 贏得 {reward:.2f}")
        return True

    @discord.ui.button(label="抽牌 (Hit)", style=discord.ButtonStyle.primary, emoji="🎴")
    async def hit(self, button, interaction):
        try:
            await interaction.response.defer()
            async with self.data_manager.balance_lock:
                gd = self.data_manager.blackjack_data[self.guild_id][self.user_id]
                pc = gd["player_cards"]
                pc.append(self.game.draw_card())
                pt = self.game.calculate_hand(pc)
                gd["player_cards"] = pc
                bet = gd["bet"]; is_gambler = gd["is_gambler"]
                if pt > 21: gd["game_status"] = "ended"
            
            # 鎖釋放後才執行 I/O
            if pt > 21:
                await self.data_manager.save_all_async()
                for c in self.children: c.disabled = True
                await interaction.edit_original_response(embed=discord.Embed(
                    title="🌸 哎呀，靈魂爆掉了！🌸",
                    description=f"**你的手牌:** {' '.join(pc)}\n**點數總計:** {pt}\n\n下次再來跟幽幽子共舞吧～",
                    color=discord.Color.red()
                ).set_footer(text="遊戲結束，冥界等待著你～"), view=None)
                return
            
            if await self.auto_settle(interaction, pc, bet, is_gambler): return
            
            await interaction.edit_original_response(embed=discord.Embed(
                title="🌸 幽幽子為你送上新櫻花一片！🌸",
                description=f"**你的手牌:** {' '.join(pc)}\n**目前點數:** {pt} {self.game.progress_bar(pt)}\n\n要繼續舞動，還是收手？",
                color=discord.Color.from_rgb(255,182,193)
            ).set_footer(text="命運在你手中～"), view=self)
        except Exception as e:
            logger.exception(f"Hit 失敗: {e}")
            await interaction.followup.send("遊戲的櫻花散落了，請重新開始！", ephemeral=True)

    @discord.ui.button(label="停牌 (Stand)", style=discord.ButtonStyle.danger, emoji="✋")
    async def stand(self, button, interaction):
        try:
            await interaction.response.defer()
            async with self.data_manager.balance_lock:
                gd = self.data_manager.blackjack_data[self.guild_id][self.user_id]
                pc = gd["player_cards"]; dc = gd["dealer_cards"]
                bet = gd["bet"]; ig = gd["is_gambler"]
                gd["game_status"] = "ended"
                self.game.dealer_play()
                result, reward = self.game.settle_game(pc, dc, bet, ig)
                self.data_manager.balance[self.guild_id][self.user_id] += reward
            
            await self.data_manager.save_all_async()
            for c in self.children: c.disabled = True
            titles = {"win":"🌸 靈魂之舞勝利！🌸","tie":"🌸 靈魂平手～🌸","lose":"🌸 冥界勝利～🌸"}
            colors = {"win":discord.Color.gold(),"tie":discord.Color.from_rgb(255,182,193),"lose":discord.Color.red()}
            results = {"win":f"你贏得了 **{reward:.2f}** 幽靈幣","tie":f"退還賭注 **{reward:.2f}** 幽靈幣","lose":"下次再來賞櫻吧～"}
            await interaction.edit_original_response(embed=discord.Embed(
                title=titles[result],
                description=f"**你的手牌:** {' '.join(pc)}\n**幽幽子的手牌:** {' '.join(dc)}\n\n{results[result]}",
                color=colors[result]
            ).set_footer(text="遊戲結束，櫻花依舊飄落～"), view=None)
            logger.info(f"{self.user_id} Stand, 結果: {result}, 獎勵: {reward:.2f}")
        except Exception as e:
            logger.exception(f"Stand 失敗: {e}")
            await interaction.followup.send("櫻花舞失效了，請重新邀幽幽子共舞！", ephemeral=True)

    @discord.ui.button(label="雙倍 (Double)", style=discord.ButtonStyle.success, emoji="💰")
    async def double_down(self, button, interaction):
        try:
            await interaction.response.defer()
            
            # [Debug 修復 #1] 徹底重構：將錯誤檢查與 Discord API 回覆移到鎖的外部！
            # 原版在鎖內部 await interaction.edit_original_response，會導致鎖被長時間佔用，卡死其他指令。
            error_type = None
            doubled_bet = 0
            pc = dc = None
            player_total = 0
            result = reward = None
            
            async with self.data_manager.balance_lock:
                gd = self.data_manager.blackjack_data[self.guild_id][self.user_id]
                if gd["double_down_used"]:
                    error_type = "used"
                else:
                    bet = gd["bet"]
                    ig = gd["is_gambler"]
                    ub = self.data_manager.balance[self.guild_id][self.user_id]
                    doubled_bet = bet * 2
                    if ub < bet:
                        error_type = "no_money"
                    else:
                        # 純記憶體操作
                        gd["bet"] = doubled_bet
                        gd["double_down_used"] = True
                        self.data_manager.balance[self.guild_id][self.user_id] -= bet
                        
                        pc = gd["player_cards"]
                        dc = gd["dealer_cards"]
                        pc.append(self.game.draw_card())
                        player_total = self.game.calculate_hand(pc)
                        gd["player_cards"] = pc
                        gd["game_status"] = "ended"
                        
                        if player_total <= 21:
                            self.game.dealer_play()
                            result, reward = self.game.settle_game(pc, dc, doubled_bet, ig)
                            self.data_manager.balance[self.guild_id][self.user_id] += reward

            # 鎖釋放後，處理錯誤訊息
            if error_type == "used":
                await interaction.edit_original_response(embed=discord.Embed(
                    title="🌸 命運只能挑戰一次！🌸",
                    description="你已經用過雙倍下注了哦～每局只能一次！",
                    color=discord.Color.red()
                ), view=self)
                return
            if error_type == "no_money":
                await interaction.edit_original_response(embed=discord.Embed(
                    title="🌸 櫻花能量不足～ 🌸",
                    description=f"你的幽靈幣只有 **{ub:.2f}**，不足以挑戰雙倍 **{doubled_bet:.2f}** 哦～",
                    color=discord.Color.red()
                ), view=self)
                return

            # 鎖釋放後，保存數據
            await self.data_manager.save_all_async()
            
            # 鎖釋放後，更新 UI
            for c in self.children: c.disabled = True
            if player_total > 21:
                await interaction.edit_original_response(embed=discord.Embed(
                    title="🌸 哎呀，靈魂爆掉了！🌸",
                    description=f"**你的手牌:** {' '.join(pc)}\n**總點數:** {player_total}\n\n下次再來賞櫻跳舞吧～",
                    color=discord.Color.red()
                ).set_footer(text="遊戲結束，櫻花謝了～"), view=None)
                return
                
            titles = {"win":"🌸 櫻花舞勝利！🌸","tie":"🌸 靈魂平衡～🌸","lose":"🌸 冥界勝利～🌸"}
            colors = {"win":discord.Color.gold(),"tie":discord.Color.from_rgb(255,182,193),"lose":discord.Color.red()}
            results = {"win":f"你贏得了 **{reward:.2f}** 幽靈幣","tie":f"退還賭注 **{reward:.2f}** 幽靈幣","lose":"下次再來共舞吧～"}
            await interaction.edit_original_response(embed=discord.Embed(
                title=titles[result],
                description=f"**你的手牌:** {' '.join(pc)}\n**幽幽子的手牌:** {' '.join(dc)}\n\n**雙倍賭注:** {doubled_bet:.2f}\n{results[result]}",
                color=colors[result]
            ).set_footer(text="遊戲結束，櫻花依舊飄落～"), view=None)
            logger.info(f"{self.user_id} Double Down, 結果: {result}, 獎勵: {reward:.2f}")
        except Exception as e:
            logger.exception(f"Double Down 失敗: {e}")
            await interaction.followup.send("櫻花舞失效了，請重新邀幽幽子共舞！", ephemeral=True)


class Blackjack(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(name="blackjack", description="🌸 幽幽子邀你在冥界櫻花園共舞一場21點～")
    async def blackjack(
        self, ctx, 
        # [Debug 修復 #4] 採用雙重保險寫法，消除 IDE 警告
        bet: float = discord.Option(float, "下注金額 (幽靈幣)", min_value=1.0)
    ):
        try:
            if not hasattr(self.bot, "data_manager"):
                await ctx.respond("❌ 數據管理器不存在", ephemeral=True); return
            
            dm = self.bot.data_manager
            
            # [Debug 修復 #3] 加入在線備份攔截
            if not await dm.check_backup_status(ctx, "blackjack"):
                return

            bet = round(bet, 2)
            uid = str(ctx.author.id); gid = str(ctx.guild.id)

            reward = None
            async with dm.balance_lock:
                if dm.blackjack_data.get(gid,{}).get(uid,{}).get("game_status") == "ongoing":
                    await ctx.respond(embed=discord.Embed(
                        title="🌸 靈魂還在跳舞！🌸",
                        description="你已經在進行一場櫻花舞了，請先完成再開新舞～",
                        color=discord.Color.red()
                    ), ephemeral=True); return
                
                ub = round(dm.balance.get(gid,{}).get(uid,0), 2)
                if ub < bet:
                    await ctx.respond(embed=discord.Embed(
                        title="🌸 幽靈幣不足，櫻花不開～ 🌸",
                        description=f"你的幽靈幣只有 **{ub:.2f}**，無法下注 **{bet:.2f}** 哦～",
                        color=discord.Color.red()
                    ), ephemeral=True); return
                
                game = BlackjackGame(); game.shuffle_deck()
                pc, dc = game.deal_initial_cards()
                dm.balance.setdefault(gid,{})[uid] = ub - bet
                
                # [Debug 修復 #2] 直接讀取記憶體，消除同步 I/O 阻塞
                is_gambler = dm.user_config.get(gid, {}).get(uid, {}).get("job") == "賭徒"
                
                dm.blackjack_data.setdefault(gid,{})[uid] = {
                    "player_cards": pc, "dealer_cards": dc, "bet": bet,
                    "game_status": "ongoing", "double_down_used": False, "is_gambler": is_gambler
                }
                pt = game.calculate_hand(pc)
                if pt == 21:
                    m = 3.5 if is_gambler else 2.5
                    reward = round(bet * m, 2)
                    dm.balance[gid][uid] += reward
                    dm.blackjack_data[gid][uid]["game_status"] = "ended"

            await dm.save_all_async()

            if pt == 21:
                await ctx.respond(embed=discord.Embed(
                    title="🌸 黑傑克！櫻花魂閃耀！🌸",
                    description=f"**你的手牌:** {' '.join(pc)}\n\n幽幽子為你獻上 **{reward:.2f}** 幽靈幣的祝福～",
                    color=discord.Color.gold()
                ).set_footer(text="恭喜！櫻花灑滿冥界"))
                logger.info(f"{uid} 開局 Blackjack, 贏得 {reward:.2f}"); return

            view = BlackjackButtons(game, dm, gid, uid)
            embed = discord.Embed(
                title="🌸 幽幽子的櫻花21點舞開始！🌸",
                description=(
                    f"你下注了 **{bet:.2f}** 幽靈幣，幽幽子邀你共舞～\n\n"
                    f"**你的初始手牌:** {' '.join(pc)}\n"
                    f"**總點數:** {pt} {game.progress_bar(pt)}\n\n"
                    f"**幽幽子的明牌:** {dc[0]}"
                ),
                color=discord.Color.from_rgb(255,182,193)
            ).set_footer(text="選擇命運吧～櫻花舞只等你來")
            response = await ctx.respond(embed=embed, view=view)
            view.message = await response.original_response()
            logger.info(f"{uid} 開始 Blackjack, 下注: {bet:.2f}")
        except Exception as e:
            logger.exception(f"Blackjack 失敗: {e}")
            await ctx.respond(embed=discord.Embed(
                title="🌸 冥界櫻花飄散了～ 🌸",
                description="哎呀，櫻花舞出了點小問題，請稍後再來邀幽幽子共舞！",
                color=discord.Color.red()
            ), ephemeral=True)


def setup(bot):
    bot.add_cog(Blackjack(bot))
    logger.info("Blackjack 遊戲系統已載入")
