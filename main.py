import discord
import os
from keep_alive import keep_alive
from discord import app_commands
import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry

intents=discord.Intents.all()
intents.message_content = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)
# Open-Meteo APIの設定
cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)


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
    elif message.content == "こんにちは":
        await message.channel.send("こんにちは！")
    elif client.user in message.mentions: # 話しかけられたかの判定
        await message.channel.send(f'{message.author.mention} 呼びましたか？') # 返信メッセージを送信
    elif message.content == "いいね":
        emoji ="👍"
        await message.add_reaction(emoji)
    elif message.content == "天気":
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": 35.6895,  # 東京の緯度
            "longitude": 139.6917,  # 東京の経度
            "hourly": ["temperature_2m", "precipitation", "weather_code"],
            "daily": ["weather_code", "temperature_2m_max", "temperature_2m_min"],
            "wind_speed_unit": "ms"
        }
        responses = openmeteo.weather_api(url, params=params)
        response = responses[0]
        # 最新の天気データを取得
        hourly = response.Hourly()
        temperature = hourly.Variables(0).ValuesAsNumpy()[0]
        precipitation = hourly.Variables(1).ValuesAsNumpy()[0]
        weather_code = hourly.Variables(2).ValuesAsNumpy()[0]
        daily = response.Daily()
        temp_max = daily.Variables(1).ValuesAsNumpy()[0]
        temp_min = daily.Variables(2).ValuesAsNumpy()[0]
        # Discordに天気情報を送信
        weather_message = (
            f"📍 **東京の天気情報**\n"
            f"🌡 気温: {temperature:.1f}°C\n"
            f"☔ 降水量: {precipitation:.1f} mm\n"
            f"🔢 天気コード: {weather_code}\n"
            f"🌞 最高気温: {temp_max:.1f}°C\n"
            f"❄ 最低気温: {temp_min:.1f}°C"
        )
        await message.channel.send(weather_message)


TOKEN = os.getenv("DISCORD_TOKEN")
# Web サーバの立ち上げ
keep_alive()
client.run(TOKEN)
