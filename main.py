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
from urllib.parse import urlparse  # emoji
from deep_translator import GoogleTranslator
from langdetect import detect  # 言語判定ライブラリ

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
COOLDOWN_SECONDS = 60  # 1分（60秒）
ALLOWED_GUILD_IDS = {1235503983179730944,1268381411904323655,1268199427865055345,1314588938358226986}  # ✅ Botが所属できるサーバーIDをここに記入（複数対応可）
PROBOT_ID = 282859044593598464  # ProbotのユーザーID
ROLE_ID = 1301466875762442250  # 付与したいロールのID
#money機能
AUTO_TRANSLATE_FILE = "AutoTranslateChannel.json"
DATA_FILE = "server_money.json"
REPO = "Shippuu-SpeedStar/shippuu-bot"  # ex: GameCreatorTAM/discord-bot

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
                "<#1236670753165021204>で自己紹介お願いします🖊️"
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
            channel_id = '1428880974820937902'
            channel = client.get_channel(channel_id)
            await channel.send(f"❌ 許可されていないサーバー ({guild.name}) に参加したため退出します。")
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
#emoji 管理者以外は非表示
@tree.command(name="emoji", description="指定したメッセージに絵文字リアクションをつけます")
@app_commands.default_permissions(administrator=True)
@app_commands.describe(
    emoji="つけたい絵文字",
    message_link="Discordメッセージのリンク（省略すると直前のメッセージ）"
)
async def emoji_command(
    interaction: discord.Interaction,
    emoji: str,
    message_link: str = None
):
    try:
        if message_link:
            # メッセージリンクを分解
            parsed = urlparse(message_link)
            parts = parsed.path.strip("/").split("/")
            if len(parts) < 3:
                await interaction.response.send_message("❌ メッセージリンクが正しくありません", ephemeral=True)
                return

            _, channel_id, message_id = map(int, parts[-3:])
            # 対象メッセージ取得
            channel = await client.fetch_channel(channel_id)
            message = await channel.fetch_message(message_id)
        else:
            # コマンド直前のメッセージ取得
            channel = interaction.channel
            history = [m async for m in channel.history(limit=2)]
            if len(history) < 2:
                await interaction.response.send_message("❌ 直前のメッセージが見つかりません", ephemeral=True)
                return
            message = history[0]

        # リアクション追加
        await message.add_reaction(emoji)
        await interaction.response.send_message(f"✅ リアクション {emoji} を追加しました！", ephemeral=True)

    except discord.NotFound:
        await interaction.response.send_message("❌ メッセージが見つかりません", ephemeral=True)
    except discord.Forbidden:
        await interaction.response.send_message("❌ メッセージにリアクションをつける権限がありません", ephemeral=True)
    except discord.HTTPException:
        await interaction.response.send_message("❌ リアクション追加に失敗しました", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ エラー: {e}", ephemeral=True)
        
#テキスト送信
@tree.command(
    name="send",
    description="指定チャンネルにメッセージを送信します（管理者専用）"
)
@app_commands.describe(
    channel_id="送信先のチャンネルID",
    content="送信するメッセージ内容（改行したい場合は |n| を使ってください）"
)
async def send_message(interaction: discord.Interaction, content: str, channel_id: str = None):

    user_id = interaction.user.id

    # 権限チェック
    if user_id not in ALLOWED_USERS:
        await interaction.response.send_message("❌ このコマンドを使う権限がありません。", ephemeral=True)
        return

    # クールダウンチェック
    now = time.time()
    last_used = cooldowns.get(user_id, 0)
    if now - last_used < COOLDOWN_SECONDS:
        remaining = int(COOLDOWN_SECONDS - (now - last_used))
        await interaction.response.send_message(
            f"⏳ あと {remaining // 60}分{remaining % 60}秒 待ってください。",
            ephemeral=True
        )
        return

    cooldowns[user_id] = now

    # 改行トークンを実際の改行に変換
    content = content.replace("|n|", "\n")

    # channel_idが指定されたかどうか
    channel_was_specified = channel_id is not None

    try:
        if channel_was_specified:
            # 指定されたチャンネルを取得
            channel_id_int = int(channel_id)
            channel = client.get_channel(channel_id_int)

            if channel is None:
                await interaction.response.send_message(
                    "❌ チャンネルが見つかりません。"
                    "Botがアクセスできるか確認してください。",
                    ephemeral=True
                )
                return
        else:
            # コマンドが実行されたチャンネルを使用
            channel = interaction.channel

            if channel is None:
                await interaction.response.send_message(
                    "❌ コマンドが実行されたチャンネルを取得できませんでした。",
                    ephemeral=True
                )
                return

        # メッセージ送信
        await channel.send(content)

        # 送信成功時にクールダウンを開始
        cooldowns[user_id] = now

        await interaction.response.send_message(
            f"✅ チャンネル {channel.mention} に送信しました。",
            ephemeral=not channel_was_specified
        )

    except ValueError:
        await interaction.response.send_message(
            "❌ チャンネルIDは数字で入力してください。",
            ephemeral=True
        )

    except discord.Forbidden:
        await interaction.response.send_message(
            "❌ このチャンネルにメッセージを送信する権限がありません。",
            ephemeral=True
        )

    except discord.HTTPException as e:
        await interaction.response.send_message(
            f"⚠️ Discordへの送信中にエラーが発生しました: {e}",
            ephemeral=True
        )
    except Exception as e:
        await interaction.response.send_message(f"⚠️ エラーが発生しました: {e}", ephemeral=True)
    
#money機能
@tree.command(name="money", description="ランダムなお金をゲット！")
async def money_get(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    data = load_money()

    reward = random.randint(50, 100)
    data[user_id] = data.get(user_id, 0) + reward

    save_money(data)  # Render上に一応保存
    trigger_github_action(data)  # GitHub Actionsでcommit

    await interaction.response.send_message(
        f"{interaction.user.mention} さん、{reward}コインを獲得しました！\n"
        f"現在の所持金: {data[user_id]} コイン"
    )
def load_money():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_money(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def trigger_github_action(data):
    """GitHub Actionsに更新リクエストを送る"""
    url = f"https://api.github.com/repos/{REPO}/dispatches"
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"token {GITHUB_TOKEN}"
    }
    payload = {
        "event_type": "update-money",
        "client_payload": {
            "data": json.dumps(data, ensure_ascii=False)
        }
    }
    r = requests.post(url, headers=headers, json=payload)
    print("GitHub Action Trigger:", r.status_code, r.text)

@tree.command(name="translate", description="メッセージを翻訳します")
@app_commands.describe(
    message_id="翻訳したいメッセージのID（省略可）",
    direction="翻訳方向を選択（to_en: 日本語→English, to_ja: English→日本語）",
    ephemeral="実行者だけに表示するかどうか（true/false、省略可）"
)
@app_commands.choices(direction=[
    app_commands.Choice(name="自動/Auto",value="auto"),
    app_commands.Choice(name="日本語 → English", value="to_en"),
    app_commands.Choice(name="English → 日本語", value="to_ja")
])
async def translate(
    interaction: discord.Interaction,
    message_id: str = None,
    direction: str = "auto",
    ephemeral: bool = False
):
    await interaction.response.defer(thinking=True, ephemeral=ephemeral)
    message = None
    if message_id:
        # IDからメッセージ取得
        try:
            message = await interaction.channel.fetch_message(int(message_id))
        except:
            await interaction.followup.send("❌ 指定したメッセージIDのメッセージが見つかりませんでした。", ephemeral=ephemeral)
            return
    else:
        # 直近の「ユーザーが送った」メッセージを取得
        async for msg in interaction.channel.history(limit=10):
            if msg.content and not msg.author.bot:
                message = msg
                break
        if message is None:
            await interaction.followup.send("❌ 翻訳対象のメッセージが見つかりません。", ephemeral=ephemeral)
            return
    text = message.content.strip()
    if not text:
        await interaction.followup.send("❌ メッセージが空です。", ephemeral=ephemeral)
        return
        
    if direction == "auto":
        try:
            detected = detect(text)  # ja / en / etc...
        except:
            await interaction.followup.send("⚠️ 判別中にエラーが発生しました。", ephemeral=ephemeral)
            return
        if detected.startswith("ja"):
            direction = "to_en"
        else:
            direction = "to_ja"
    try:
        if direction == "to_en":
            src, dest, flag = "ja", "en", "🇯🇵 → 🇺🇸"
        else:
            src, dest, flag = "en", "ja", "🇺🇸 → 🇯🇵"
        translated = GoogleTranslator(source=src, target=dest).translate(text)
        result = f"{translated}"
    except Exception as e:
        await interaction.followup.send("⚠️ 翻訳中にエラーが発生しました:{e}", ephemeral=ephemeral)
        return
    await interaction.followup.send(result, ephemeral=ephemeral)

@tree.command(name="auto_translate_mode", description="自動翻訳モードをチャンネルごとにON/OFFします。")
@app_commands.describe(
    direction="ON / OFF を選択"
)
@app_commands.choices(direction=[
    app_commands.Choice(name="ON", value="on"),
    app_commands.Choice(name="OFF", value="off"),
])
async def AutoTranslateModeChange(interaction: discord.Interaction, direction: str):
    channel_id = str(interaction.channel.id)
    # 現在の設定をロード
    data = load_auto_translate_settings()
    # 設定を保存
    data[channel_id] = direction
    save_auto_translate_settings(data)
    trigger_github_action(data)
    mode_text = "ON" if direction == "on" else "OFF"
    await interaction.response.send_message(
        f"🌐 このチャンネルの自動翻訳モードを **{mode_text}** に切り替えました！"
    )
# ▼ JSON 読み書き関数 ▼
def load_auto_translate_settings():
    if not os.path.exists(AUTO_TRANSLATE_FILE):
        return {}
    with open(AUTO_TRANSLATE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_auto_translate_settings(data):
    with open(AUTO_TRANSLATE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
def trigger_github_action(data):
    """GitHub Actionsに更新リクエストを送る"""
    url = f"https://api.github.com/repos/{REPO}/dispatches"
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"token {GITHUB_TOKEN}"
    }
    payload = {
        "event_type": "TranslateModeChange",
        "client_payload": {
            "data": json.dumps(data, ensure_ascii=False)
        }
    }
    r = requests.post(url, headers=headers, json=payload)
    print("GitHub Action Trigger:", r.status_code, r.text)

    
@tree.command(name="timeout", description="指定したユーザーをタイムアウトします。")
@app_commands.describe(
    user="タイムアウトするユーザー",
    minutes="タイムアウトの時間（分単位）"
)
@commands.has_permissions(moderate_members=True)
async def timeout(interaction: discord.Interaction, user: discord.Member, minutes: int):
    try:
        duration = timedelta(minutes=minutes)
        await user.timeout(duration)
        await interaction.response.send_message(
            f"✅ {user.mention} を {minutes} 分間タイムアウトしました。", ephemeral=True
        )
    except discord.Forbidden:
        await interaction.response.send_message("❌ 権限が不足しています。", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"⚠️ エラーが発生しました: {e}", ephemeral=True)

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
    # ▼ 自動翻訳 ON/OFF の読み取り
    channel_id = str(message.channel.id)
    settings = load_auto_translate_settings()
    is_auto = settings.get(channel_id) == "on"
    if is_auto:
        text = message.content.strip()
        if not text:
            return
        # 言語判定
        try:
            detected = detect(text)
        except:
            return
        # 翻訳方向を決定
        if detected.startswith("ja"):
            src, dest, flag = "ja", "en", "🇯🇵 → 🇺🇸"
        else:
            src, dest, flag = "en", "ja", "🇺🇸 → 🇯🇵"
        # 翻訳
        try:
            translated = GoogleTranslator(source=src, target=dest).translate(text)
        except:
            return
        # 返信形式で送信
        await message.reply(f"{translated}", mention_author=False)

                
TOKEN = os.getenv("DISCORD_TOKEN")
# Web サーバの立ち上げ
keep_alive()
client.run(TOKEN)
