import requests
import time

print("🚀 Script de test Telegram démarré...")

BOT_TOKEN = "8331971296:AAHlF5iATHcjgGcM0RHekYfp0ziWT1DrSxc"
CHAT_ID = "7971098484"
message = "✅ Test depuis Render (bot en ligne)"

url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
params = {"chat_id": CHAT_ID, "text": message}

try:
    r = requests.get(url, params=params)
    print("📩 Requête envoyée à Telegram")
    print("🔍 Réponse API :", r.text)
except Exception as e:
    print("❌ Erreur :", e)

print("⏳ Attente 30s avant arrêt...")
time.sleep(30)
print("🏁 Fin du script")
