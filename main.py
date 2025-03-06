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
@tree.command(name='hello', description='こんにちは！') 
async def test(interaction: discord.Interaction): 
  await interaction.response.send_message('こんにちは！')
    
@tree.command(name='membercount', description='サーバーの人数を表示します') 
async def on_message(message):
    # message インスタンスから guild インスタンスを取得
    guild = message.guild 
    # ユーザとBOTを区別しない場合
    member_count = guild.member_count
    # ユーザのみ
    user_count = sum(1 for member in guild.members if not member.bot)
    # BOTのみ
    bot_count = sum(1 for member in guild.members if member.bot)
    await interaction.response.send(f'メンバー数：{member_count}ユーザー数：{user_count}ボット数：{bot_count}')


TOKEN = os.getenv("DISCORD_TOKEN")
# Web サーバの立ち上げ
keep_alive()
client.run(TOKEN)
