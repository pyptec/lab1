import time
from datetime import datetime

from .logger import logger
from .sensors import SoCSensor, AmbientSensor
from .storage import DataStorage
from .alerts import AlertManager
from reporting.generator import ReportGenerator

class MonitoringEngine:
    def __init__(self, config):
        self.config = config
        self.intervalo = config["general"]["intervalo_lectura_s"]
        self.lecturas_para_reporte = config["general"]["lecturas_para_reporte"]
        
        # Inicializar manejadores
        self.soc_sensor = SoCSensor()
        self.amb_sensor = AmbientSensor(config)
        self.storage = DataStorage(config)
        self.alert_mgr = AlertManager(config)
        self.reporter = ReportGenerator(config)
        
        # Estado de memoria (para la API)
        self.history = []
        self.start_time = datetime.now()
        
    def run(self):
        logger.info("Iniciando Motor de Monitoreo de Temperatura...")
        
        ciclos = 0
        try:
            while True:
                # Leer Sensores
                ts = datetime.now().isoformat()
                soc_temp = self.soc_sensor.read_temperature()
                amb_temp = self.amb_sensor.read_temperature()
                
                # Guardar en memoria
                lectura = {
                    "timestamp": ts,
                    "soc_temp": soc_temp,
                    "ambient_temp": amb_temp
                }
                self.history.append(lectura)
                
                # Log y CSV
                logger.info(f"Lectura -> SoC: {soc_temp}°C | Amb: {amb_temp}°C")
                self.storage.save_reading(ts, soc_temp, amb_temp)
                
                # JSON
                self.storage.export_json(self.history)
                
                # Alertas
                self.alert_mgr.check_alerts(soc_temp, amb_temp)
                
                ciclos += 1
                
                # Reportes (cada N lecturas, requerimiento Nivel 1 y 2)
                if ciclos % self.lecturas_para_reporte == 0:
                    logger.info(f"Generando reportes periódicos (Ciclo {ciclos})")
                    self.reporter.generar_reportes(self.history, self.start_time)
                
                # Dormir
                time.sleep(self.intervalo)
                
        except KeyboardInterrupt:
            logger.info("Deteniendo motor por interrupción de teclado...")
            # Generar reporte final antes de salir
            self.reporter.generar_reportes(self.history, self.start_time)
            logger.info("Sistema detenido limpiamente.")
