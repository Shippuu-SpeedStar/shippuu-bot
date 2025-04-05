import discord
import random

# 話題リスト
topics = [
    "今日は何食べた？🍽",
    "最近ハマってる飲み物ある？☕",
    "今、何のゲームしてる？🎮",
    "最近観たアニメ・映画は？📺",
    "好きなお菓子は？🍫",
    "寝る前にやることってある？🛏",
    "最近ちょっと嬉しかったことある？😊",
    "明日は何をする予定？📅",
    "好きな季節はいつ？🌸☀🍁❄",
    "今行ってみたい場所は？🗺",
    "最近買ったもので良かったものは？🛍",
    "よく使うアプリは？📱",
    "好きな音楽ジャンルは？🎧",
    "理想の休日の過ごし方は？🌞",
    "学校・仕事終わりにすることって何？🎒💼",
    "もし一日だけ透明人間になれたら何する？👻",
    "好きなキャラクターは？🧸",
    "昔ハマってたことって何？🕰",
    "最近『おおっ！』って思ったことある？😮",
    "好きな動物は？🐶🐱",
    "1億円あったら何に使う？💸",
    "苦手な食べ物は？😖",
    "今日の気分を一言で表すと？💭",
    "無人島に1つだけ持っていくなら？🏝",
    "今、部屋にあるもので一番好きなものは？🛋",
    "最近寝不足？それとも寝すぎ？😪",
    "ゲーム内でのマイルーティンある？🔁",
    "好きなジャンルは？（RPG、FPSなど）📚",
    "今日の季節感、100点満点中何点？📊",
    "今日を10点満点で評価すると？📊"
]

def on_message(reg_res):
  topic = random.choice(topics)
  return f"💬 今日の話題はこちら！\n>>> {topic}"
