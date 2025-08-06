import discord
from discord.ext import commands
import openai
import asyncio
import os
import random
import time

API_URL = 'https://api.chatanywhere.org/v1/'  # 如果你用的是這個平台

class Ping(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(name="ping", description="幽幽子為你測試與靈界通訊的延遲～")
    async def ping(self, ctx: discord.ApplicationContext):
        openai.api_base = API_URL
        openai.api_key = os.getenv('CHATANYWHERE_API')

        await ctx.defer()

        embed = discord.Embed(
            title="🌸 幽幽子的靈界通訊測試 🌸",
            description="幽幽子正在與靈界通訊，測試延遲中…請稍候～",
            color=discord.Color.from_rgb(255, 182, 193)
        )
        embed.set_footer(text=random.choice([
            "靈魂的波動正在傳遞，稍等一下哦～",
            "嘻嘻，靈界的回應有時會慢一點呢～",
            "櫻花飄落的速度，比這通訊還快吧？"
        ]))

        message = await ctx.followup.send(embed=embed)

        iterations = 3
        total_time = 0
        delays = []

        for i in range(iterations):
            start_time = time.time()
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are a simple ping tester."},
                        {"role": "user", "content": "Ping!"}
                    ],
                    max_tokens=10
                )
            except Exception as e:
                error_embed = discord.Embed(
                    title="🌸 哎呀，靈界通訊失敗了！🌸",
                    description=f"幽幽子試圖與靈界通訊時，發生了一點小意外…\n錯誤：{e}",
                    color=discord.Color.red()
                )
                error_embed.set_footer(text="下次再試試吧～")
                await message.edit(embed=error_embed)
                return

            delay = (time.time() - start_time) * 1000
            delays.append(delay)
            total_time += delay

            if delay <= 500:
                embed_color = discord.Color.teal()
            elif delay <= 1000:
                embed_color = discord.Color.gold()
            else:
                embed_color = discord.Color.red()

            update_embed = discord.Embed(
                title="🌸 幽幽子的靈界通訊測試 🌸",
                description=(
                    f"正在與靈界通訊… 第 {i + 1}/{iterations} 次\n\n"
                    f"**本次延遲**: `{delay:.2f} 毫秒`\n"
                    f"**平均延遲**: `{total_time / (i + 1):.2f} 毫秒`"
                ),
                color=embed_color
            )
            update_embed.set_footer(text=random.choice([
                f"第 {i + 1} 次通訊完成，靈魂的回應真快呢～",
                f"靈界第 {i + 1} 次回應，櫻花都忍不住飄落了～",
                f"第 {i + 1} 次通訊，靈魂的波動真美妙～"
            ]))
            await message.edit(embed=update_embed)
            await asyncio.sleep(1)

        avg_delay = total_time / iterations
        if avg_delay <= 500:
            result_color = discord.Color.teal()
            footer_choices = [
                "靈界的通訊真順暢，靈魂的舞步都輕快起來了～",
                "這樣的延遲，連幽靈都會讚嘆哦～",
                "嘻嘻，靈界與你的靈魂完美共鳴了～"
            ]
        elif avg_delay <= 1000:
            result_color = discord.Color.gold()
            footer_choices = [
                "通訊有點慢呢，靈魂的波動需要更多練習哦～",
                "這樣的延遲，櫻花都等得有點不耐煩了～",
                "靈界的回應有點遲，可能是幽靈在偷懶吧？"
            ]
        else:
            result_color = discord.Color.red()
            footer_choices = [
                "哎呀，靈界的通訊太慢了，靈魂都快睡著了～",
                "這樣的延遲，連櫻花都忍不住嘆息了～",
                "靈界的回應太慢了，幽幽子都等得不耐煩了～"
            ]

        result_embed = discord.Embed(
            title="🌸 幽幽子的靈界通訊結果 🌸",
            description=(
                f"**WebSocket 延遲**: `{self.bot.latency * 1000:.2f} 毫秒`\n"
                f"**靈界通訊平均延遲**: `{avg_delay:.2f} 毫秒`\n\n"
                f"詳細結果：\n"
                f"第 1 次: `{delays[0]:.2f} 毫秒`\n"
                f"第 2 次: `{delays[1]:.2f} 毫秒`\n"
                f"第 3 次: `{delays[2]:.2f} 毫秒`"
            ),
            color=result_color
        )
        result_embed.set_footer(text=random.choice(footer_choices))
        await message.edit(embed=result_embed)

def setup(bot):
    bot.add_cog(Ping(bot))
