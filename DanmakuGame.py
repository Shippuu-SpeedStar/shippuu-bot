import discord
import random


class DanmakuGame(discord.ui.View):
    """Discord上で動作するターン制弾幕回避ゲーム"""

    WIDTH = 5
    HEIGHT = 5
    MAX_HP = 3
    MAX_TURNS = 20

    def __init__(self, player_id):
        # 120秒操作されなければViewを終了
        super().__init__(timeout=120)

        self.player_id = player_id

        # プレイヤーの初期位置
        self.player_x = 2
        self.player_y = 4

        self.hp = self.MAX_HP
        self.turn = 0
        self.score = 0

        # 弾の座標を保存
        self.bullets = set()

        self.game_finished = False
        self.status_message = "矢印ボタンを押して弾幕を回避してください。"

        # 最初の弾を生成
        self.spawn_bullets()

    def spawn_bullets(self):
        """画面上部に弾を生成する"""

        # 進行度によって弾数を増やす
        if self.turn < 7:
            bullet_count = 1
        elif self.turn < 14:
            bullet_count = 2
        else:
            bullet_count = 3

        columns = list(range(self.WIDTH))
        random.shuffle(columns)

        for x in columns[:bullet_count]:
            self.bullets.add((x, 0))

    def move_bullets(self):
        """すべての弾を1マス下へ移動する"""

        new_bullets = set()

        for x, y in self.bullets:
            new_y = y + 1

            if new_y < self.HEIGHT:
                new_bullets.add((x, new_y))

        self.bullets = new_bullets

    def check_collision(self):
        """プレイヤーと弾が重なっているか確認する"""

        player_position = (self.player_x, self.player_y)

        if player_position in self.bullets:
            self.bullets.remove(player_position)
            self.hp -= 1
            return True

        return False

    def create_display(self):
        """盤面をメッセージとして作成する"""

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

        board_text = "\n".join(board)

        hp_text = "❤️" * self.hp
        hp_text += "🖤" * (self.MAX_HP - self.hp)

        display = (
            "## 🔴 弾幕回避ゲーム\n"
            + board_text
            + "\n\n"
            + "HP：" + hp_text + "\n"
            + "ターン："
            + str(self.turn)
            + "/"
            + str(self.MAX_TURNS)
            + "\n"
            + "スコア："
            + str(self.score)
            + "\n\n"
            + self.status_message
        )

        return display

    def disable_buttons(self):
        """すべてのボタンを無効化する"""

        for item in self.children:
            item.disabled = True

    async def interaction_check(self, interaction):
        """ゲームを開始した本人以外の操作を拒否する"""

        if interaction.user.id != self.player_id:
            await interaction.response.send_message(
                "❌ このゲームは開始した本人だけが操作できます。",
                ephemeral=True
            )
            return False

        return True

    async def next_turn(self, interaction, move_x, move_y):
        """移動とターン進行を処理する"""

        if self.game_finished:
            await interaction.response.send_message(
                "このゲームはすでに終了しています。",
                ephemeral=True
            )
            return

        # プレイヤーを移動
        self.player_x += move_x
        self.player_y += move_y

        # 盤面の外に出ないように制限
        self.player_x = max(
            0,
            min(self.WIDTH - 1, self.player_x)
        )

        self.player_y = max(
            0,
            min(self.HEIGHT - 1, self.player_y)
        )

        # 弾を1マス下へ移動
        self.move_bullets()

        # 被弾判定
        was_hit = self.check_collision()

        self.turn += 1

        if was_hit:
            self.status_message = "💥 被弾しました！"
        else:
            self.score += 10
            self.status_message = "✅ 回避成功！"

        # HPがなくなった場合
        if self.hp <= 0:
            self.game_finished = True
            self.status_message = (
                "## 💥 ゲームオーバー\n"
                "最終スコア："
                + str(self.score)
            )

            self.disable_buttons()
            self.stop()

        # 最大ターンまで生存した場合
        elif self.turn >= self.MAX_TURNS:
            hp_bonus = self.hp * 100
            self.score += hp_bonus

            self.game_finished = True
            self.status_message = (
                "## 🎉 ゲームクリア！\n"
                "HPボーナス：+"
                + str(hp_bonus)
                + "\n"
                + "最終スコア："
                + str(self.score)
            )

            self.disable_buttons()
            self.stop()

        else:
            # 次の弾を生成
            self.spawn_bullets()

        await interaction.response.edit_message(
            content=self.create_display(),
            view=self
        )

    @discord.ui.button(
        label="←",
        style=discord.ButtonStyle.primary
    )
    async def button_left(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        await self.next_turn(interaction, -1, 0)

    @discord.ui.button(
        label="↑",
        style=discord.ButtonStyle.primary
    )
    async def button_up(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        await self.next_turn(interaction, 0, -1)

    @discord.ui.button(
        label="待機",
        style=discord.ButtonStyle.secondary
    )
    async def button_wait(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        await self.next_turn(interaction, 0, 0)

    @discord.ui.button(
        label="↓",
        style=discord.ButtonStyle.primary
    )
    async def button_down(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        await self.next_turn(interaction, 0, 1)

    @discord.ui.button(
        label="→",
        style=discord.ButtonStyle.primary
    )
    async def button_right(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        await self.next_turn(interaction, 1, 0)
