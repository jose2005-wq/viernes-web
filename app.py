from flask import Flask, request, jsonify
import os

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        "service": "VIERNES Web API v1.2",
        "status": "Online",
        "ai_status": "Basic mode active"
    })

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')
    
    if not user_message:
        return jsonify({"error": "No message provided"}), 400
    
    respuesta = f"VIERNES v1.2 recibió: {user_message}"
    
    return jsonify({"response": respuesta})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
