import logging
import threading
from pathlib import Path

import openmeteo_requests
import requests_cache
from openmeteo_requests.Client import OpenMeteoRequestsError
from retry_requests import retry


logger = logging.getLogger(__name__)

# Open-Meteo APIの設定
# キャッシュをweather.pyと同じ場所に保存し、起動時の作業ディレクトリに
# かかわらず同じキャッシュを利用する。
cache_path = Path(__file__).with_name("weather_cache")
cache_session = requests_cache.CachedSession(
    str(cache_path),
    expire_after=3600,
)

# 日次上限や短時間の利用制限（HTTP 429）は再試行しても改善しないため、
# サーバー側の一時障害だけを最大2回再試行する。
retry_session = retry(
    cache_session,
    retries=2,
    backoff_factor=0.5,
    status_to_retry=(500, 502, 503, 504),
)
openmeteo = openmeteo_requests.Client(session=retry_session)

# CachedSessionは複数スレッドから同時に操作せず、APIアクセスを直列化する。
_request_lock = threading.Lock()


# 緯度
citycodes_latitude = {
    "札幌": "43.0667",
    "仙台": "38.2667",
    "新潟": "37.8864",
    "さいたま": "35.9081",
    "東京": "35.6895",
    "横浜": "35.4659",
    "金沢": "36.6",
    "静岡": "34.9833",
    "名古屋": "35.1815",
    "三重": "34.7333",
    "大阪": "34.6937",
    "広島": "34.4",
    "高知": "33.5048",
    "福岡": "33.6",
    "那覇": "26.2167",
    "シアトル": "47.6062",
    "ブカレスト": "44.4267",
    "シーランド公国": "51.89528",  # ここからネタ枠
    "ロンドン": "51.5085",  # ここからネタ枠
    "西表島": "24.3333",  # ここからネタ枠
    "志布志市志布志町志布志": "31.476",  # ここからネタ枠
    # ここからChat-GPTにより検索された座標
    "青森": "40.824623",
    "盛岡": "39.703531",
    "秋田": "39.718600",
    "山形": "38.240437",
    "福島": "37.750299",
    "水戸": "36.341813",
    "宇都宮": "36.565725",
    "前橋": "36.391208",
    "千葉": "35.605058",
    "富山": "36.695290",
    "福井": "36.065219",
    "甲府": "35.664158",
    "長野": "36.651289",
    "岐阜": "35.391227",
    "津": "34.730283",
    "大津": "35.004531",
    "京都": "35.021004",
    "神戸": "34.691279",
    "奈良": "34.685333",
    "和歌山": "34.226034",
    "鳥取": "35.503869",
    "松江": "35.472297",
    "岡山": "34.661772",
    "山口": "34.186121",
    "徳島": "34.065770",
    "高松": "34.340149",
    "松山": "33.841660",
    "佐賀": "33.249367",
    "長崎": "32.744839",
    "熊本": "32.789828",
    "大分": "33.238194",
    "宮崎": "31.911090",
    "鹿児島": "31.560148",
}

# 経度
citycodes_longitude = {
    "札幌": "141.35",
    "仙台": "140.8667",
    "新潟": "139.0059",
    "さいたま": "139.6566",
    "東京": "139.6917",
    "横浜": "139.6223",
    "金沢": "136.6167",
    "静岡": "138.3833",
    "名古屋": "136.9064",
    "三重": "136.5167",
    "大阪": "135.5022",
    "広島": "132.45",
    "高知": "133.4447",
    "福岡": "130.4167",
    "那覇": "127.6833",
    "シアトル": "-122.3321",
    "ブカレスト": "26.1025",
    "シーランド公国": "1.48056",  # ここからネタ枠
    "ロンドン": "-0.1257",  # ここからネタ枠
    "西表島": "123.8",  # ここからネタ枠
    "志布志市志布志町志布志": "131.1011",  # ここからネタ枠
    # ここからChat-GPTにより検索された座標
    "青森": "140.740593",
    "盛岡": "141.152667",
    "秋田": "140.102334",
    "山形": "140.363634",
    "福島": "140.467521",
    "水戸": "140.446793",
    "宇都宮": "139.883565",
    "前橋": "139.060156",
    "千葉": "140.123308",
    "富山": "137.211338",
    "福井": "136.221642",
    "甲府": "138.568449",
    "長野": "138.181224",
    "岐阜": "136.722291",
    "津": "136.508591",
    "大津": "135.868590",
    "京都": "135.755608",
    "神戸": "135.183025",
    "奈良": "135.832744",
    "和歌山": "135.167506",
    "鳥取": "134.237672",
    "松江": "133.050499",
    "岡山": "133.934675",
    "山口": "131.470500",
    "徳島": "134.559303",
    "高松": "134.043444",
    "松山": "132.765362",
    "佐賀": "130.298822",
    "長崎": "129.873756",
    "熊本": "130.741667",
    "大分": "131.612591",
    "宮崎": "131.423855",
    "鹿児島": "130.557981",
}


def on_message(reg_res):
    city_name = reg_res.group(1).strip()

    if city_name not in citycodes_latitude:
        return "そこの天気はわからないです．．．"

    # 二つの辞書の片方だけに都市が追加された場合も、例外にせず検出する。
    if city_name not in citycodes_longitude:
        logger.error("%sの経度が設定されていません。", city_name)
        return "⚠️ この地点の座標設定に問題があるため、天気を取得できません。"

    citycode_latitude = citycodes_latitude[city_name]
    citycode_longitude = citycodes_longitude[city_name]

    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": citycode_latitude,
        "longitude": citycode_longitude,
        "daily": ["temperature_2m_min", "temperature_2m_max"],
        "current": [
            "precipitation",
            "temperature_2m",
            "relative_humidity_2m",
            "wind_speed_10m",
            "wind_direction_10m",
            "cloud_cover",
            "precipitation_probability",
        ],
        "forecast_days": 1,
        "wind_speed_unit": "ms",
        # 海外都市では現地の日付を基準に最高・最低気温を取得する。
        "timezone": "auto",
    }

    try:
        with _request_lock:
            responses = openmeteo.weather_api(url, params=params)

        if not responses:
            logger.error("Open-Meteoから空のレスポンスが返されました。")
            return "⚠️ 天気情報を取得できませんでした。"

        response = responses[0]

        # 現在の天気データを取得
        current = response.Current()
        current_precipitation = current.Variables(0).Value()
        current_temperature_2m = current.Variables(1).Value()
        current_relative_humidity_2m = current.Variables(2).Value()
        current_wind_speed_10m = current.Variables(3).Value()
        current_wind_direction_10m = current.Variables(4).Value()
        current_cloud_cover = current.Variables(5).Value()
        current_precipitation_probability = current.Variables(6).Value()

        # 風向きを16方位へ変換
        wind_directions = [
            "北", "北北東", "北東", "東北東",
            "東", "東南東", "南東", "南南東",
            "南", "南南西", "南西", "西南西",
            "西", "西北西", "北西", "北北西",
        ]
        wind_index = int((current_wind_direction_10m + 11.25) / 22.5) % 16
        wind_dir_text = wind_directions[wind_index]

        # 今日の最高・最低気温を取得
        daily = response.Daily()
        daily_temperature_2m_min = daily.Variables(0).ValuesAsNumpy()[0]
        daily_temperature_2m_max = daily.Variables(1).ValuesAsNumpy()[0]

    except OpenMeteoRequestsError as error:
        error_text = str(error)

        if "Daily API request limit exceeded" in error_text:
            logger.warning("Open-Meteoの日次リクエスト上限に到達しました。")
            return (
                "⚠️ 天気情報サービスの1日あたりの利用上限に達しました。\n"
                "上限が解除されるまで、天気情報を取得できません。"
            )

        if "rate limit" in error_text.lower() or "too many requests" in error_text.lower():
            logger.warning("Open-Meteoのアクセス頻度制限に到達しました。")
            return (
                "⚠️ 天気情報へのアクセスが一時的に集中しています。\n"
                "しばらく時間を空けてからお試しください。"
            )

        logger.exception("Open-Meteo APIでエラーが発生しました。")
        return "⚠️ 天気情報サービスでエラーが発生しました。"

    except (IndexError, TypeError, ValueError, AttributeError):
        logger.exception("Open-Meteoの応答データを解析できませんでした。")
        return "⚠️ 取得した天気情報を正しく読み取れませんでした。"

    except Exception:
        logger.exception("天気情報の取得中に予期しないエラーが発生しました。")
        return "⚠️ 天気情報を取得できませんでした。"

    return (
        f"📍 **{city_name}の天気情報**\n"
        f"🌡 気温: {current_temperature_2m:.1f}°C\n"
        f"🌞 最高気温: {daily_temperature_2m_max:.1f}°C\n"
        f"❄️ 最低気温: {daily_temperature_2m_min:.1f}°C\n"
        f"💧 湿度: {current_relative_humidity_2m:.1f}%\n"
        f"☔ 降水量: {current_precipitation:.1f} mm\n"
        f"🌧️ 降水確率: {current_precipitation_probability:.1f}%\n"
        f"💨 風速: {current_wind_speed_10m:.1f} m/s\n"
        f"🧭 風向: {wind_dir_text} ({current_wind_direction_10m:.1f}°)\n"
        f"⛅ 雲量: {current_cloud_cover:.1f}%\n"
        f"-# 緯度: {citycode_latitude}° 経度: {citycode_longitude}°\n"
        "-# Weather data by Open-Meteo.com"
    )
