import discord
import os
from keep_alive import keep_alive
from discord import app_commands
import weather
import re

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
async def member_count(message):
    help_message = discord.Embed( # Embedを定義する
                          title="Example Embed",# タイトル
                          color=0x00ff00, # フレーム色指定(今回は緑)
                          description="Example Embed for Advent Calendar", # Embedの説明文 必要に応じて
                          url="https://tamgamecreator.github.io/NO.04" # これを設定すると、タイトルが指定URLへのリンクになる
                          )
    help_message.set_author(name=client.user, # Botのユーザー名
                     url="https://tamgamecreator.github.io/NO.04", # titleのurlのようにnameをリンクにできる。botのWebサイトとかGithubとか
                     icon_url=client.user.avatar_url # Botのアイコンを設定してみる
                     )

    help_message.set_thumbnail(url="https://tamgamecreator.github.io/NO.04/data/image01.png") # サムネイルとして小さい画像を設定できる

    help_message.set_image(url="https://tamgamecreator.github.io/NO.04/data/image03.png") # 大きな画像タイルを設定できる

    help_message.add_field(name="フィールド１",value="値１") # フィールドを追加。
    help_message.add_field(name="フィールド２",value="値２")

    help_message.set_footer(text="made by nashiroaoi", # フッターには開発者の情報でも入れてみる
                     icon_url="https://tamgamecreator.github.io/update/data/Icon01.png")
    await message.channel.send(embed=help_message) # embedの送信には、embed={定義したembed名}
        
@client.event
async def on_message(message):
    reg_res = re.compile(u"Bot君、(.+)の天気は？").search(message.content)
    if message.author.bot:
        return
    elif message.content == "こんにちは":
        await message.channel.send("こんにちは！")
    elif client.user in message.mentions: # 話しかけられたかの判定
        await message.channel.send(f'{message.author.mention} 呼びましたか？') # 返信メッセージを送信
    elif message.content == "いいね":
        emoji ="👍"
        await message.add_reaction(emoji)
    elif reg_res:
        weather_message = weather.on_message(reg_res)
        await message.channel.send(weather_message)

TOKEN = os.getenv("DISCORD_TOKEN")
# Web サーバの立ち上げ
keep_alive()
client.run(TOKEN)
