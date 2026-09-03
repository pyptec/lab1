from datetime import datetime

from .logger import logger


class RTCReader:

    def __init__(self, rtc="rtc0"):

        self.rtc = rtc

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

            return rtc_datetime

        except Exception as e:

            logger.error(
                f"Error leyendo RTC {self.rtc}: "
                f"{type(e).__name__}: {e}"
            )

            return None