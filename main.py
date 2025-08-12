import yfinance as yf
import pandas as pd
import ta
import time
import datetime
import pytz
from telegram import Bot

# -------- CONFIG --------
SYMBOL = "BTC-USD"       # Actif à surveiller
INTERVAL = "1m"          # Intervalle de 1 minute
RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30
PRE_SIGNAL_MARGIN = 2    # marge avant le vrai signal
TELEGRAM_TOKEN = "TON_TELEGRAM_BOT_TOKEN"
TELEGRAM_CHAT_ID = "TON_CHAT_ID"
# ------------------------

bot = Bot(token=TELEGRAM_TOKEN)
paris_tz = pytz.timezone("Europe/Paris")

def get_rsi():
    data = yf.download(SYMBOL, period="2d", interval=INTERVAL)
    
    # Récupérer uniquement les prix de clôture
    close_prices = data['Close']
    if isinstance(close_prices, pd.DataFrame):
        close_prices = close_prices.iloc[:, 0]  # On garde juste la première colonne

    # Calcul du RSI
    data['RSI'] = ta.momentum.RSIIndicator(close_prices, RSI_PERIOD).rsi()
    rsi_value = data['RSI'].iloc[-1]
    return rsi_value

def send_telegram(message):
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)

print("Bot démarré... Surveillance RSI en cours.")

while True:
    now = datetime.datetime.now(paris_tz)
    if 8 <= now.hour < 22:  # heures actives
        rsi = get_rsi()
        heure_str = now.strftime("%H:%M:%S")
        print(f"{heure_str} | RSI: {rsi:.2f}")

        # Pré-signal
        if RSI_OVERBOUGHT - PRE_SIGNAL_MARGIN <= rsi < RSI_OVERBOUGHT:
            send_telegram(f"🔔 Pré-signal SURACHAT détecté ({rsi:.2f}) à {heure_str}")
        elif RSI_OVERSOLD < rsi <= RSI_OVERSOLD + PRE_SIGNAL_MARGIN:
            send_telegram(f"🔔 Pré-signal SURVENTE détecté ({rsi:.2f}) à {heure_str}")

        # Signal clair
        if rsi >= RSI_OVERBOUGHT:
            send_telegram(f"🚨 Signal clair SURACHAT ({rsi:.2f}) à {heure_str}")
        elif rsi <= RSI_OVERSOLD:
            send_telegram(f"🚨 Signal clair SURVENTE ({rsi:.2f}) à {heure_str}")

    else:
        print(f"{now.strftime('%H:%M:%S')} | Marché inactif. En pause.")

    time.sleep(60)
