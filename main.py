import discord
import os
from keep_alive import keep_alive
from discord import app_commands
import asyncio
from discord.channel import VoiceChannel

intents = discord.Intents.all()
intents.message_content = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)
voiceChannel: VoiceChannel

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
        
@client.event
async def on_message(message):
    if message.author.bot:
        return
    if message.content == "こんにちは":
        await message.channel.send("こんにちは！")
    elif client.user in message.mentions: # 話しかけられたかの判定
        await message.channel.send(f'{message.author.mention} 呼びましたか？') # 返信メッセージを送信
    elif message.content == "いいね":
        emoji ="👍"
        await message.add_reaction(emoji)
    elif message.content == "疾風、来てください":
        if message.author.voice:
            global voiceChannel
            channel = message.author.voice.channel
            #await message.author.voice.channel.connect()
            voiceChannel = await VoiceChannel.connect(message.author.voice.channel)
            await message.channel.send(f"VCに参加しました: {channel.name}")
        else:
            await message.channel.send('VCに接続してから言ってください')
    elif message.content == "疾風、VC退出です！":
        voiceChannel.stop()
        await voiceChannel.disconnect()
        #await message.author.voice.channel.leave()
        await message.channel.send("ありがとうございました！")

TOKEN = os.getenv("DISCORD_TOKEN")
# Web サーバの立ち上げ
keep_alive()
client.run(TOKEN)
