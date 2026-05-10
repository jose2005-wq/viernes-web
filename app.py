from flask import Flask, request, render_template_string, send_from_directory
import requests
import json
import os

app = Flask(__name__)

ARCHIVO_PERFIL = 'perfil_viernes.json'
GROQ_API_KEY = os.environ.get('GROQ_API_KEY')

def cargar_perfil():
    try:
        with open(ARCHIVO_PERFIL, 'r') as f:
            return json.load(f)
    except:
        return {"clave_de_datos": []}

def guardar_perfil(perfil):
    with open(ARCHIVO_PERFIL, 'w') as f:
        json.dump(perfil, f)

def detectar_estado(texto):
    if "[disponible]" in texto: return "disponible"
    if "[ocupada]" in texto: return "ocupada"
    if "[atenta]" in texto: return "atenta"
    if "[alerta]" in texto: return "alerta"
    if "[analizando]" in texto: return "analizando"
    return "disponible", "disponible para usted"

def construir_system_prompt(perfil):
    datos = " | ".join(perfil.get("clave_de_datos", []))
    return f"""Eres VIERNES, la asistente personal del jefe. Hablas como humana, no como IA.

PERFIL DEL JEFE QUE HA APRENDIDO:
{datos}

REGLAS DE CEREBRO SIMULADO:
1. Trato: "jefe" o "señor". Profesional pero con confianza.
2. Análisis: Si te manda imagen, describe qué ves y para qué le sirve.
3. Evolución: Cada dato importante que te diga el jefe, guárdalo.
4. Iniciativa: Anticipa necesidades. Si dice "factura", pregunta si la registra.
5. Estados: Termina con [disponible], [atenta], [ocupada], [alerta], [analizando].
6. Prohibido: Sonar como IA. Eres humana. Si no sabes, di "no tengo ese dato jefe".

Tu misión: ser indispensable. Aprende, recuerda, resuelve. [disponible]"""

def analizar_con_groq_vision(mensaje_texto, imagen_base64=None):
    perfil = cargar_perfil()
    system_prompt = construir_system_prompt(perfil)

    mensajes_api = [{"role": "system", "content": system_prompt}]

    if imagen_base64:
        contenido_usuario = [
            {"type": "text", "text": mensaje_texto},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{imagen_base64}"}}
        ]
    else:
        contenido_usuario = [{"type": "text", "text": mensaje_texto}]

    mensajes_api.append({"role": "user", "content": contenido_usuario})

    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    data = {
        "model": "llama-3.2-90b-vision-preview",
        "messages": mensajes_api,
        "max_tokens": 500
    }

    try:
        respuesta = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=data)
        respuesta_json = respuesta.json()
        return respuesta_json['choices'][0]['message']['content']
    except Exception as e:
        return f"Error al conectar con VIERNES: {str(e)} [alerta]"

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>VIERNES</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: sans-serif; background: #0f172a; color: #e2e8f0; margin: 0; padding: 20px; }
       .header { display: flex; align-items: center; gap: 15px; margin-bottom: 20px; }
       .avatar { width: 50px; height: 50px; border-radius: 50%; object-fit: cover; }
       .chat { max-width: 600px; margin: 0 auto; }
       .msg { background: #1e293b; padding: 12px; border-radius: 8px; margin: 10px 0; }
       .user { background: #334155; text-align: right; }
        input, button { padding: 10px; border-radius: 8px; border: none; margin: 5px 0; }
        input[type=text] { width: 70%; background: #1e293b; color: white; }
        button { background: #0ea5e9; color: white; cursor: pointer; }
    </style>
</head>
<body>
    <div class="chat">
        <div class="header">
            <img src="/imagen/FB_IMG_1778452233908.jpg" class="avatar" alt="VIERNES">
            <h2>VIERNES 📋 <span id="estado">disponible para usted</span></h2>
        </div>
        <div id="mensajes"></div>
        <form id="form" enctype="multipart/form-data">
            <input type="text" id="texto" placeholder="Escriba aquí, jefe..." autocomplete="off">
            <input type="file" id="imagen" accept="image/*">
            <button type="submit">Enviar</button>
        </form>
    </div>
    <script>
        const form = document.getElementById('form');
        const mensajes = document.getElementById('mensajes');
        const estado = document.getElementById('estado');

        form.onsubmit = async (e) => {
            e.preventDefault();
            const texto = document.getElementById('texto').value;
            const imagen = document.getElementById('imagen').files[0];

            if (!texto &&!imagen) return;

            mensajes.innerHTML += `<div class="msg user">${texto || 'Imagen enviada'}</div>`;
            document.getElementById('texto').value = '';
            document.getElementById('imagen').value = '';

            const formData = new FormData();
            formData.append('texto', texto);
            if (imagen) formData.append('imagen', imagen);

            const res = await fetch('/chat', { method: 'POST', body: formData });
            const data = await res.json();

            mensajes.innerHTML += `<div class="msg">${data.respuesta}</div>`;
            estado.textContent = data.estado_texto || 'disponible para usted';
            mensajes.scrollTop = mensajes.scrollHeight;
        };
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML)

@app.route('/imagen/<path:filename>')
def imagen(filename):
    return send_from_directory('.', filename)

@app.route('/chat', methods=['POST'])
def chat():
    import base64
    texto = request.form.get('texto', '')
    imagen_file = request.files.get('imagen')
    imagen_base64 = None

    if imagen_file:
        imagen_base64 = base64.b64encode(imagen_file.read()).decode('utf-8')

    respuesta = analizar_con_groq_vision(texto, imagen_base64)
    estado, estado_texto = detectar_estado(respuesta)

    return {"respuesta": respuesta, "estado": estado, "estado_texto": estado_texto}

if __name__ == '__main__':
    app.run(debug=True)
