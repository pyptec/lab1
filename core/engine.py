import time
from datetime import datetime

from .logger import logger
from .sensors import SoCSensor, AmbientSensor
from .storage import DataStorage
from .alerts import AlertManager
from .outputs import GPIOController
from reporting.generator import ReportGenerator


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

        # GPIO
        self.gpio = GPIOController(config)

        # Servicios
        self.storage = DataStorage(config)
        self.alert_mgr = AlertManager(config)
        self.reporter = ReportGenerator(config)

        # Historial para API
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

                # ==========================================
                # 1. TEMPERATURA RASPBERRY PI
                # ==========================================

                soc_temp = (
                    self.soc_sensor.read_temperature()
                )

                # ==========================================
                # 2. CONTROL VENTILADOR
                # ==========================================

                self.gpio.update_fan(
                    soc_temp
                )

                # ==========================================
                # 3. SENSOR THT03R MODBUS
                # ==========================================

                amb_temp, humidity = (
                    self.amb_sensor.read()
                )

                # ==========================================
                # 4. GUARDAR LECTURA
                # ==========================================

                lectura = {

                    "timestamp": ts,

                    "soc_temp": soc_temp,

                    "ambient_temp": amb_temp,

                    "humidity": humidity
                }

                self.history.append(
                    lectura
                )

                # ==========================================
                # 5. LOG
                # ==========================================

                logger.info(

                    f"Lectura -> "
                    f"SoC: {soc_temp}°C | "
                    f"Ambiente: {amb_temp}°C | "
                    f"Humedad: {humidity}%"
                )

                # ==========================================
                # 6. CSV
                # ==========================================

                self.storage.save_reading(

                    ts,
                    soc_temp,
                    amb_temp,
                    humidity
                )

                # ==========================================
                # 7. JSON
                # ==========================================

                self.storage.export_json(
                    self.history
                )

                # ==========================================
                # 8. ALERTAS
                # ==========================================

                self.alert_mgr.check_alerts(

                    soc_temp,
                    amb_temp
                )

                # ==========================================
                # 9. CONTADOR DE CICLOS
                # ==========================================

                ciclos += 1

                # ==========================================
                # 10. PILOTO GPIO5
                # ==========================================

                self.gpio.update_pilot(
                    ciclos
                )

                # ==========================================
                # 11. REPORTE PERIÓDICO
                # ==========================================

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

                # ==========================================
                # 12. ESPERA
                # ==========================================

                time.sleep(
                    self.intervalo
                )

        except KeyboardInterrupt:

            logger.info(
                "Deteniendo sistema..."
            )

            # Apagar y liberar GPIO
            self.gpio.cleanup()

            # Reporte final
            self.reporter.generar_reportes(

                self.history,
                self.start_time
            )

            logger.info(
                "Sistema detenido limpiamente."
            )