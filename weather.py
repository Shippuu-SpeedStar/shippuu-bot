import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry
import re
# Open-Meteo APIの設定
cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)
#緯度
citycodes_latitude = {
    "札幌": '43.0667',
    "仙台": '38.2667',
    "新潟": '37.8864',
    "東京": '35.6895',
    "金沢": '36.6',
    "名古屋": '35.1815',
    "大阪": '34.6937',
    "広島": '34.4',
    "高知": '33.5048',
    "福岡": '33.6',
    "那覇": '26.2167'
}
#経度
citycodes_longitude = {
    "札幌": '141.35',
    "仙台": '140.8667',
    "新潟": '139.0059',
    "東京": '139.6917',
    "金沢": '136.6167',
    "名古屋": '136.9064',
    "大阪": '135.5022',
    "広島": '132.45',
    "高知": '133.4447',
    "福岡": '130.4167',
    "那覇": '127.6833'
}

def on_message(reg_res):
    if reg_res.group(1) in citycodes_latitude.keys():
      citycode_latitude = citycodes_latitude[reg_res.group(1)]
      citycode_longitude = citycodes_longitude[reg_res.group(1)]
      url = "https://api.open-meteo.com/v1/forecast"
      params = {
      "latitude": citycode_latitude,  # 東京の緯度
      "longitude": citycode_longitude,  # 東京の経度
      "hourly": ["temperature_2m", "precipitation", "cloud_cover", "wind_speed_10m", "wind_direction_10m"],
        "daily": ["temperature_2m_max", "temperature_2m_min", "precipitation_probability_max"],
        "wind_speed_unit": "ms",
        "timezone": "Asia/Tokyo"
      }
      responses = openmeteo.weather_api(url, params=params)
      response = responses[0]
      # 最新の天気データを取得
      hourly = response.Hourly()
      temperature = hourly.Variables(0).ValuesAsNumpy()[0]
      precipitation = hourly.Variables(1).ValuesAsNumpy()[0]
      cloud_cover = hourly.Variables(2).ValuesAsNumpy()[0]
      wind_speed = hourly.Variables(3).ValuesAsNumpy()[0]
      wind_direction = hourly.Variables(4).ValuesAsNumpy()[0]
      
      daily = response.Daily()
      temp_max = daily.Variables(0).ValuesAsNumpy()[0]
      temp_min = daily.Variables(1).ValuesAsNumpy()[0]
      precip_prob = daily.Variables(2).ValuesAsNumpy()[0]
      # 風向きを変換
      directions = ["北", "北北東", "北東", "東北東", "東", "東南東", "南東", "南南東",
                    "南", "南南西", "南西", "西南西", "西", "西北西", "北西", "北北西"]
      wind_dir_text = directions[int((wind_direction + 11.25) / 22.5) % 16]
      # Discordに天気情報を送信
      weather_message = (
        f"📍 **{reg_res.group(1)}の天気情報**\n"
        f"🌡 気温: {temperature:.1f}°C\n"
        f"☔ 降水量: {precipitation:.1f} mm\n"
        f"☁️ 雲量: {cloud_cover:.1f}%\n"
        f"💨 風速: {wind_speed:.1f} m/s\n"
        f"🧭 風向: {wind_dir_text} ({wind_direction:.1f}°)\n"
        f"🌞 最高気温: {temp_max:.1f}°C\n"
        f"❄️ 最低気温: {temp_min:.1f}°C\n"
        f"🌧 降水確率: {precip_prob:.1f}%\n"
        f"-# 緯度: {citycode_latitude}° 経度: {citycode_longitude}°"
      )
      return weather_message
    else:
      return 'そこの天気はわからないです．．．'
