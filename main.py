import os
import yfinance as yf
import pandas as pd
import ta
import time
import datetime
import pytz
import warnings
from telegram import Bot
from flask import Flask
from threading import Thread

# -------- CONFIG --------
SYMBOLS = ["EURUSD=X", "GBPUSD=X", "JPY=X"]  # EUR/USD, GBP/USD, USD/JPY
INTERVAL = "1m"
RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30
PRE_SIGNAL_MARGIN = 2

TELEGRAM_TOKEN = "8331971296:AAHlF5iATHcjgGcM0RHekYfp0ziWT1DrSxc"
TELEGRAM_CHAT_ID = "7971098484"
# ------------------------

# Masquer les warnings inutiles
warnings.filterwarnings("ignore")

bot = Bot(token=TELEGRAM_TOKEN)
paris_tz = pytz.timezone("Europe/Paris")

def get_rsi(symbol):
    data = yf.download(symbol, period="2d", interval=INTERVAL)
    close_prices = data['Close']

    if isinstance(close_prices, pd.DataFrame):
        close_prices = close_prices.iloc[:, 0]

    data['RSI'] = ta.momentum.RSIIndicator(close_prices, RSI_PERIOD).rsi()
    return data['RSI'].iloc[-1]

def send_telegram(message):
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)

def start_bot():
    # Message de démarrage
    send_telegram("✅ Bot RSI démarré et en surveillance sur EUR/USD, GBP/USD et USD/JPY")
    print("Bot démarré... Surveillance RSI en cours.")

    while True:
        now = datetime.datetime.now(paris_tz)

        if 8 <= now.hour < 22:  # heures actives
            for symbol in SYMBOLS:
                rsi = get_rsi(symbol)
                heure_str = now.strftime("%H:%M:%S")

                # Pré-signal
                if RSI_OVERBOUGHT - PRE_SIGNAL_MARGIN <= rsi < RSI_OVERBOUGHT:
                    send_telegram(f"🔔 Pré-signal SURACHAT {symbol} ({rsi:.2f}) à {heure_str}")
                elif RSI_OVERSOLD < rsi <= RSI_OVERSOLD + PRE_SIGNAL_MARGIN:
                    send_telegram(f"🔔 Pré-signal SURVENTE {symbol} ({rsi:.2f}) à {heure_str}")

                # Signal clair
                if rsi >= RSI_OVERBOUGHT:
                    send_telegram(f"🚨 Signal clair SURACHAT {symbol} ({rsi:.2f}) à {heure_str}")
                elif rsi <= RSI_OVERSOLD:
                    send_telegram(f"🚨 Signal clair SURVENTE {symbol} ({rsi:.2f}) à {heure_str}")

        time.sleep(60)

# === Serveur Flask pour Render ===
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
