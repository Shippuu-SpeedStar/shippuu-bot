from flask import Flask, jsonify
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "I'm alive"

@app.route("/ping") 
def ping(): 
    return jsonify({"status": "online"}), 200

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()
