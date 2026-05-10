import os
import requests
from flask import Flask, request
from groq import Groq

app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

client = Groq(api_key=GROQ_API_KEY)

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": text})

@app.route("/", methods=["POST"])
def webhook():
    data = request.json
    message = data.get("message", {})
    chat_id = message.get("chat", {}).get("id")
    user_text = message.get("text", "")
    
    if not chat_id or not user_text:
        return "ok"
    
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "Eres VIERNES, una IA mexicana sarcástica pero útil. Responde corto y directo."
                },
                {
                    "role": "user", 
                    "content": user_text
                }
            ],
            model="llama-3.1-70b-versatile",
        )
        reply = chat_completion.choices[0].message.content
    except Exception as e:
        reply = f"Me atoré bb: {e}"
    
    send_message(chat_id, reply)
    return "ok"

@app.route("/", methods=["GET"])
def home():
    return "VIERNES está viva sin memoria 🔥"

if __name__ == "__main__":
    app.run()
