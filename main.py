import discord
import os
from keep_alive import keep_alive
# スラッシュコマンド
from discord import app_commands
# 天気予報
import urllib.request
import json
import re

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)
# 天気予報
citycode = '016010'
#resp = urllib.request.urlopen('https://www.jma.go.jp/bosai/forecast/data/forecast/%s'%citycode.json).read()
resp = urllib.request.urlopen('https://www.jma.go.jp/bosai/forecast/data/forecast/016010.json').read()
resp = json.loads(resp.decode('utf-8'))

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
async def on_message(message):
    # message インスタンスから guild インスタンスを取得
    guild = message.guild 
    # ユーザとBOTを区別しない場合
    member_count = guild.member_count
    await message.response.send_message(f'今の人数は{member_count}です')

#@client.event
#async def on_message(call_message):
#    if call_message.author != client.user:
#        if client.user in call_message.mentions: # 話しかけられたかの判定
#            reply = f'{call_message.author.mention} 呼びましたか？' # 返信メッセージの作成
#            await call_message.channel.send(reply) # 返信メッセージを送信
        
@client.event
async def react_message(message):
    if message.author.bot:
        return
    elif message.content == "こんにちは":
        await message.channel.send("こんにちは！")
    elif client.user in message.mentions: # 話しかけられたかの判定
        await message.channel.send(f'{message.author.mention} 呼びましたか？') # 返信メッセージを送信
    elif message.content == "いいね":
        emoji ="👍"
        await message.add_reaction(emoji)
    elif message.content == "Bot君、札幌の天気は？":
        msg = resp['location']['city']
        msg += "の天気は、\n"
        for f in resp['forecasts']:
            msg += f['dateLabel'] + "が" + f['telop'] + "\n"
            msg += "です。"
            await client.send_message(message.channel, message.author.mention + msg)

TOKEN = os.getenv("DISCORD_TOKEN")
# Web サーバの立ち上げ
keep_alive()
client.run(TOKEN)
