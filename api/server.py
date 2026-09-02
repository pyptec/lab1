from flask import Flask, jsonify, render_template
import threading
from core.logger import logger

app = Flask(__name__, template_folder="templates")

# Referencia global al motor para leer el estado
_engine = None

@app.route('/')
def dashboard():
    return render_template("index.html")

@app.route('/temp', methods=['GET'])
def get_temp():
    if _engine and _engine.history:
        return jsonify(_engine.history[-1])
    return jsonify({"error": "No hay datos todavía"}), 404

@app.route('/history', methods=['GET'])
def get_history():
    if _engine:
        return jsonify(_engine.history)
    return jsonify([]), 200

@app.route('/status', methods=['GET'])
def get_status():
    return jsonify({
        "status": "running",
        "total_readings": len(_engine.history) if _engine else 0,
        "config": _engine.config["general"] if _engine else {}
    })

def start_server(engine_ref, host="0.0.0.0", port=5000):
    global _engine
    _engine = engine_ref
    
    def run():
        # Deshabilitar logs de werkzeug para no ensuciar nuestro log principal
        import logging
        log = logging.getLogger('werkzeug')
        log.disabled = True
        
        logger.info(f"Iniciando API REST en http://{host}:{port}")
        app.run(host=host, port=port, debug=False, use_reloader=False)
        
    thread = threading.Thread(target=run, daemon=True)
    thread.start()
    return thread
