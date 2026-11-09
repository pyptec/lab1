from datetime import datetime

from .logger import logger


class RTCReader:

    def __init__(self, rtc="rtc0"):

        self.rtc = rtc
        self._available = False

        self.date_path = f"/sys/class/rtc/{rtc}/date"
        self.time_path = f"/sys/class/rtc/{rtc}/time"

        logger.info(
            f"RTC inicializado | {rtc}"
        )

    def read_datetime(self):
        """
        Lee directamente la fecha y hora del RTC
        administrado por el kernel de Linux.
        """

        try:

            with open(self.date_path, "r") as f:
                fecha = f.read().strip()

            with open(self.time_path, "r") as f:
                hora = f.read().strip()

            rtc_datetime = datetime.strptime(
                f"{fecha} {hora}",
                "%Y-%m-%d %H:%M:%S"
            )

            if not self._available:
                logger.info(f"RTC {self.rtc} disponible: lectura recuperada.")
            self._available = True
            return rtc_datetime

        except (OSError, ValueError) as e:
            self._available = False
            logger.warning(
                f"RTC {self.rtc} no disponible: {type(e).__name__}: {e}. "
                "Se usara el reloj del sistema y se reintentara en el siguiente ciclo."
            )
            return None
