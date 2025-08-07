from flask import Flask, render_template, request
import requests
import os
import json
from dotenv import load_dotenv

# Cargar variables desde .env
load_dotenv()

app = Flask(__name__)

# Clave API
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
HISTORY_FILE = "chat_history.json"

# Función para cargar historial desde el archivo JSON
def load_history():
    if not os.path.exists(HISTORY_FILE):
        return []
    with open(HISTORY_FILE, "r") as f:
        return json.load(f)

# Función para guardar historial
def save_history(history):
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f)

# Función para obtener respuesta de OpenRouter
def get_gpt_response(history):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "openai/gpt-3.5-turbo",  # puedes cambiar a gpt-4 si tu plan lo permite
        "messages": [
            {
                "role": "system",
                "content": (
                    "Act as a professional nutrition advisor. "
                    "Stay in your ROL OF PROFESIONAL NUTRITION ADVISOR."
                    "Your job is to help users with healthy meal plans, supplement advice, "
                    "nutrient information, muscle gain and fat loss strategies. "
                    "Be clear, practical, and avoid medical diagnosis. "
                    "Be kind and think step-by-step before answering."
                )
            }
        ] + history
    }

    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Error: {str(e)}"

# Ruta principal
@app.route("/", methods=["GET", "POST"])
def index():
    chat_history = load_history()
    response = ""

    if request.method == "POST":
        question = request.form["question"]
        chat_history.append({"role": "user", "content": question})
        response = get_gpt_response(chat_history)
        chat_history.append({"role": "assistant", "content": response})
        save_history(chat_history)

    return render_template("index.html", chat=chat_history)

# Ruta para reiniciar historial
@app.route("/reset")
def reset():
    save_history([])
    return "Chat history reset. <a href='/'>Volver al chat</a>"

# Iniciar app
if __name__ == "__main__":
    app.run()
