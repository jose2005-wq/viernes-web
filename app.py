from flask import Flask, request, jsonify, render_template_string
import datetime

app = Flask(__name__)

# NÚCLEO DE PERSONALIDAD VIERNES v1.3 - FEMENINA
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
            return "
