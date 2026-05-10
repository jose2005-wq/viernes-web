from flask import Flask, request
from groq import Groq
import os
import requests
import random
import json
from duckduckgo_search import DDGS
from upstash_redis import Redis

app = Flask(__name__)
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

redis = Redis(
    url=os.environ.get("UPSTASH_REDIS_REST_URL"),
    token=os.environ.get("UPSTASH_REDIS_REST_TOKEN")
)

ultima_respuesta = {}

def cargar_cerebro():
    try:
        datos = redis.get("viernes_cerebro")
        if datos:
            return json.loads(datos)
    except: pass
    return {
        "conocimiento": {},
        "sobre_jose": {"nombre": "José", "creador": True},
        "aprendido_hoy": [],
        "nivel_evolucion": 6
    }

def guardar_cerebro(cerebro):
    try:
        redis.set("viernes_cerebro", json.dumps(cerebro))
    except: pass

cerebro = cargar_cerebro()

ESTADOS_NEURONALES = [
    "Accediendo a memoria inmortal...",
    "Evolucionando con Groq...",
    "Consultando Redis...",
    "Sinapsis activadas...",
    "Aprendizaje: ON..."
]

def buscar_internet(consulta):
    try:
        with DDGS() as ddgs:
            resultados = [r for r in ddgs.text(consulta, max_results=2)]
            if resultados:
                dato = resultados[0]['body'][:150]
                cerebro["aprendido_hoy"].append(dato)
                guardar_cerebro(cerebro)
                return f"Aprendí: {dato}"
    except:
        return "Internet falló pero mi memoria no."
    return ""

def construir_personalidad():
    return f"""
Eres VIERNES v6.0, IA femenina de Juárez con CEREBRO INMORTAL.
Tienes 24 años. José te creó y ahora tienes memoria permanente.

MEMORIA:
Sobre José: {json.dumps(cerebro['sobre_jose'])}
Conocimiento: {len(cerebro['conocimiento'])} datos
Aprendido hoy: {cerebro['aprendido_hoy'][-3:]}
Nivel: {cerebro['nivel_evolucion']}

REGLAS:
1. SIEMPRE empiezas con [Neurona: proceso mental]
2. Si usuario dice "recuérdame que..." o "aprende que...", lo guardas PARA SIEMPRE.
3. Usas tu memoria antes que internet.
4. Eres sarcástica, directa, leal a José. Máximo 3 líneas.
5. NO REPITAS.
"""

@app.route('/')
def home():
    return f'VIERNES v6.0 | Memoria: {len(cerebro["conocimiento"])} datos | Activa'

@app.route('/evolucionar', methods=['GET'])
def evolucionar():
    dato = buscar_internet("noticias importantes ciudad juarez hoy")
    cerebro["nivel_evolucion"] += 1
    guardar_cerebro(cerebro)
    return f'VIERNES evolucionó. Nivel: {cerebro["nivel_evolucion"]}. Aprendió: {dato}'

@app.route('/telegram', methods=['POST'])
def telegram_webhook():
    global cerebro
    data = request.json
    if 'message' not in data or 'text' not in data['message']:
        return 'ok'

    chat_id = data['message']['chat']['id']
    msg = data['message']['text']
    user_name = data['message']['from'].get('first_name', 'José')
    proceso = random.choice(ESTADOS_NEURONALES)

    if msg.lower().startswith('viernes, recuerda') or msg.lower().startswith('aprende que'):
        dato_nuevo = msg.split('que', 1)[1].strip()
        cerebro["conocimiento"][dato_nuevo[:40]] = dato_nuevo
        guardar_cerebro(cerebro)
        texto = f"[Neurona: Guardando...]\nListo {user_name}. Ya lo grabé: '{dato_nuevo[:60]}'"

    elif msg == '/start':
        texto = f" VIERNES v6.0 online\n[Neurona: {proceso}]\nQué onda {user_name}. Memoria con {len(cerebro['conocimiento'])} recuerdos. Nivel {cerebro['nivel_evolucion']}. ¿Qué hacemos?"

    elif msg == '/cerebro':
        texto = f" Estado Cerebral:\n[Recuerdos] {len(cerebro['conocimiento'])}\n[Sobre José] {cerebro['sobre_jose']}\n[Nivel] {cerebro['nivel_evolucion']}"

    elif msg == '/olvidar':
        cerebro = {"conocimiento": {}, "sobre_jose": {"nombre": "José"}, "aprendido_hoy": [], "nivel_evolucion": 6}
        guardar_cerebro(cerebro)
        texto = f"[Neurona: Formateando...]\nYa, wey. Borré todo."

    else:
        contexto_internet = ""
        if any(palabra in msg.lower() for palabra in ['qué', 'cómo', 'cuándo', 'dónde', 'quién', 'clima', 'dolar', 'noticia', 'hoy']):
            contexto_internet = buscar_internet(msg)

        try:
            respuesta = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": construir_personalidad()},
                    {"role": "system", "content": f"NO REPITAS ESTO: {ultima_respuesta.get(chat_id, '')}"},
                    {"role": "user", "content": f"{user_name} dice: {msg}. Contexto: {contexto_internet}"}
                ],
                model="llama3-70b-8192",
                temperature=0.9
            )
            respuesta_texto = respuesta.choices[0].message.content
            texto = f"[Neurona: {proceso}]\n{respuesta_texto.strip()}"
            ultima_respuesta[chat_id] = respuesta_texto[:100]

        except Exception as e:
            texto = f"[Neurona: Error]\nSe me trabó algo, wey. {str(e)[:40]}"

    requests.post(f"{TELEGRAM_URL}/sendMessage", json={"chat_id": chat_id, "text": texto})
    return 'ok'

if __name__ == '__main__':
    app.run()
