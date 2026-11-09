import random
from pathlib import Path
import yaml
import minimalmodbus
import serial

from .logger import logger


class SoCSensor:
    def __init__(self):
        self.path = "/sys/class/thermal/thermal_zone0/temp"

    def read_temperature(self):
        """
        Lee la temperatura interna del SoC de la Raspberry Pi.
        """
        try:
            with open(self.path, "r") as f:
                temp_miligrados = float(f.read().strip())

            temp_celsius = temp_miligrados / 1000.0
            return round(temp_celsius, 2)

        except Exception as e:
            logger.warning(
                f"No se pudo leer temperatura del SoC: {e}"
            )

            return None


class AmbientSensor:
    def __init__(self, config):
        self.config = config

        sensor_cfg = config.get("sensor_tht03r", {})

        self.cfg_file = Path(sensor_cfg.get("cfg_file", "tht03r.yml"))
        if not self.cfg_file.is_absolute():
            self.cfg_file = Path(__file__).resolve().parents[1] / self.cfg_file

        self.cfg_section = sensor_cfg.get(
            "cfg_section",
            "tht03r_sensor"
        )

        self.sensor_config = None
        self.instrument = None
        self._available = False

        self._load_config()
        self._create_instrument()

    def _load_config(self):
        """
        Carga la configuración Modbus desde tht03r.yml.
        """

        try:
            with open(self.cfg_file, "r", encoding="utf-8") as f:
                cfg = yaml.safe_load(f)

            self.sensor_config = (
                cfg["medidores"][self.cfg_section]
            )

            logger.info(
                f"THT03R configurado desde {self.cfg_file}"
            )

        except Exception as e:
            logger.error(
                f"No se pudo cargar configuración THT03R: {e}"
            )
            raise

    def _create_instrument(self):
        """
        Inicializa MinimalModbus.
        """

        cfg = self.sensor_config

        try:
            self.instrument = minimalmodbus.Instrument(
                cfg["port"],
                int(cfg["slave_id"])
            )

            self.instrument.mode = minimalmodbus.MODE_RTU

            self.instrument.serial.baudrate = int(
                cfg["baudrate"]
            )

            self.instrument.serial.bytesize = int(
                cfg["bytesize"]
            )

            self.instrument.serial.stopbits = int(
                cfg["stopbits"]
            )

            self.instrument.serial.timeout = float(
                cfg["timeout"]
            )

            parity_map = {
                "N": serial.PARITY_NONE,
                "E": serial.PARITY_EVEN,
                "O": serial.PARITY_ODD
            }

            self.instrument.serial.parity = parity_map.get(
                str(cfg["parity"]).upper(),
                serial.PARITY_NONE
            )

            self.instrument.clear_buffers_before_each_transaction = True
            self.instrument.close_port_after_each_call = True

            self.instrument.debug = bool(
                cfg.get("debug", False)
            )

            # No mantener el puerto abierto entre ciclos.
            self.instrument.serial.close()

            logger.info(
                f"THT03R Modbus inicializado "
                f"Puerto={cfg['port']} "
                f"Slave={cfg['slave_id']} "
                f"Baud={cfg['baudrate']}"
            )

        except (OSError, serial.SerialException) as e:
            self._disconnect()
            logger.warning(
                f"THT03R no disponible en {cfg['port']}: "
                f"{type(e).__name__}: {e}. Se reintentara en la proxima lectura."
            )

    def _disconnect(self):
        """Liberar una conexion fallida para reconstruirla en el siguiente ciclo."""
        if self.instrument is not None:
            try:
                self.instrument.serial.close()
            except (OSError, serial.SerialException) as e:
                logger.warning(f"No se pudo cerrar el puerto THT03R: {e}")
        self.instrument = None
        self._available = False

    def _read_register(self, name):
        """
        Busca y lee un registro por nombre desde el YAML.
        """

        reg = next(
            (
                r for r in self.sensor_config["registers"]
                if r["name"].lower() == name.lower()
            ),
            None
        )

        if reg is None:
            raise ValueError(
                f"Registro {name} no encontrado en YAML"
            )

        return self.instrument.read_register(
            registeraddress=int(reg["address"]),
            number_of_decimals=int(
                reg.get("decimals", 0)
            ),
            functioncode=int(
                reg.get("fc", 3)
            ),
            signed=False
        )

    def read(self):
        """
        Lee temperatura y humedad del THT03R.

        Retorna:

        temperatura, humedad
        """

        try:
            if self.instrument is None:
                self._create_instrument()
                if self.instrument is None:
                    return None, None

            temperatura = self._read_register(
                "Temperature"
            )

            humedad = self._read_register(
                "Humidity"
            )

            temperatura = round(
                float(temperatura), 2
            )

            humedad = round(
                float(humedad), 2
            )

            if not self._available:
                logger.info("THT03R disponible: lecturas Modbus recuperadas.")
            self._available = True

            logger.info(
                f"THT03R -> "
                f"Temperatura: {temperatura}°C | "
                f"Humedad: {humedad}%"
            )

            return temperatura, humedad

        except (OSError, serial.SerialException, minimalmodbus.ModbusException) as e:
            self._disconnect()
            logger.warning(
                f"THT03R sin lectura valida: {type(e).__name__}: {e}. "
                "Se reintentara en el siguiente ciclo."
            )
            return None, None

    def read_temperature(self):
        """
        Mantiene compatibilidad con código anterior.
        """

        temperatura, _ = self.read()
        return temperatura