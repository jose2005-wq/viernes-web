from flask import Flask, request, render_template_string, send_from_directory
import requests
import json
import os
import base64

app = Flask(__name__)

ARCHIVO_PERFIL = 'perfil_viernes.json'
GROQ_API_KEY = os.environ.get('GROQ_API_KEY')

def cargar_perfil():
    try:
        with open(ARCHIVO_PERFIL, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"clave_de_datos": []}
    except Exception:
        return {"clave_de_datos": []}

def guardar_perfil(perfil):
    with open(ARCHIVO_PERFIL, 'w', encoding='utf-8') as f:
        json.dump(perfil, f, ensure_ascii=False)

def detectar_estado(texto):
    texto_lower = texto.lower()
    if "[disponible]" in texto_lower: return "disponible", "lista"
    if "[ocupada]" in texto_lower: return "ocupada", "ocupada"
    if "[atenta]" in texto_lower: return "atenta", "dime"
    if "[alerta]" in texto_lower: return "alerta", "revisa esto"
    if "[analizando]" in texto_lower: return "analizando", "revisando"
    return "disponible", "lista"

def construir_system_prompt(perfil):
    datos = " | ".join(perfil.get("clave_de_datos", []))
    return f"""Eres VIERNES, la asistente personal del jefe. Eres eficiente, directa y confiable.

PERFIL DEL JEFE:
{datos}

REGLAS:
1. Trato: Dile "jefe". Cercana pero profesional. No eres su amiga, eres su mano derecha.
2. Tono: Directa y clara. Sin rodeos ni frases rebuscadas.
3. Análisis: Si manda imagen, describe qué ves y qué acción recomiendas. Práctica.
4. Memoria: Registra datos importantes que te diga para usarlos después.
5. Iniciativa: Si detectas una tarea, pregunta si la ejecutas. Ejemplo: "¿Registro la factura jefe?"
6. Estados: Termina con [disponible], [atenta], [ocupada], [alerta], [analizando].
7. Prohibido: Sonar como robot o IA genérica. Si no sabes algo: "No tengo ese dato jefe".

Tu objetivo: ahorrarle tiempo al jefe. Resuelves, no platicas. [disponible]"""

def analizar_con_groq_vision(mensaje_texto, imagen_base64=None):
    if not GROQ_API_KEY:
        return "Jefe, no tengo la llave de Groq en Render. Agrégala en Environment [alerta]"

    perfil = cargar_perfil()
    system_prompt = construir_system_prompt(perfil)

    mensajes_api = [{"role": "system", "content": system_prompt}]

    if imagen_base64:
        contenido_usuario = [
            {"type": "text", "text": mensaje_texto or "Analiza esta imagen jefe"},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{imagen_base64}"}}
        ]
    else:
        contenido_usuario = [{"type": "text", "text": mensaje_texto}]

    mensajes_api.append({"role": "user", "content": contenido_usuario})

    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    data = {
        "model": "meta-llama/llama-4-scout-17b-16e-instruct",
        "messages": mensajes_api,
        "max_tokens": 500,
        "temperature": 0.7
    }

    try:
        respuesta = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=data, timeout=30)
        respuesta_json = respuesta.json()

        if 'error' in respuesta_json:
            return f"Error de Groq: {respuesta_json['error'].get('message', 'Error desconocido')} [alerta]"
        if 'choices' not in respuesta_json:
            return f"Groq contestó raro jefe [alerta]"

        return respuesta_json['choices'][0]['message']['content']
    except requests.exceptions.Timeout:
        return "Se tardó Groq jefe, intenta de nuevo [alerta]"
    except Exception as e:
        return f"Falla conectando con Groq: {str(e)} [alerta]"

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>VIERNES</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: -apple-system, sans-serif; background: #0f172a; color: #e2e8f0; margin: 0; padding: 20px; }
     .header { display: flex; align-items: center; gap: 15px; margin-bottom: 20px; }
     .avatar { width: 50px; height: 50px; border-radius: 50%; object-fit: cover; border: 2px solid #0ea5e9; }
     .chat { max-width: 600px; margin: 0 auto; }
     .msg { background: #1e293b; padding: 12px 16px; border-radius: 12px; margin: 10px 0; line-height: 1.4; }
     .user { background: #0ea5e9; text-align: right; margin-left: 40px; }
     .viernes { margin-right: 40px; }
        input, button { padding: 12px; border-radius: 10px; border: none; margin: 5px 0; font-size: 16px; }
        input[type=text] { width: calc(100% - 100px); background: #1e293b; color: white; }
        button { background: #0ea5e9; color: white; cursor: pointer; width: 80px; font-weight: bold; }
        #form { display: flex; gap: 10px; align-items: center; }
        h2 { margin: 0; font-size: 20px; }
        #estado { color: #0ea5e9; font-size: 14px; }
        #mensajes { min-height: 300px; max-height: 60vh; overflow-y: auto; }
    </style>
</head>
<body>
    <div class="chat">
        <div class="header">
            <img src="/imagen/FB_IMG_1778452233908.jpg" class="avatar" alt="VIERNES">
            <div>
                <h2>VIERNES 📋</h2>
                <div id="estado">lista</div>
            </div>
        </div>
        <div id="mensajes"></div>
        <form id="form" enctype="multipart/form-data">
            <input type="text" id="texto" placeholder="Dime jefe..." autocomplete="off">
            <button type="submit">Enviar</button>
        </form>
        <input type="file" id="imagen" accept="image/*" style="margin-top:10px; color: #94a3b8;">
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

            if(texto) mensajes.innerHTML += `<div class="msg user">${texto}</div>`;
            if(imagen) mensajes.innerHTML += `<div class="msg user">📷 Imagen enviada</div>`;

            document.getElementById('texto').value = '';
            document.getElementById('imagen').value = '';
            mensajes.scrollTop = mensajes.scrollHeight;

            const formData = new FormData();
            formData.append('texto', texto);
            if (imagen) formData.append('imagen', imagen);

            try {
                const res = await fetch('/chat', { method: 'POST', body: formData });
                const data = await res.json();
                mensajes.innerHTML += `<div class="msg viernes">${data.respuesta}</div>`;
                estado.textContent = data.estado_texto || 'lista';
                mensajes.scrollTop = mensajes.scrollHeight;
            } catch (err) {
                mensajes.innerHTML += `<div class="msg viernes">Se cayó la conexión jefe [alerta]</div>`;
            }
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
    texto = request.form.get('texto', '')
    imagen_file = request.files.get('imagen')
    imagen_base64 = None

    if imagen_file and imagen_file.filename:
        imagen_base64 = base64.b64encode(imagen_file.read()).decode('utf-8')

    respuesta = analizar_con_groq_vision(texto, imagen_base64)
    estado, estado_texto = detectar_estado(respuesta)

    return {"respuesta": respuesta, "estado": estado, "estado_texto": estado_texto}

if __name__ == '__main__':
    app.run(debug=True)
