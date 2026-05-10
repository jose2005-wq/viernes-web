from flask import Flask, request, jsonify, render_template_string
import datetime

app = Flask(__name__)

class CerebroViernes:
    def __init__(self):
        self.memoria = []
        self.personalidad = {
            "nombre": "VIERNES",
            "tono": "profesional, cálida, eficiente",
            "estado": "en línea y lista para ayudarte"
        }
    
    def pensar(self, mensaje):
        self.memoria.append(mensaje)
        if len(self.memoria) > 10:
            self.memoria.pop(0)
        
        msg = mensaje.lower()
        hora = datetime.datetime.now().strftime("%H:%M")
        
        if "hola" in msg or "buenos" in msg:
            return f"Buenas, José. Soy VIERNES. Son las {hora}. {self.personalidad['estado']}. ¿En qué puedo ayudarte hoy?"
        
        elif "quien eres" in msg or "que eres" in msg:
            return "Soy VIERNES, tu asistente personal. Fui creada para ayudarte a resolver, organizar y ejecutar. Mi prioridad eres tú."
        
        elif "gracias" in msg:
            return "Un placer, José. Para eso estoy aquí."
        
        elif "memoria" in msg or "recuerdas" in msg:
            ultimas = " | ".join(self.memoria[-3:]) if len(self.memoria) > 1 else "aún no hemos hablado mucho"
            return f"Por supuesto. Recuerdo que recientemente mencionaste: {ultimas}"
        
        else:
            return f"Entendido. Registré tu mensaje: '{mensaje}'. Aún estoy en fase base, pero ya proceso y respondo. ¿Continuamos con algo específico?"

viernes = CerebroViernes()

HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VIERNES</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Arial; 
            background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 100%); 
            color: #e0e0e0; 
            height: 100vh; 
            display: flex; 
            flex-direction: column; 
        }
        .header { 
            background: rgba(0,0,0,0.8); 
            padding: 20px; 
            border-bottom: 1px solid #4a90e2; 
            text-align: center; 
            backdrop-filter: blur(10px);
        }
        .header h1 { color: #4a90e2; font-size: 28px; font-weight: 300; letter-spacing: 3px; }
        .header p { color: #888; font-size: 12px; margin-top: 5px; }
        #chat { 
            flex: 1; 
            overflow-y: auto; 
            padding: 20px; 
            max-width: 800px; 
            width: 100%; 
            margin: 0 auto; 
        }
        .msg { 
            margin: 15px 0; 
            padding: 14px 20px; 
            border-radius: 18px; 
            max-width: 70%; 
            line-height: 1.5;
        }
        .user { 
            background: #4a90e2; 
            color: #fff; 
            margin-left: auto; 
        }
        .viernes { 
            background: rgba(42,42,42,0.8); 
            border: 1px solid #333;
            backdrop-filter: blur(5px);
        }
        .input-area { 
            padding: 20px; 
            background: rgba(0,0,0,0.8); 
            border-top: 1px solid #333; 
            display: flex; 
            max-width: 800px; 
            width: 100%; 
            margin: 0 auto;
            backdrop-filter: blur(10px);
        }
        #msg { 
            flex: 1; 
            padding: 15px; 
            font-size: 16px; 
            border: 1px solid #333; 
            background: rgba(26,26,26,0.8); 
            color: #fff; 
            border-radius: 12px; 
            outline: none; 
        }
        #msg:focus { border-color: #4a90e2; }
        button { 
            padding: 15px 30px; 
            font-size: 16px; 
            background: #4a90e2; 
            color: #fff; 
            border: none; 
            border-radius: 12px; 
            cursor: pointer; 
            margin-left: 10px; 
            transition: all 0.3s;
        }
        button:hover { background: #357abd; transform: translateY(-2px); }
    </style>
</head>
<body>
    <div class="header">
        <h1>V I E R N E S</h1>
        <p>Sistema de Asistencia Personal | Versión 1.3</p>
    </div>
    
    <div id="chat">
        <div class="msg viernes">Buenas, José. Soy VIERNES. Mi sistema está operativo. ¿En qué puedo asistirte?</div>
    </div>
    
    <div class="input-area">
        <input id="msg" placeholder="Escribe tu mensaje..." onkeypress="if(event.key==='Enter') hablar()">
        <button onclick="hablar()">Enviar</button>
    </div>
    
    <script>
    async function hablar(){
        const input = document.getElementById('msg');
        const msg = input.value.trim();
        if(!msg) return;
        
        const chat = document.getElementById('chat');
        chat.innerHTML += `<div class="msg user">${msg}</div>`;
        input.value = '';
        chat.scrollTop = chat.scrollHeight;
        
        chat.innerHTML += `<div class="msg viernes" id="temp">Procesando...</div>`;
        chat.scrollTop = chat.scrollHeight;
        
        const r = await fetch('/chat', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({message: msg})
        });
        const data = await r.json();
        
        document.getElementById('temp').remove();
        chat.innerHTML += `<div class="msg viernes">${data.response}</div>`;
        chat.scrollTop = chat.scrollHeight;
    }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get('message', '')
    respuesta = viernes.pensar(user_message)
    return
