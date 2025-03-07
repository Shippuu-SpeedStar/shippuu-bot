import discord
import os
from keep_alive import keep_alive
from discord import app_commands
#天気
import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


#天気予報
# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

# Make sure all required weather variables are listed here
# The order of variables in hourly or daily is important to assign them correctly below
url = "https://api.open-meteo.com/v1/forecast"
params = {
	"latitude": 35.6895,
	"longitude": 139.6917,
	"hourly": "precipitation",
	"daily": ["temperature_2m_max", "temperature_2m_min"],
	"timezone": "Asia/Tokyo",
	"forecast_days": 3
}
responses = openmeteo.weather_api(url, params=params)

# Process first location. Add a for-loop for multiple locations or weather models
response = responses[0]
print(f"Coordinates {response.Latitude()}°N {response.Longitude()}°E")
print(f"Elevation {response.Elevation()} m asl")
print(f"Timezone {response.Timezone()} {response.TimezoneAbbreviation()}")
print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")












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
    elif message.content == "天気":
        # Process hourly data. The order of variables needs to be the same as requested.
        hourly = response.Hourly()
        hourly_precipitation = hourly.Variables(0).ValuesAsNumpy()
        
        hourly_data = {"date": pd.date_range(
            start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
            end = pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
            freq = pd.Timedelta(seconds = hourly.Interval()),
            inclusive = "left"
        )}
        hourly_data["precipitation"] = hourly_precipitation
        hourly_dataframe = pd.DataFrame(data = hourly_data)
        await message.send(hourly_dataframe)


TOKEN = os.getenv("DISCORD_TOKEN")
# Web サーバの立ち上げ
keep_alive()
client.run(TOKEN)
