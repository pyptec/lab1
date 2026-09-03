from datetime import datetime
from smbus2 import SMBus

from .logger import logger


class RTCReader:

    DS3231_ADDR = 0x68

    def __init__(self, bus_number=1):

        self.bus_number = bus_number

        logger.info(
            f"RTC DS3231 inicializado | "
            f"I2C bus={self.bus_number} | "
            f"address=0x{self.DS3231_ADDR:02X}"
        )

    @staticmethod
    def _bcd_to_dec(value):
        return (value >> 4) * 10 + (value & 0x0F)

    def read_datetime(self):

        try:

            with SMBus(self.bus_number) as bus:

                data = bus.read_i2c_block_data(
                    self.DS3231_ADDR,
                    0x00,
                    7
                )

            segundos = self._bcd_to_dec(
                data[0] & 0x7F
            )

            minutos = self._bcd_to_dec(
                data[1] & 0x7F
            )

            # DS3231 configurado en formato 24 horas
            horas = self._bcd_to_dec(
                data[2] & 0x3F
            )

            dia = self._bcd_to_dec(
                data[4] & 0x3F
            )

            mes = self._bcd_to_dec(
                data[5] & 0x1F
            )

            anio = 2000 + self._bcd_to_dec(
                data[6]
            )

            return datetime(
                anio,
                mes,
                dia,
                horas,
                minutos,
                segundos
            )

        except Exception as e:

            logger.error(
                f"Error leyendo RTC DS3231: "
                f"{type(e).__name__}: {e}"
            )

            return None