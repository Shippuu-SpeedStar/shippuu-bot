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
    new_activity = f"テスト"
    await client.change_presence(activity=discord.Game(new_activity))

    # スラッシュコマンドを同期
    await tree.sync()
# @client.event
# async def on_message(message):
 #   emoji ="👍"
  #  await message.add_reaction(emoji)
@tree.command(name='hello', description='Say hello to the world!') 
async def test(interaction: discord.Interaction): 
  await interaction.response.send_message('こんにちは！')


TOKEN = os.getenv("DISCORD_TOKEN")
# Web サーバの立ち上げ
keep_alive()
client.run(TOKEN)
