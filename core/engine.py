import time
from datetime import datetime

from .logger import logger
from .sensors import SoCSensor, AmbientSensor
from .storage import DataStorage
from .alerts import AlertManager
from reporting.generator import ReportGenerator
from .alerts import AlertManager
from .outputs import GPIOController


class MonitoringEngine:

    def __init__(self, config):

        self.config = config

        self.intervalo = config["general"]["intervalo_lectura_s"]

        self.lecturas_para_reporte = (
            config["general"]["lecturas_para_reporte"]
        )

        # Sensores
        self.soc_sensor = SoCSensor()
        self.amb_sensor = AmbientSensor(config)
        
        #gpio
        self.gpio = GPIOController(config)

        # Servicios
        self.storage = DataStorage(config)
        self.alert_mgr = AlertManager(config)
        self.reporter = ReportGenerator(config)

        # Historial utilizado por la API
        self.history = []

        self.start_time = datetime.now()

    def run(self):

        logger.info(
            "Iniciando Motor de Monitoreo..."
        )

        ciclos = 0

        try:

            while True:

                ts = datetime.now().isoformat()

                # --------------------------------
                # Temperatura Raspberry Pi
                # --------------------------------

                soc_temp = (
                    self.soc_sensor.read_temperature()
                )

                # --------------------------------
                # Sensor THT03R Modbus
                # --------------------------------

                amb_temp, humidity = (
                    self.amb_sensor.read()
                )

                # --------------------------------
                # Guardar lectura en memoria
                # --------------------------------

                lectura = {

                    "timestamp": ts,

                    "soc_temp": soc_temp,

                    "ambient_temp": amb_temp,

                    "humidity": humidity
                }

                self.history.append(
                    lectura
                )

                # --------------------------------
                # Log
                # --------------------------------

                logger.info(
                    f"Lectura -> "
                    f"SoC: {soc_temp}°C | "
                    f"Ambiente: {amb_temp}°C | "
                    f"Humedad: {humidity}%"
                )

                # --------------------------------
                # CSV
                # --------------------------------

                self.storage.save_reading(
                    ts,
                    soc_temp,
                    amb_temp,
                    humidity
                )

                # --------------------------------
                # JSON
                # --------------------------------

                self.storage.export_json(
                    self.history
                )

                # --------------------------------
                # Alertas
                # --------------------------------

                self.alert_mgr.check_alerts(
                    soc_temp,
                    amb_temp
                )

                ciclos += 1

                # --------------------------------
                # Reporte periódico
                # --------------------------------

                if (
                    ciclos
                    % self.lecturas_para_reporte
                    == 0
                ):

                    logger.info(
                        f"Generando reportes "
                        f"(Ciclo {ciclos})"
                    )

                    self.reporter.generar_reportes(
                        self.history,
                        self.start_time
                    )

                time.sleep(
                    self.intervalo
                )

        except KeyboardInterrupt:

            logger.info(
                "Deteniendo sistema..."
            )

            self.reporter.generar_reportes(
                self.history,
                self.start_time
            )

            logger.info(
                "Sistema detenido limpiamente."
            )