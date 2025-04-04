import discord
import os
from keep_alive import keep_alive
from discord import app_commands
import weather
import BombGame
import re
import asyncio
import random
from datetime import datetime, timezone, timedelta

intents=discord.Intents.all()
intents.message_content = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

# 日本時間（JST）
JST = timezone(timedelta(hours=9))

# おみくじの履歴を保存する辞書
last_omikuji = {}

@client.event
async def on_ready():
    print('ログインしました')
 # アクティビティを設定
    activity = discord.Activity(name='疾風スピードスター', type=discord.ActivityType.competing)
    await client.change_presence(status=discord.Status.online, activity=activity)
    # スラッシュコマンドを同期
    await tree.sync()
# スラッシュコマンド
@tree.command(name='membercount', description='サーバーの人数を表示します') 
async def member_count(message):
    # message インスタンスから guild インスタンスを取得
    guild = message.guild 
    # ユーザとBOTを区別しない場合
    member_count = guild.member_count
    await message.response.send_message(f'今の人数は{member_count}です')
@tree.command(name='help', description='疾風の使い方') 
async def help_command(message):
    help_message = discord.Embed( # Embedを定義する
                          title="疾風の使い方",# タイトル
                          color=0x00ff00, # フレーム色指定(今回は緑)
                          description="このbotの使い方を説明します。"
                          )
    help_message.add_field(name="/help",value="今表示しているものです。", inline=False) # フィールドを追加。
    help_message.add_field(name="/membercount",value="サーバー参加人数を表示します。", inline=False)
    help_message.add_field(name="/omikuji",value="おみくじ引けます", inline=False)
    help_message.set_footer(text="made by TAM Game Creator", # フッターには開発者の情報でも入れてみる
                     icon_url="https://tamgamecreator.github.io/update/data/Icon01.png")
    await message.response.send_message(embed=help_message) # embedの送信には、embed={定義したembed名}
@tree.command(name='omikuji', description='おみくじ引きます') 
async def omikuji_command(interaction: discord.Interaction):
    user_id = interaction.user.id
    now = datetime.now(JST).date()  # 今日の日付（JST）
    # すでに引いているかチェック
    if user_id in last_omikuji and last_omikuji[user_id] == now:
        await interaction.response.send_message("⚠️ おみくじは1日1回までです！明日また引いてください！", ephemeral=True)
        return
    # おみくじを引く
    choice = random.choice(['大吉', '中吉', '吉', '小吉', '末吉', '凶', '大凶'])
    await interaction.response.send_message(f"あなたの今日の運勢は **{choice}** です！")
    # 今日の日付を記録
    last_omikuji[user_id] = now
@tree.command(name="random_number", description="指定した範囲内でランダムな数値を生成します")
@app_commands.describe(min_value="最小値", max_value="最大値")
async def random_number(interaction: discord.Interaction, min_value: int, max_value: int):
    """ 指定範囲内のランダムな数値を送信 """
    if min_value > max_value:
        await interaction.response.send_message("⚠️ 最小値が最大値より大きいです。もう一度入力してください。", ephemeral=True)
        return
    result = random.randint(min_value, max_value)
    await interaction.response.send_message(f"⚡ ランダムな数値: **{result}**（{min_value} 〜 {max_value}）")
@tree.command(name="bomb", description="爆弾解除ゲームを開始する！")
@app_commands.describe(mode="ボムを仕掛けるか、自動で決めるか")
@app_commands.choices(mode=[
    app_commands.Choice(name="ボムを仕掛ける", value="set"),
    app_commands.Choice(name="自動で決める", value="auto")
])
async def bomb_game(interaction: discord.Interaction, mode: str):
    if mode == "auto":
        # 自動で爆弾の場所を決定
        correct_button = random.choice(["A", "B", "C"])
        await interaction.response.send_message("💣 **爆弾がセットされた！正しいボタンを押して解除しよう！**", view=BombGame.BombGame(correct_button))
    
    elif mode == "set":
        # プレイヤーが爆弾をセット
        await interaction.response.send_message("💣 **どこに爆弾を仕掛けますか？**", view=BombGame.BombSetup(interaction.user.id))

    
@client.event
async def on_message(message):
    reg_res = re.compile(u"疾風、(.+)の天気は？").search(message.content)
    if message.author == client.user:
        return
    if message.channel.id == 1236670753165021204:#自己紹介チャンネルに自動で絵文字
        emoji ="👍"
        await message.add_reaction(emoji)
    elif message.content == "こんにちは":
        await message.channel.send("こんにちは！")
    elif client.user in message.mentions: # 話しかけられたかの判定
        await message.channel.send(f'{message.author.mention} 呼びましたか？') # 返信メッセージを送信
    elif message.content == "いいね" or message.content == "いいね！":
        emoji ="👍"
        await message.add_reaction(emoji)
    elif message.content == "おめでとう":
        await message.channel.send("おめでとうございます！")
    elif message.content == "疾風、自己紹介":
        jikosyokai = (
        f"こんにちは！疾風です！\n"
        f"疾風スピードスターを盛り上げるために作成されました。\n"
        f"よろしくお願いします👍"
        )
        await message.channel.send(jikosyokai)
    elif message.content == "疾風ありがとう":
        await message.channel.send("どういたしまして！👍")
    elif message.channel.id == 1347057189868539905 and message.author.bot:
        await message.delete()
    elif reg_res:
        weather_message = weather.on_message(reg_res)
        await message.channel.send(weather_message)
    elif message.content == "!join":
        if message.author.voice:  # ユーザーがVCにいるか確認
            channel = message.author.voice.channel
            try:
                await channel.connect()
            except discord.errors.ClientException:
                await message.channel.send("すでにVCに接続しています！")
            except Exception as e:
                await message.channel.send(f"エラーが発生しました: {e}")
        else:
            await message.channel.send("VCに参加してからコマンドを使用してください！")

    elif message.content == "!leave":
        vc = message.guild.voice_client  # サーバーのVCクライアントを取得
        if vc:  # VCに接続している場合のみ処理
            await vc.disconnect()
        else:
            await message.channel.send("ボットはVCに参加していません！")

                
TOKEN = os.getenv("DISCORD_TOKEN")
# Web サーバの立ち上げ
keep_alive()
client.run(TOKEN)
