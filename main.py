import discord
import os
from keep_alive import keep_alive
from discord import app_commands
import weather
import re
import asyncio
import random

intents=discord.Intents.all()
intents.message_content = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

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
async def omikuji_command(message):
    choice = random.choice(['大吉','中吉', '吉', '小吉','末吉', '凶', '大凶'])
    await message.response.send_message(f"あなたの今日の運勢は **{choice}** です!")
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
    elif reg_res:
        weather_message = weather.on_message(reg_res)
        await message.channel.send(weather_message)

TOKEN = os.getenv("DISCORD_TOKEN")
# Web サーバの立ち上げ
keep_alive()
client.run(TOKEN)
