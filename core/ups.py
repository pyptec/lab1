import subprocess
import re

from .logger import logger


class UPSReader:

    def __init__(self):

        self.script = "/home/pi/UPS_HAT_E/ups.py"

        logger.info(
            f"UPS inicializada | script={self.script}"
        )

    def read(self):

        try:

            resultado = subprocess.run(
                [
                    "/usr/bin/python3",
                    self.script
                ],
                capture_output=True,
                text=True,
                timeout=5
            )

            if resultado.returncode != 0:

                raise RuntimeError(
                    resultado.stderr.strip()
                )

            salida = resultado.stdout

            # ==========================================
            # ESTADO
            # ==========================================

            if "Charging state" in salida:

                estado = "CARGANDO"

            elif "Discharging state" in salida:

                estado = "DESCARGANDO"

            else:

                estado = "DESCONOCIDO"

            # ==========================================
            # BATERÍA
            # ==========================================

            porcentaje = self._buscar(
                salida,
                r"Battery Percent\s+(\d+)"
            )

            voltaje_mv = self._buscar(
                salida,
                r"Battery Voltage\s+(-?\d+)"
            )

            corriente_ma = self._buscar(
                salida,
                r"Battery Current\s+(-?\d+)"
            )

            capacidad_mah = self._buscar(
                salida,
                r"Remaining Capacity\s+(\d+)"
            )

            # ==========================================
            # CONVERSIÓN
            # ==========================================

            porcentaje = (
                int(porcentaje)
                if porcentaje is not None
                else None
            )

            voltaje = (
                round(
                    int(voltaje_mv) / 1000.0,
                    3
                )
                if voltaje_mv is not None
                else None
            )

            corriente = (
                int(corriente_ma)
                if corriente_ma is not None
                else None
            )

            capacidad = (
                int(capacidad_mah)
                if capacidad_mah is not None
                else None
            )

            return {
                "percent": porcentaje,
                "voltage": voltaje,
                "current": corriente,
                "capacity": capacidad,
                "state": estado
            }

        except Exception as e:

            logger.error(
                f"Error leyendo UPS: "
                f"{type(e).__name__}: {e}"
            )

            return {
                "percent": None,
                "voltage": None,
                "current": None,
                "capacity": None,
                "state": "ERROR"
            }

    @staticmethod
    def _buscar(texto, patron):

        resultado = re.search(
            patron,
            texto,
            re.IGNORECASE
        )

        if resultado:

            return resultado.group(1)

        return None