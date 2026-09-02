import sys
import os

# Asegurar que el paquete sea encontrable si se corre desde este directorio
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.config_loader import load_config
from core.engine import MonitoringEngine
from api.server import start_server

def main():
    try:
        # Cargar Configuración
        config = load_config("config.yaml")
        
        # Limpiar archivos si se pasa el flag --clean
        if "--clean" in sys.argv:
            archivos = config["general"]["archivos_salida"]
            borrados = 0
            for path in archivos.values():
                if os.path.exists(path):
                    try:
                        os.remove(path)
                        borrados += 1
                    except Exception as e:
                        print(f"No se pudo borrar {path}: {e}")
            print(f"Limpieza completa: {borrados} archivos eliminados. Saliendo...")
            sys.exit(0)
            
        # Inicializar Motor (que engloba Niveles 1, 2, y 3)
        engine = MonitoringEngine(config)
        
        # Levantar API (Nivel 3)
        host = config["api"].get("host", "0.0.0.0")
        port = config["api"].get("port", 5000)
        start_server(engine, host, port)
        
        # Iniciar Bucle Infinito del Demonio
        engine.run()
        
    except Exception as e:
        print(f"Error crítico en el sistema: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
