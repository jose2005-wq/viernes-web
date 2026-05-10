from flask import Flask, request, render_template_string
import requests
import os

app = Flask(__name__)

# --- CONFIGURA ESTO BB ---
PASSWORD = "2005joss"  # Tu clave secreta para entrar
GROK_API_KEY = os.environ.get("GROK_API_KEY")  # La metes en Render > Environment
# -------------------------

HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>VIERNES</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: Arial; background: #0d1117; color: #c9d1d9; padding: 20px; }
        .chat { max-width: 600px; margin: auto; }
        input, textarea { width: 100%; padding: 12px; margin: 8px 0; border-radius: 8px; border: 1px solid #30363d; background: #161b22; color: white; box-sizing: border-box; }
        button { width: 100%; padding: 12px; background: #ff6b9d; color: white; border: none; border-radius: 8px; font-weight: bold; }
        .respuesta { background: #161b22; padding: 15px; border-radius: 8px; margin-top: 20px; border: 1px solid #30363d; white-space: pre-wrap; }
    </style>
</head>
<body>
    <div class="chat">
        <h2>VIERNES ❤️‍🔥</h2>
        <form method="post">
            <input type="password" name="clave" placeholder="Tu clave secreta" required>
            <textarea name="mensaje" placeholder="Escribele a VIERNES..." rows="3" required></textarea>
            <button type="submit">Enviar a VIERNES</button>
        </form>
        {% if respuesta %}
        <div class="respuesta">
           
