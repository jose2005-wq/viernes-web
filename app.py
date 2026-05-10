from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return '''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>VIERNES</title>
<style>
body{background:#0a0a0a;color:#e0e0e0;font-family:Arial;padding:20px}
h1{color:#4a90e2;text-align:center}
#chat{max-width:600px;margin:20px auto;background:#1a1a1a;padding:20px;border-radius:10px;min-height:300px}
.msg{margin:10px 0;padding:10px;border-radius:8px}
.user{background:#4a90e2;margin-left:20%}
.bot{background:#2a2a2a;margin-right:20%}
input{width:70%;padding:10px;background:#2a2a2a;color:#fff;border:1px solid #333}
button{width:25%;padding:10px;background:#4a90e2;color:#fff;border:none}
</style></head>
<body>
<h1>V I E R N E S</h1>
<div id="chat"><div class="msg bot">Soy VIERNES. Sistema operativo. ¿En qué te ayudo?</div></div>
<div style="max-width:600px;margin:auto">
<input id="msg" placeholder="Escribe..." onkeypress="if(event.key==='Enter') enviar()">
<button onclick="enviar()">Enviar</button>
</div>
<script>
async function enviar(){
let input = document.getElementById('msg');
let txt = input.value.trim();
if(!txt) return;
let chat = document.getElementById('chat');
chat.innerHTML += '<div class="msg user">'+txt+'</div>';
input.value = '';
chat.innerHTML += '<div class="msg bot" id="temp">Procesando...</div>';
try{
let r = await fetch('/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:txt})});
let data = await r.json();
document.getElementById('temp').remove();
chat.innerHTML += '<div class="msg bot">'+data.response+'</div>';
}catch(e){
document.getElementById('temp').innerHTML = 'Error: '+e;
}
chat.scrollTop = chat.scrollHeight;
}
</script></body></html>'''

@app.route('/chat', methods=['POST'])
def chat():
    try:
        msg = request.json.get('message', '')
        return jsonify({"response": "Recibido: " + msg + ". VIERNES funcionando."})
    except Exception as e:
        return jsonify({"response": "Error: " + str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
