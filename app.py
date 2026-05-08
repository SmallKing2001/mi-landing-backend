from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Archivo donde guardamos los suscriptores
DATABASE_FILE = "suscriptores.json"

def load_subscribers():
    """Cargar lista de suscriptores existentes"""
    if os.path.exists(DATABASE_FILE):
        with open(DATABASE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_subscriber(subscriber):
    """Guardar nuevo suscriptor"""
    subscribers = load_subscribers()
    subscribers.append(subscriber)
    with open(DATABASE_FILE, "w", encoding="utf-8") as f:
        json.dump(subscribers, f, indent=4, ensure_ascii=False)

def email_exists(email):
    """Verificar si el email ya está registrado"""
    subscribers = load_subscribers()
    return any(sub['email'] == email for sub in subscribers)

@app.route("/api/subscribe", methods=["POST"])
def subscribe():
    """Endpoint para registrar nuevos suscriptores"""
    data = request.get_json()
    name = data.get("name", "").strip()
    email = data.get("email", "").strip().lower()
    
    # Validaciones
    if not name or len(name) < 2:
        return jsonify({"error": "El nombre debe tener al menos 2 caracteres"}), 400
    
    if not email or "@" not in email:
        return jsonify({"error": "Email inválido"}), 400
    
    # Evitar duplicados
    if email_exists(email):
        return jsonify({"error": "Este email ya está registrado"}), 400
    
    # Guardar suscriptor
    subscriber = {
        "id": len(load_subscribers()) + 1,
        "name": name,
        "email": email,
        "fecha_registro": datetime.now().isoformat(),
        "ip": request.remote_addr,
        "activo": True
    }
    
    save_subscriber(subscriber)
    
    # Imprimir en consola para verlo en tiempo real
    print(f"\n📧 Nuevo suscriptor:")
    print(f"   Nombre: {name}")
    print(f"   Email: {email}")
    print(f"   Fecha: {subscriber['fecha_registro']}")
    print(f"   Total suscriptores: {len(load_subscribers())}\n")
    
    # Aquí podrías enviar un email de bienvenida con smtplib
    
    return jsonify({
        "message": "Suscripción exitosa",
        "subscriber": {"name": name, "email": email}
    }), 200

@app.route("/api/subscribers", methods=["GET"])
def get_subscribers():
    """Endpoint opcional para ver todos los suscriptores (solo para pruebas)"""
    return jsonify(load_subscribers())

@app.route("/api/stats", methods=["GET"])
def get_stats():
    """Estadísticas básicas"""
    subscribers = load_subscribers()
    return jsonify({
        "total": len(subscribers),
        "hoy": sum(1 for s in subscribers if s['fecha_registro'].startswith(datetime.now().strftime("%Y-%m-%d")))
    })

if __name__ == "__main__":
    print("🚀 Servidor iniciado en http://localhost:5000")
    print("📋 Los suscriptores se guardarán en suscriptores.json")
    print("Presiona CTRL+C para detener el servidor\n")
    app.run(debug=True, port=5000)