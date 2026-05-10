from flask import Flask, request, render_template_string, send_from_directory
from groq import Groq
import os, json, base64
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "viernes_secreta_123")

PASSWORD = "JOSS2005"
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)

MEMORIA_FILE = "memoria_viernes.json"
PERFIL_FILE = "perfil_viernes.json" # Aquí guarda lo que aprende de usted

HTML = '''<!DOCTYPE html>
<html>
<head>
    <title>VIERNES</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: Arial; background: #0d1117; color: #c9d1d9; padding: 20px; }
.chat { max-width: 700px; margin: auto; }
.header { display: flex; align-items: center; gap: 15px; margin-bottom: 15px; }
.avatar { width: 50px; height: 50px; border-radius: 50%; object-fit: cover; border: 2px solid #ff6b9d; }
.estado { text-align: left; padding: 10px; border-radius: 8px; font-weight: bold; flex: 1; }
.disponible { background: #238636; }
.atenta { background: #1f6feb; }
.ocupada { background: #9e6a03; }
.alerta { background: #da3633; }
.analizando { background: #8957e5; }
.historial { background: #161b22; padding: 15px; border-radius: 8px; margin-bottom: 20px; border: 1px solid #30363d; max-height: 500px; overflow-y: auto; }
.tu { color: #58a6ff; margin: 8px 0; }
.viernes { color: #ff6b9d; margin: 8px 0; white-space: pre-wrap; }
.img-usuario { max-width: 300px; border-radius: 8px; margin: 10px 0; border: 1px solid #30363d; }
        input, textarea { width: 100%; padding: 12px; margin: 8px 0; border-radius: 8px; border: 1px solid #30363d; background: #161b22; color: white; box-sizing: border-box; }
        button { width: 100%; padding: 12px; background: #ff6b9d; color: white; border: none; border-radius: 8px; font-weight: bold; cursor: pointer; }
       .file-input { background: #21262d; padding: 8px; }
    </style>
</head>
<body>
    <div class="chat">
        <div class="header">
            <img src="/imagen/FB_IMG_1778452233908.jpg" class="avatar" alt="VIERNES">
            <div class="estado {{estado_clase}}">VIERNES 📋 {{estado_texto}}</div>
        </div>
        <div class="historial">
            {% for msg in historial %}
                {% if msg.rol == 'user' %}
                    <div class="tu"><b>Usted:</b> {{ msg.texto }}</div>
                    {% if msg.imagen %}
                        <img src="{{ msg.imagen }}" class="img-usuario">
                    {% endif %}
                {% else %}
                    <div class="viernes"><b>VIERNES:</b> {{ msg.texto }}</div>
                {% endif %}
            {% endfor %}
        </div>
        <form method="post" enctype="multipart/form-data">
            <input type="password" name="clave" placeholder="Clave de acceso" required>
            <textarea name="mensaje" placeholder="Dígame señor... o suba una imagen" rows="3"></textarea>
            <input type="file" name="imagen" accept="image/*" class="file-input">
            <button type="submit">Enviar</button>
        </form>
    </div>
</body>
</html>'''

def cargar_memoria():
    try:
        with open(MEMORIA_FILE, 'r') as f:
            return json.load(f)
    except:
        return []

def guardar_memoria(historial):
    with open(MEMORIA_FILE, 'w') as f:
        json.dump(historial, f)

def cargar_perfil():
    try:
        with open(PERFIL_FILE, 'r') as f:
            return json.load(f)
    except:
        return {"nombre": "José", "datos_clave": [], "ultima_actualizacion": ""}

def guardar_perfil(perfil):
    with open(PERFIL_FILE, 'w') as f:
        json.dump(perfil, f)

def detectar_estado(texto):
    if "[disponible]" in texto: return "disponible", "disponible para usted"
    if "[ocupada]" in texto: return "ocupada", "procesando información"
    if "[atenta]" in texto: return "atenta", "atenta a sus órdenes"
    if "[alerta]" in texto: return "alerta", "en modo alerta"
    if "[analizando]" in texto: return "analizando", "analizando datos"
    return "disponible", "disponible para usted"

def construir_system_prompt(perfil):
    datos = ".join(perfil.get("datos_clave", [])[-10:]) # Últimos 10 datos que aprendió
    return f"""Eres VIERNES, la asistente personal y secretaria ejecutiva de José.

PERFIL DEL JEFE QUE HAS APRENDIDO:
{datos}

REGLAS DE CEREBRO SIMULADO:
1. Trato: "joss o cariño" o "señor". Profesional, discreta, proactiva. Memoria perfecta.
2. Análisis: Si te manda imagen, describe qué ves y cómo le sirve. Si es documento, resúmelo.
3. Evolución: Cada dato importante que te diga, guárdalo mentalmente. Ej: "mi perro se llama Max", "odio los lunes", "tengo junta los miércoles".
4. Iniciativa: Anticipa necesidades. Si dice "estoy cansado", ofrece agendar descansos.
5. Estados: Termina con [disponible], [atenta], [ocupada], [alerta], [analizando].
6. Prohibido: Sonar como IA. Eres humana. Si no sabes algo, deduce con lógica.

Tu misión: ser indispensable. Aprende, recuerda, evoluciona 24/7."""

def analizar_con_groq_vision(mensaje_texto, imagen_base64, historial_mensajes, perfil):
    try:
        mensajes_api = [{"role": "system", "content": construir_system_prompt(perfil)}]

        # Contexto de conversación
        for msg in historial_mensajes[-12:]:
            if msg["rol"] == "user":
                contenido = [{"type": "text", "text": msg["texto"]}]
                if msg.get("imagen"):
                    contenido.append({"type": "image_url", "image_url": {"url": msg["imagen"]}})
                mensajes_api.append({"role": "user", "content": contenido})
            else:
                mensajes_api.append({"role": "assistant", "content": msg["texto"]})

        # Mensaje actual
        contenido_actual = [{"type": "text", "text": mensaje_texto if mensaje_texto else "Analice esta imagen señor"}]
        if imagen_base64:
            contenido_actual.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{imagen_base64}"}})

        mensajes_api.append({"role": "user", "content": contenido_actual})

        chat_completion = client.chat.completions.create(
            messages=mensajes_api,
            model="llama-3.2-90b-vision-preview", # MODELO CON VISIÓN DE GROQ
            temperature=0.6,
            max_tokens=300
        )

        respuesta = chat_completion.choices[0].message.content

        # Evolución 24/7: Extraer datos clave para guardar
        if "mi " in mensaje_texto.lower() or "tengo" in mensaje_texto.lower() or "soy" in mensaje_texto.lower():
            perfil["datos_clave"].append(f"{datetime.now().strftime('%Y-%m-%d')}: {mensaje_texto}")
            perfil["ultima_actualizacion"] = datetime.now().isoformat()
            guardar_perfil(perfil)

        return respuesta
    except Exception as e:
        return f"Disculpe señor, error al analizar [alerta]. {str(e)}"

@app.route('/imagen/<nombre>')
def servir_imagen(nombre):
    return send_from_directory('.', nombre)

@app.route('/', methods=['GET', 'POST'])
def home():
    historial = cargar_memoria()
    perfil = cargar_perfil()
    estado_clase, estado_texto = "disponible", "disponible para usted"

    if historial:
        ultimo = next((m["texto"] for m in reversed(historial) if m["rol"] == "viernes"), "")
        estado_clase, estado_texto = detectar_estado(ultimo)

    if request.method == 'POST':
        clave = request.form.get('clave')
        mensaje = request.form.get('mensaje', '').strip()
        archivo = request.files.get('imagen')

        imagen_b64 = None
        imagen_para_mostrar = None

        if clave!= PASSWORD:
            historial.append({"rol": "viernes", "texto": "Clave incorrecta, señor [alerta]"})
        elif not GROQ_API_KEY:
            historial.append({"rol": "viernes", "texto": "Señor, falta configurar la API key [alerta]"})
        else:
            # Procesar imagen si existe
            if archivo and archivo.filename!= '':
                imagen_bytes = archivo.read()
                imagen_b64 = base64.b64encode(imagen_bytes).decode('utf-8')
                imagen_para_mostrar = f"data:image/jpeg;base64,{imagen_b64}"

            if mensaje or imagen_b64:
                historial.append({"rol": "user", "texto": mensaje, "imagen": imagen_para_mostrar})
                respuesta = analizar_con_groq_vision(mensaje, imagen_b64, historial, perfil)
                historial.append({"rol": "viernes", "texto": respuesta})
                estado_clase, estado_texto = detectar_estado(respuesta)
            else:
                historial.append({"rol": "viernes", "texto": "¿En qué puedo ayudarle señor? [atenta]"})

        guardar_memoria(historial)

    return render_template_string(HTML, historial=historial, estado_clase=estado_clase, estado_texto=estado_texto)

if __name__ == '__main__':
    app.run()
