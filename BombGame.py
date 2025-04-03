import discord
import random

class BombGame(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.correct_button = random.choice(["A", "B", "C"])  # 正解ボタンをランダムに設定

    @discord.ui.button(label="A", style=discord.ButtonStyle.primary)
    async def button_a(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.check_bomb(interaction, "A")

    @discord.ui.button(label="B", style=discord.ButtonStyle.primary)
    async def button_b(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.check_bomb(interaction, "B")

    @discord.ui.button(label="C", style=discord.ButtonStyle.primary)
    async def button_c(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.check_bomb(interaction, "C")

    async def check_bomb(self, interaction, choice):
        if choice == self.correct_button:
            await interaction.response.edit_message(content=f"💣 **{interaction.user.name} が爆弾を解除した！🎉**", view=None)
        else:
            await interaction.response.edit_message(content=f"💥 **{interaction.user.name} のミス！爆発した…💀**", view=None)
