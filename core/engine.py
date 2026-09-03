import time
from datetime import datetime

from .logger import logger
from .sensors import SoCSensor, AmbientSensor
from .storage import DataStorage
from .alerts import AlertManager
from .outputs import GPIOController
from reporting.generator import ReportGenerator
from .rtc import RTCReader
from .ups import UPSReader

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

        #rtc
        self.rtc = RTCReader()
        
        #ups
        
        self.ups = UPSReader()
        
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
                
                #====================================
                #RTC
                #=====================================
                rtc_datetime = self.rtc.read_datetime()

                if rtc_datetime is not None:

                    ts = rtc_datetime.isoformat()

                    rtc_text = rtc_datetime.strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )

                else:

                    ts = datetime.now().isoformat()

                    rtc_text = "RTC ERROR"

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
                # PUERTA GPIO13
                # HIGH = CERRADA
                # LOW  = ABIERTA
                # ==========================================

                door_closed = self.gpio.check_door_change()

                if door_closed is True:
                    door_text = "CERRADA"

                elif door_closed is False:
                    door_text = "ABIERTA"

                else:
                    door_text = "ERROR"
                    
                    
                # ==========================================
                # UPS / BATERÍA
                # ==========================================

                ups_data = self.ups.read()

                battery_percent = ups_data["percent"]
                battery_voltage = ups_data["voltage"]
                battery_current = ups_data["current"]
                battery_capacity = ups_data["capacity"]
                battery_state = ups_data["state"]
                # ==========================================
                # 4. GUARDAR LECTURA
                # ==========================================

                lectura = {

                    "timestamp": ts,

                    "soc_temp": soc_temp,
                    "ambient_temp": amb_temp,
                    "humidity": humidity,
                    
                    "battery_percent": battery_percent,
                    "battery_voltage": battery_voltage,
                    "battery_current": battery_current,
                    "battery_capacity": battery_capacity,
                    "battery_state": battery_state,
                    
                    "door_closed": door_closed,
                    "pilot_on": self.gpio.pilot_state,
                    "fan_on": self.gpio.fan_state
                }

                self.history.append(
                    lectura
                )

                # ==========================================
                # 5. LOG
                # ==========================================

                battery_percent_text = (
                    f"{battery_percent}%"
                    if battery_percent is not None
                    else "--"
                )

                battery_voltage_text = (
                    f"{battery_voltage:.2f}V"
                    if battery_voltage is not None
                    else "--"
                )

                fan_text = (
                    "ON"
                    if self.gpio.fan_state
                    else "OFF"
                )

                pilot_text = (
                    "ON"
                    if self.gpio.pilot_state
                    else "OFF"
                )

                logger.info(
                    f"{rtc_text} | "
                    f"TEMP {amb_temp:.1f}°C | "
                    f"HR {humidity:.1f}% | "
                    f"SOC {soc_temp:.1f}°C | "
                    f"PUERTA {door_text} | "
                    f"FAN {fan_text} | "
                    f"PILOTO {pilot_text} | "
                    f"BAT {battery_percent_text} {battery_voltage_text} | "
                    f"UPS {battery_state}"
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