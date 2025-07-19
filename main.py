import discord
import os
from keep_alive import keep_alive
from discord import app_commands
from discord.ext import commands, tasks
import weather
import BombGame
import topic
import re
import asyncio
import random
from datetime import datetime, timezone, timedelta
import time
import requests
import json

intents=discord.Intents.all()
intents.message_content = True
intents.members = True  # メンバー参加イベントを取得するために必要
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

# 日本時間（JST）
JST = timezone(timedelta(hours=9))

# おみくじの履歴を保存する辞書
last_omikuji = {}
# 遠隔当行の履歴を保存する辞書
ALLOWED_USERS = {1228003399933497366, 1255885908784451739}  # ✅ 使えるユーザーのIDをここに追加
cooldowns = {}  # user_id: last_used_timestamp
COOLDOWN_SECONDS = 600  # 10分（600秒）
ALLOWED_GUILD_IDS = {1235503983179730944,1268381411904323655,1268199427865055345}  # ✅ Botが所属できるサーバーIDをここに記入（複数対応可）
PROBOT_ID = 282859044593598464  # ProbotのユーザーID
ROLE_ID = 1301466875762442250  # 付与したいロールのID
#money
money_data = {}
last_work_used = {}
GITHUB_REPO = "Shippuu-SpeedStar/shippuu-bot"  # GitHubリポジトリのパス
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")  # 安全な方法で読み込む（本番環境ではSecrets管理推奨）
@client.event
async def on_member_join(member):
    """ 新しいメンバーが参加した時に発動 """
    guild = member.guild
    probot = guild.get_member(PROBOT_ID)  # Probotのステータスを取得

    if probot is None or probot.status == discord.Status.offline:
        # Probotがオフラインならロールを付与
        role = guild.get_role(ROLE_ID)
        if role:
            #await member.add_roles(role)
            guild = member.guild 
            # ユーザとBOTを区別しない場合
            member_count = guild.member_count
            msg = (
                f"{member.mention}さんが参加しました！🎉 {member_count}人目の参加者です！✨\n"
                "-# メンションNGの方も最初だけメンションすみません。\n"
                "<#1236670753165021204>で自己紹介お願いします🖊️\n"
                "<#1254457265046421556>で超古参勢ロール配布中です！(100人まで)"
            )
            await client.get_channel(1235503983179730946).send(msg)
        else:
            print("指定されたロールが見つかりません。")
@client.event
async def on_guild_join(guild):
    if guild.id not in ALLOWED_GUILD_IDS:
        print(f"❌ 許可されていないサーバー ({guild.name}) に参加したため退出します。")
        try:
            await guild.leave()
        except Exception as e:
            print(f"⚠️ サーバーから退出できませんでした: {e}")
    else:
        print(f"✅ 許可されたサーバー ({guild.name}) に参加しました。")

@client.event
async def on_ready():
    print('ログインしました')
 # アクティビティを設定
    activity = discord.Activity(name='疾風スピードスター', type=discord.ActivityType.competing)
    await client.change_presence(status=discord.Status.online, activity=activity)
    # スラッシュコマンドを同期
    await tree.sync()
    save_money_data.start()#通貨機能開始
    # money_data 読み込み（Bot起動時）
    try:
        with open("server_money.json", "r", encoding="utf-8") as f:
            money_data = json.load(f)
            print("💾 通貨データを読み込みました")
    except FileNotFoundError:
        money_data = {}
        print("⚠️ 通貨データが見つかりませんでした。新規作成します")
# 通貨機能
@tree.command(name='work', description='通貨を獲得します') 
async def member_count(message):
    user_id = str(message.user.id)
    now = datetime.utcnow()
    # クールダウン制限（例：30秒）
    if user_id in last_work_used and now - last_work_used[user_id] < timedelta(seconds=30):
        await message.response.send_message("少し待ってから実行してください", ephemeral=True)
        return
    earned = random.randint(100, 500)
    money_data[user_id] = money_data.get(user_id, 0) + earned
    last_work_used[user_id] = now
    await message.response.send_message(f"{message.user.mention} さんは {earned} コインを稼ぎました！💰現在{money_data[user_id]}所持")
@tree.command(name='money_dump', description='通貨をバックアップします') 
async def member_count(message):
    await message.response.send_message(f"手動バックアップ{money_data}")
    with open("server_money.json", "w", encoding="utf-8") as f:
        json.dump(money_data, f, ensure_ascii=False, indent=4)
    print("通貨データを保存しました")
    # GitHub Actionsトリガー
    trigger_github_workflow(money_data)
@tasks.loop(hours=6)
async def save_money_data():
    with open("server_money.json", "w", encoding="utf-8") as f:
        json.dump(money_data, f, ensure_ascii=False, indent=4)
    print("通貨データを保存しました")
    # GitHub Actionsトリガー
    trigger_github_workflow(money_data)
def trigger_github_workflow(money_data):
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    data = {
        "ref": "main",
        "inputs": {
            "json_data": json.dumps(money_data)
        }
    }
    response = requests.post(
        f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/actions/workflows/save_money.yml/dispatches",
        headers=headers,
        json=data
    )

#スラッシュコマンド
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
        try:
            emoji ="👍"
            await message.add_reaction(emoji)
        except discord.HTTPException as e:
            await message.channel.send("ボットエラー")
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
    elif message.content == "疾風、今日の話題は？":
        today_topic = topic.on_message()
        await message.channel.send(today_topic)
    elif reg_res:
        weather_message = weather.on_message(reg_res)
        await message.channel.send(weather_message)
    # コマンド形式：疾風、チャンネル送信[チャンネルID],[メッセージ内容]
    if message.content.startswith("疾風、チャンネル送信[") and "]," in message.content:
        user_id = message.author.id
        # ✅ 使用許可ユーザーの確認
        if user_id not in ALLOWED_USERS:
            await message.channel.send("❌ このコマンドを使う権限がありません。")
            return
        # ✅ クールダウン確認
        now = time.time()
        last_used = cooldowns.get(user_id, 0)
        if now - last_used < COOLDOWN_SECONDS:
            remaining = int(COOLDOWN_SECONDS - (now - last_used))
            await message.channel.send(f"⏳ あと {remaining // 60}分{remaining % 60}秒 待ってください。")
            return
        # ✅ メッセージ処理
        try:
            # 部分を抽出
            command_body = message.content[len("疾風、チャンネル送信["):]
            channel_id_str, content = command_body.split("],", 1)

            channel_id = int(channel_id_str.strip())
            content = content.strip()

            channel = client.get_channel(channel_id)
            if channel is None:
                await message.channel.send("❌ チャンネルが見つかりません。Botがそのチャンネルにアクセスできるか確認してください。")
                return

            await channel.send(content)
            await message.channel.send(f"✅ 指定したチャンネル <#{channel_id}> に送信しました。")
        except Exception as e:
            await message.channel.send(f"⚠️ エラーが発生しました: {e}")

                
TOKEN = os.getenv("DISCORD_TOKEN")
# Web サーバの立ち上げ
keep_alive()
client.run(TOKEN)
