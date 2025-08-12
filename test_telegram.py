import requests

# Remplace par tes infos
TOKEN = "8331971296:AAHlF5iATHcjgGcM0RHekYfp0ziWT1DrSxc"  # Ton token BotFather
CHAT_ID = "7971098484"  # Ton chat_id numérique
MESSAGE = "📢 Test direct depuis Render 🚀"

url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
payload = {"chat_id": CHAT_ID, "text": MESSAGE}

print("📡 Envoi du message...")
response = requests.post(url, data=payload)
print("📬 Réponse API Telegram :", response.json())
