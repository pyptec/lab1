import random
import sys
from .logger import logger

class SoCSensor:
    def __init__(self):
        self.path = "/sys/class/thermal/thermal_zone0/temp"
        
    def read_temperature(self):
        """Lee la temperatura del SoC de la Raspberry Pi y la convierte a Celsius."""
        try:
            with open(self.path, "r") as f:
                temp_miligrados = float(f.read().strip())
                temp_celsius = temp_miligrados / 1000.0
                return round(temp_celsius, 2)
        except Exception as e:
            logger.warning(f"No se pudo leer el SoC desde {self.path}. Usando valor de prueba. Error: {e}")
            return round(random.uniform(40.0, 50.0), 2)

class AmbientSensor:
    def __init__(self, config=None):
        self.config = config
        self.use_simulation = True
        
        # Intentamos importar los módulos del THT03R que tenías en el entorno
        try:
            import os
            # base_dir es proyecto_temperatura, parent_dir es Proyecto (donde están util.py y modbusdevices.py)
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            parent_dir = os.path.dirname(base_dir)
            sys.path.append(parent_dir)
            import util
            import modbusdevices
            self.util = util
            self.modbusdevices = modbusdevices
            
            if self.config and "sensor_tht03r" in self.config:
                self.cfg_file = self.config["sensor_tht03r"].get("cfg_file")
                self.cfg_section = self.config["sensor_tht03r"].get("cfg_section")
                if self.cfg_file and self.cfg_section:
                    self.tht03r_config = self.util.cargar_configuracion(self.cfg_file, self.cfg_section)
                    self.use_simulation = False
                    logger.info("Sensor THT03R reconocido e inicializado correctamente.")
        except Exception as e:
            logger.warning(f"No se pudo inicializar THT03R (usaremos simulación): {e}")

    def read_temperature(self):
        """Lee la temperatura ambiente real o simulada."""
        if self.use_simulation:
            # Rango razonable para temperatura ambiente
            return round(random.uniform(18.0, 25.0), 2)
        else:
            try:
                payload = self.modbusdevices.payload_event_modbus(self.tht03r_config)
                if payload and "d" in payload and len(payload["d"]) > 0:
                    valores = payload["d"][0]["v"]
                    if valores and len(valores) > 0:
                        temp = float(valores[0])
                        return round(temp, 2)
            except Exception as e:
                logger.error(f"Error leyendo THT03R real, volviendo a simulación en este ciclo: {e}")
                
            return round(random.uniform(18.0, 25.0), 2)
