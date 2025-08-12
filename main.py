import yfinance as yf
import pandas as pd
import ta
import time
import datetime
import pytz
import warnings
from telegram import Bot

# -------- CONFIG --------
SYMBOLS = ["EURUSD=X", "GBPUSD=X", "JPY=X"]  # Paires à surveiller
INTERVAL = "1m"          # Intervalle de 1 minute
RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30
PRE_SIGNAL_MARGIN = 2    # marge avant le vrai signal
TELEGRAM_TOKEN = "8331971296:AAHlF5iATHcjgGcM0RHekYfp0ziWT1DrSxc"
TELEGRAM_CHAT_ID = "7971098484"
# ------------------------

# Ignorer les warnings inutiles
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

bot = Bot(token=TELEGRAM_TOKEN)
paris_tz = pytz.timezone("Europe/Paris")

def get_rsi(symbol):
    data = yf.download(symbol, period="2d", interval=INTERVAL)
    close_prices = data['Close']
    if isinstance(close_prices, pd.DataFrame):
        close_prices = close_prices.iloc[:, 0]  # Garde juste la première colonne
    data['RSI'] = ta.momentum.RSIIndicator(close_prices, RSI_PERIOD).rsi()
    return data['RSI'].iloc[-1]

def send_telegram(message):
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)

# Message de démarrage
send_telegram("🚀 Bot RSI démarré avec succès sur Render ! Surveillance : EUR/USD, GBP/USD, USD/JPY")

print("Bot démarré... Surveillance RSI en cours.")

while True:
    now = datetime.datetime.now(paris_tz)
    if 8 <= now.hour < 22:  # heures actives
        for symbol in SYMBOLS:
            try:
                rsi = get_rsi(symbol)
                heure_str = now.strftime("%H:%M:%S")
                print(f"{heure_str} | {symbol} | RSI: {rsi:.2f}")

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

            except Exception as e:
                print(f"Erreur pour {symbol} : {e}")
    else:
        print(f"{now.strftime('%H:%M:%S')} | Marché inactif. En pause.")

    time.sleep(60)
