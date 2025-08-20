import discord
from discord.ext import commands
import random

class QuizView(discord.ui.View):
    def __init__(self, ctx, question, correct_answer, options):
        super().__init__(timeout=30)
        self.ctx = ctx
        self.question = question
        self.correct_answer = correct_answer
        self.answered = False
        for option in options:
            self.add_item(QuizButton(option, correct_answer, self))

    async def on_timeout(self):
        if self.answered:
            return
        embed = discord.Embed(
            title="🪭 幽幽子的問答時間～",
            description=f"{self.question}\n\n⏳ 「時間到了呢～」幽幽子飄走了，正確答案是 `{self.correct_answer}`！",
            color=discord.Color.dark_grey()
        )
        embed.set_footer(text="幽靈的謎題只有30秒哦～")
        for child in self.children:
            child.disabled = True
        try:
            await self.message.edit(embed=embed, view=self)
        except Exception:
            pass

class QuizButton(discord.ui.Button):
    def __init__(self, label, correct_answer, quiz_view):
        super().__init__(label=label, style=discord.ButtonStyle.secondary)
        self.is_correct = label == correct_answer
        self.quiz_view = quiz_view

    async def callback(self, interaction: discord.Interaction):
        if interaction.user != self.quiz_view.ctx.author:
            return await interaction.response.send_message("❌ 哎呀，這是給別人的謎題哦～", ephemeral=True)

        if self.quiz_view.answered:
            return await interaction.response.send_message("⏳ 這題已經解開啦，幽靈不會重複問哦！", ephemeral=True)

        self.quiz_view.answered = True
        self.quiz_view.stop()

        for child in self.quiz_view.children:
            child.disabled = True
            if isinstance(child, discord.ui.Button):
                if child.label == self.quiz_view.correct_answer:
                    child.style = discord.ButtonStyle.success
                else:
                    child.style = discord.ButtonStyle.danger

        if self.is_correct:
            desc = f"{self.quiz_view.question}\n\n✅ 「嘻嘻，答對了呢～」幽幽子為你鼓掌！🎉"
            color = discord.Color.green()
        else:
            desc = f"{self.quiz_view.question}\n\n❌ 「哎呀，錯啦～」正確答案是 `{self.quiz_view.correct_answer}`，下次再來哦！"
            color = discord.Color.red()

        embed = discord.Embed(
            title="🪭 幽幽子的問答時間～",
            description=desc,
            color=color
        )
        embed.set_footer(text="幽靈的謎題只有30秒哦～")
        await interaction.response.edit_message(embed=embed, view=self.quiz_view)

class QuizCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(name="quiz", description="幽幽子邀你來場問答挑戰哦～")
    async def quiz(self, ctx: discord.ApplicationContext):
        data_manager = ctx.bot.data_manager
        quiz_data = data_manager.load_json("config/quiz.json", default=[])
        if not quiz_data:
            return await ctx.respond("❌ 哎呀，題庫空空的，就像幽靈肚子一樣！")

        question_data = random.choice(quiz_data)
        question = question_data.get("question", "")
        correct_answer = question_data.get("correct", "")
        incorrect_answers = question_data.get("incorrect", [])

        if not question or not correct_answer or len(incorrect_answers) != 3:
            return await ctx.respond("❌ 題庫有誤，請檢查 quiz.json 格式！")

        options = [correct_answer] + incorrect_answers
        random.shuffle(options)

        embed = discord.Embed(
            title="🪭 幽幽子的問答時間～",
            description=f"「{question}」\n嘻嘻，這可不好猜呢～快選一個吧！",
            color=discord.Color.from_rgb(255, 182, 193)
        )
        embed.set_footer(text="幽靈的謎題只有30秒哦～")

        view = QuizView(ctx, question, correct_answer, options)
        message = await ctx.respond(embed=embed, view=view)
        # 給 view 紀錄訊息以便 on_timeout 用
        if hasattr(message, "original_response"):
            view.message = await message.original_response()
        else:
            view.message = await message

def setup(bot):
    bot.add_cog(QuizCog(bot))
