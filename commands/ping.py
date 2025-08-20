import discord
from discord.ext import commands
import asyncio
import random
import time

class Ping(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(name="ping", description="幽幽子為你測試與Discord伺服器的通訊延遲～")
    async def ping(self, ctx: discord.ApplicationContext):
        await ctx.defer()

        embed = discord.Embed(
            title="🌸 幽幽子的Discord通訊測試 🌸",
            description="幽幽子正在測試延遲中…請稍候～",
            color=discord.Color.from_rgb(255, 182, 193)
        )
        embed.set_footer(text=random.choice([
            "靈魂的波動正在傳遞，稍等一下哦～",
            "嘻嘻，Discord的回應有時會慢一點呢～",
            "櫻花飄落的速度，比這通訊還快吧？"
        ]))

        message = await ctx.followup.send(embed=embed)

        iterations = 5
        delays = []
        total_time = 0

        for i in range(iterations):
            start_time = time.time()
            await asyncio.sleep(0)
            end_time = time.time()
            delay = (end_time - start_time) + self.bot.latency
            delay_ms = delay * 1000
            delays.append(delay_ms)
            total_time += delay_ms

            if delay_ms <= 500:
                embed_color = discord.Color.teal()
            elif delay_ms <= 1000:
                embed_color = discord.Color.gold()
            else:
                embed_color = discord.Color.red()

            update_embed = discord.Embed(
                title="🌸 幽幽子的Discord通訊測試 🌸",
                description=(
                    f"正在測試… 第 {i + 1}/{iterations} 次\n\n"
                    f"**本次延遲**: `{delay_ms:.2f} 毫秒`"
                ),
                color=embed_color
            )
            update_embed.set_footer(text=random.choice([
                f"第 {i + 1} 次通訊完成，靈魂的回應真快呢～",
                f"Discord第 {i + 1} 次回應，櫻花都忍不住飄落了～",
                f"第 {i + 1} 次通訊，靈魂的波動真美妙～"
            ]))
            await message.edit(embed=update_embed)
            await asyncio.sleep(1)

        avg_delay = total_time / iterations
        if avg_delay <= 500:
            result_color = discord.Color.teal()
            footer_choices = [
                "通訊真順暢，靈魂的舞步都輕快起來了～",
                "這樣的延遲，連幽靈都會讚嘆哦～",
                "嘻嘻，Discord與你的靈魂完美共鳴了～"
            ]
        elif avg_delay <= 1000:
            result_color = discord.Color.gold()
            footer_choices = [
                "通訊有點慢呢，靈魂的波動需要更多練習哦～",
                "這樣的延遲，櫻花都等得有點不耐煩了～",
                "Discord的回應有點遲，可能是幽靈在偷懶吧？"
            ]
        else:
            result_color = discord.Color.red()
            footer_choices = [
                "哎呀，通訊太慢了，靈魂都快睡著了～",
                "這樣的延遲，連櫻花都忍不住嘆息了～",
                "Discord的回應太慢了，幽幽子都等得不耐煩了～"
            ]

        result_embed = discord.Embed(
            title="🌸 幽幽子的Discord通訊結果 🌸",
            description=(
                f"**WebSocket 延遲**: `{self.bot.latency * 1000:.2f} 毫秒`\n"
                f"**平均延遲**: `{avg_delay:.2f} 毫秒`\n\n"
                f"詳細結果：\n"
                + "\n".join([f"第 {i + 1} 次: `{delays[i]:.2f} 毫秒`" for i in range(iterations)])
            ),
            color=result_color
        )
        result_embed.set_footer(text=random.choice(footer_choices))
        await message.edit(embed=result_embed)

def setup(bot):
    bot.add_cog(Ping(bot))
