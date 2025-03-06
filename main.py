import discord
import os
from keep_alive import keep_alive
from discord import app_commands

client = discord.Client(intents=discord.Intents.default())
tree = app_commands.CommandTree(client)

@client.event
async def on_ready():
    print('ログインしました')
 # アクティビティを設定
    activity = discord.Activity(name='疾風スピードスター', type=discord.ActivityType.competing)
    await client.change_presence(status=discord.Status.online, activity=activity)

    # スラッシュコマンドを同期
    await tree.sync()
# @client.event
# async def on_message(message):
 #   emoji ="👍"
  #  await message.add_reaction(emoji)
# スラッシュコマンド
@tree.command(name='hello', description='こんにちは！') 
async def test(interaction: discord.Interaction): 
  await interaction.response.send_message('こんにちは！')
@tree.command(name='membercount', description='サーバーの人数を表示します') 
async def on_message(message):
    # message インスタンスから guild インスタンスを取得
    guild = message.guild 
    # ユーザとBOTを区別しない場合
    member_count = guild.member_count
    await message.response.send_message(f'今の人数は{member_count}です')
        
# 返信する非同期関数を定義
#async def reply(message):
#    reply = f'{message.author.mention} 呼びましたか？' # 返信メッセージの作成
#    await message.channel.send(reply) # 返信メッセージを送信
@client.event
async def on_message(call_message):
    if call_message.author.bot:
        return
    if client.user in call_message.mentions: # 話しかけられたかの判定
        reply = f'{call_message.author.mention} 呼びましたか？' # 返信メッセージの作成
        await call_message.channel.send(reply) # 返信メッセージを送信
        #await reply(message) # 返信する非同期関数を実行
#async def on_message(message):
#    if message.author.bot:
#        return
#    if "こんにちは！" in message.content.lower():
#        send_message = f'{hello_message.author.mention}さん、こんにちは！'# 返信メッセージの作成


TOKEN = os.getenv("DISCORD_TOKEN")
# Web サーバの立ち上げ
keep_alive()
client.run(TOKEN)
