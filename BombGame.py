import discord
import random
from datetime import timedelta


# 爆弾の場所を記録する辞書
bomb_location = {}


class BombGame(discord.ui.View):
    """爆弾解除ゲームのボタン"""

    def __init__(self, correct_button):
        super().__init__()
        self.correct_button = correct_button

    @discord.ui.button(label="A", style=discord.ButtonStyle.primary)
    async def button_a(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        await self.check_bomb(interaction, "A")

    @discord.ui.button(label="B", style=discord.ButtonStyle.primary)
    async def button_b(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        await self.check_bomb(interaction, "B")

    @discord.ui.button(label="C", style=discord.ButtonStyle.primary)
    async def button_c(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        await self.check_bomb(interaction, "C")

    async def check_bomb(self, interaction, choice):
        if choice == self.correct_button:
            await interaction.response.edit_message(
                content=f"💣 **{interaction.user.name} が爆弾を解除した！🎉**",
                view=None
            )
        else:
            await interaction.response.edit_message(
                content=f"💥 **{interaction.user.name} のミス！爆発した…💀**",
                view=None
            )


class BombSetup(discord.ui.View):
    """ユーザーが爆弾を仕掛けるボタン"""

    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id

    @discord.ui.button(label="A にセット", style=discord.ButtonStyle.danger)
    async def set_a(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        await self.set_bomb(interaction, "A")

    @discord.ui.button(label="B にセット", style=discord.ButtonStyle.danger)
    async def set_b(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        await self.set_bomb(interaction, "B")

    @discord.ui.button(label="C にセット", style=discord.ButtonStyle.danger)
    async def set_c(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        await self.set_bomb(interaction, "C")

    async def set_bomb(self, interaction, choice):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(
                "この爆弾はあなたが仕掛けるものではありません！",
                ephemeral=True
            )
            return

        bomb_location[interaction.channel.id] = choice

        # メッセージを爆弾セット完了に編集 & 解除UIを追加
        await interaction.response.edit_message(
            content="💣 **爆弾がセットされた！**\n他の人は解除を試みよう！",
            view=BombGame(choice)
        )
