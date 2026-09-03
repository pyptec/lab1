import subprocess
from datetime import datetime

from .logger import logger


class RTCReader:

    def __init__(self, device="/dev/rtc0"):
        self.device = device

        logger.info(
            f"RTC inicializado | dispositivo={self.device}"
        )

    def read_datetime(self):
        """
        Lee fecha y hora directamente desde /dev/rtc0
        mediante hwclock.
        """

        try:
            resultado = subprocess.run(
                [
                    "hwclock",
                    "--show",
                    "--rtc",
                    self.device
                ],
                capture_output=True,
                text=True,
                timeout=2
            )

            if resultado.returncode != 0:
                raise RuntimeError(
                    resultado.stderr.strip()
                )

            texto = resultado.stdout.strip()

            # Ejemplo:
            # 2026-09-02 20:35:15.123456-05:00

            fecha = datetime.fromisoformat(
                texto.split()[0] + " " + texto.split()[1]
            )

            return fecha

        except Exception as e:

            logger.error(
                f"Error leyendo RTC {self.device}: "
                f"{type(e).__name__}: {e}"
            )

            return None