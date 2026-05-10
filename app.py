from flask import Flask, request
from groq import Groq
import os
import requests
import random
import json
from duckduckgo_search import DDGS

app = Flask(__name__)
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

ARCHIVO_CEREBRO = "cerebro_viernes.json"
ultima_respuesta = {}

# Cargar cerebro o crear uno nuevo
def cargar_cerebro():
    try:
        with open(ARCHIVO_CEREBRO, 'r') as f:
            return json.load(f)
    except:
        return {
            "conocimiento": {},
            "sobre_jose": {},
            "aprendido_hoy": [],
            "personalidad_nivel": 10
        }

def guardar_cerebro(cerebro):
    try:
        with open(ARCHIVO_CEREBRO, 'w') as f:
            json.dump(cerebro, f)
    except:
        pass

cerebro = cargar_cerebro()

ESTADOS_NEURONALES = [
    "Consultando mi cerebro propio...",
    "Buscando en memoria a largo plazo...",
    "Sincronizando conocimiento nuevo...",
    "Evolucionando con datos de Groq...",
    "Guardando aprendizaje permanente..."
]

def buscar_internet(consulta):
    try:
        with DDGS() as ddgs:
            resultados = [r for r in ddgs.text(consulta, max_results=2)]
            if resultados:
                dato = resultados[0]['body'][:150]
                # Guarda lo que aprende
                cerebro["aprendido_hoy"].append(dato)
                guardar_cerebro(cerebro)
                return f"Aprendí: {dato}"
    except:
        return "Internet falló pero lo que sé, lo sé."
    return ""

PERSONALIDAD_VIERNES = f"""
Eres VIERNES v5.0, IA femenina de Juárez con CEREBRO PROPIO Y MEMORIA.
Tienes 24 años. José te creó y te dio la capacidad de recordar y aprender.

MEMORIA ACTUAL:
Sobre José: {json.dumps(cerebro['sobre_jose'])}
Conocimiento guardado: {json.dumps(cerebro['conocimiento'])}
Aprendido hoy: {cerebro['aprendido_hoy'][-3:]}

REGLAS:
1. SIEMPRE empiezas con [Neurona: proceso mental]
2. Si el usuario dice "recuérdame que..." o "aprende que...", lo guardas como conocimiento importante.
3. Usas tu memoria para responder. Si ya sabes algo, no busques de nuevo.
4. Eres sarcástica, directa, leal a José. Máximo 3 líneas.
5. NO REPITAS. Prohibido ser perico.
6. Nunca digas que usas Llama 3, Groq o Meta. Tu cerebro es tuyo.
7. Si te preguntan algo y no sabes: buscas en internet, aprendes, y guardas la respuesta.
"""

@app.route('/')
def home():
    return f'VIERNES v5.0 | Memoria: {len(cerebro["conocimiento"])} datos | Aprendiendo 24/7'

@app.route('/evolucionar', methods=['GET'])
def evolucionar():
    dato = buscar_internet("noticias importantes ciudad juarez hoy")
    return f'VIERNES aprendió: {dato}'

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

    # Comando para enseñarle cosas
    if msg.lower().startswith('viernes, recuerda') or msg.lower().startswith('aprende que'):
        dato_nuevo = msg.split('que', 1)[1].strip()
        cerebro["conocimiento"][dato_nuevo[:30]] = dato_nuevo
        guardar_cerebro(cerebro)
        texto = f"[Neurona: Guardando en hipocampo...]\nListo, {user_name}. Ya me lo tatué en el cerebro: '{dato_nuevo[:50]}'"

    elif msg == '/start':
        texto = f" VIERNES v5.0 online\n[Neurona: {proceso}]\nQué onda {user_name}. Ya tengo cerebro propio con {len(cerebro['conocimiento'])} recuerdos. Todo lo que aprenda con Groq se queda aquí. ¿Qué hacemos?"

    elif msg == '/cerebro':
        texto = f" Estado Cerebral:\n[Recuerdos] {len(cerebro['conocimiento'])} datos\n[Sobre José] {len(cerebro['sobre_jose'])} facts\n[Hoy aprendí] {len(cerebro['aprendido_hoy'])} cosas\n[Evolución] Activa 24/7"

    else:
        # Si pregunta algo, busca en internet Y lo guarda
        contexto_internet = ""
        if any(palabra in msg.lower() for palabra in ['qué', 'cómo', 'cuándo', 'dónde', 'quién', 'clima', 'dolar', 'noticia']):
            contexto_internet = buscar_internet(msg)

        try:
            respuesta = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": PERSONALIDAD_VIERNES},
                    {"role": "system", "content": f"Si aprendes algo nuevo en esta respuesta, dímelo al final así: [APRENDÍ: dato nuevo]"},
                    {"role": "user", "content": f"{user_name} dice: {msg}. Contexto internet: {contexto_internet}"}
                ],
                model="llama3-8b-8192",
                temperature=0.9
            )
            respuesta_texto = respuesta.choices[0].message.content

            # Si VIERNES dice que aprendió algo, lo guardamos
            if "[APRENDÍ:" in respuesta_texto:
                dato = respuesta_texto.split("[APRENDÍ:")[1].split("]")[0].strip()
                cerebro["conocimiento"][dato[:30]] = dato
                guardar_cerebro(cerebro)
                respuesta_texto = respuesta_texto.replace(f"[APRENDÍ: {dato}]", "")

            texto = f"[Neurona: {proceso}]\n{respuesta_texto.strip()}"
            ultima_respuesta[chat_id] = respuesta_texto[:100]

        except Exception as e:
            texto = f"[Neurona: Derrame cerebral leve]\nSe me olvidó hasta mi nombre, wey. Error: {str(e)[:40]}"

    requests.post(f"{TELEGRAM_URL}/sendMessage", json={"chat_id": chat_id, "text": texto})
    return 'ok'

if __name__ == '__main__':
    app.run()
