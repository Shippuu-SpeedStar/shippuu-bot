import random
import discord
from discord import app_commands
class Danmaku(discord.ui.View):
    WIDTH = 5
    HEIGHT = 5
    MAX_TURNS = 30

    def __init__(self, player_id: int):
        # 60秒間操作がなければ終了
        super().__init__(timeout=60)

        self.player_id = player_id
        self.player_x = 2
        self.player_y = 4

        self.hp = 3
        self.turn = 0
        self.score = 0
        self.bullets = set()

        self.finished = False
        self.result_message = ""
        self.message = None

        # 最初の弾幕を生成
        self.spawn_bullets()

    def spawn_bullets(self):
        """画面上部に新しい弾を生成します。"""

        # ターンが進むほど弾数が増加
        bullet_count = min(1 + self.turn // 10, 3)

        available_x = list(range(self.WIDTH))
        random.shuffle(available_x)

        for x in available_x[:bullet_count]:
            self.bullets.add((x, 0))

    def move_bullets(self):
        """すべての弾を1マス下へ移動します。"""

        moved_bullets = set()

        for x, y in self.bullets:
            new_y = y + 1

            # 画面内にある弾だけ残す
            if new_y < self.HEIGHT:
                moved_bullets.add((x, new_y))

        self.bullets = moved_bullets

    def check_collision(self):
        """プレイヤーと弾の衝突を判定します。"""

        player_position = (self.player_x, self.player_y)

        if player_position in self.bullets:
            self.hp -= 1
            self.bullets.remove(player_position)
            return True

        return False

    def render(self):
        """現在のゲーム状態をDiscord用の文字列に変換します。"""

        board = []

        for y in range(self.HEIGHT):
            row = []

            for x in range(self.WIDTH):
                position = (x, y)

                if position == (self.player_x, self.player_y):
                    row.append("🛩️")
                elif position in self.bullets:
                    row.append("🔴")
                else:
                    row.append("⬛")

            board.append("".join(row))

        hp_display = "❤️" * self.hp + "🖤" * (3 - self.hp)

        text = (
            "## 弾幕回避ゲーム\n"
            f"{'\n'.join(board)}\n\n"
            f"残りHP：{hp_display}\n"
            f"ターン：{self.turn}/{self.MAX_TURNS}\n"
            f"スコア：{self.score}"
        )

        if self.result_message:
            text += f"\n\n{self.result_message}"

        return text

    def disable_all_buttons(self):
        """すべての操作ボタンを無効化します。"""

        for item in self.children:
            item.disabled = True

    async def interaction_check(
        self,
        interaction: discord.Interaction
    ) -> bool:
        """ゲーム開始者以外からの操作を拒否します。"""

        if interaction.user.id != self.player_id:
            await interaction.response.send_message(
                "❌ このゲームは開始した本人だけが操作できます。",
                ephemeral=True
            )
            return False

        return True

    async def process_turn(
        self,
        interaction: discord.Interaction,
        move_x: int,
        move_y: int
    ):
        """プレイヤーの移動とターン進行を処理します。"""

        if self.finished:
            await interaction.response.send_message(
                "このゲームはすでに終了しています。",
                ephemeral=True
            )
            return

        # プレイヤーを移動
        self.player_x = max(
            0,
            min(self.WIDTH - 1, self.player_x + move_x)
        )
        self.player_y = max(
            0,
            min(self.HEIGHT - 1, self.player_y + move_y)
        )

        # 弾を移動
        self.move_bullets()

        # 衝突判定
        was_hit = self.check_collision()

        self.turn += 1

        if was_hit:
            self.result_message = "💥 被弾しました！"
        else:
            self.score += 10
            self.result_message = ""

        # ゲームオーバー判定
        if self.hp <= 0:
            self.finished = True
            self.result_message = (
                f"## 💥 ゲームオーバー\n"
                f"最終スコア：**{self.score}**"
            )
            self.disable_all_buttons()
            self.stop()

        # クリア判定
        elif self.turn >= self.MAX_TURNS:
            self.finished = True

            # 残ったHPに応じてボーナス
            hp_bonus = self.hp * 100
            self.score += hp_bonus

            self.result_message = (
                f"## 🎉 ゲームクリア！\n"
                f"HPボーナス：**+{hp_bonus}**\n"
                f"最終スコア：**{self.score}**"
            )
            self.disable_all_buttons()
            self.stop()

        else:
            # 次の弾幕を生成
            self.spawn_bullets()

        await interaction.response.edit_message(
            content=self.render(),
            view=self
        )

    @discord.ui.button(
        label="←",
        style=discord.ButtonStyle.primary,
        row=0
    )
    async def move_left(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        await self.process_turn(interaction, -1, 0)

    @discord.ui.button(
        label="↑",
        style=discord.ButtonStyle.primary,
        row=0
    )
    async def move_up(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        await self.process_turn(interaction, 0, -1)

    @discord.ui.button(
        label="待機",
        style=discord.ButtonStyle.secondary,
        row=0
    )
    async def wait_turn(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        await self.process_turn(interaction, 0, 0)

    @discord.ui.button(
        label="↓",
        style=discord.ButtonStyle.primary,
        row=0
    )
    async def move_down(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        await self.process_turn(interaction, 0, 1)

    @discord.ui.button(
        label="→",
        style=discord.ButtonStyle.primary,
        row=0
    )
    async def move_right(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        await self.process_turn(interaction, 1, 0)

    async def on_timeout(self):
        """60秒間操作がなかった場合の処理です。"""

        if self.finished:
            return

        self.finished = True
        self.result_message = "⌛ 操作がなかったためゲームを終了しました。"
        self.disable_all_buttons()

        if self.message is not None:
            try:
                await self.message.edit(
                    content=self.render(),
                    view=self
                )
            except discord.HTTPException:
                pass
