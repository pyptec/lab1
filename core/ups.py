import subprocess
import re
import time

from .logger import logger


class UPSReader:

    def __init__(self):

        self.script = "/home/pi/UPS_HAT_E/ups.py"

        # Última lectura válida.
        # Si en un ciclo falla la UPS no destruimos inmediatamente
        # el último dato conocido.
        self.last_data = {
            "percent": None,
            "voltage": None,
            "current": None,
            "capacity": None,
            "state": "SIN DATOS"
        }

        logger.info(
            f"UPS inicializada | {self.script}"
        )


    def read(self):

        proceso = None

        try:

            # -u = salida Python sin buffer.
            # Esto permite capturar las líneas mientras ups.py continúa.
            proceso = subprocess.Popen(
                [
                    "/usr/bin/python3",
                    "-u",
                    self.script
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )

            inicio = time.monotonic()

            estado = None
            porcentaje = None
            voltaje_mv = None
            corriente_ma = None
            capacidad_mah = None

            while True:

                # Timeout total para obtener UNA lectura
                if time.monotonic() - inicio > 4:
                    break

                linea = proceso.stdout.readline()

                if not linea:

                    if proceso.poll() is not None:
                        break

                    time.sleep(0.05)
                    continue

                linea = linea.strip()

                # ----------------------------
                # ESTADO
                # ----------------------------

                if "Charging state" in linea:
                    estado = "CARGANDO"

                elif "Discharging state" in linea:
                    estado = "DESCARGANDO"

                # ----------------------------
                # VOLTAJE BATERÍA
                # ----------------------------

                match = re.search(
                    r"Battery Voltage\s+(-?\d+)",
                    linea,
                    re.IGNORECASE
                )

                if match:
                    voltaje_mv = int(match.group(1))

                # ----------------------------
                # CORRIENTE BATERÍA
                # ----------------------------

                match = re.search(
                    r"Battery Current\s+(-?\d+)",
                    linea,
                    re.IGNORECASE
                )

                if match:
                    corriente_ma = int(match.group(1))

                # ----------------------------
                # PORCENTAJE
                # ----------------------------

                match = re.search(
                    r"Battery Percent\s+(\d+)",
                    linea,
                    re.IGNORECASE
                )

                if match:
                    porcentaje = int(match.group(1))

                # ----------------------------
                # CAPACIDAD
                # ----------------------------

                match = re.search(
                    r"Remaining Capacity\s+(\d+)",
                    linea,
                    re.IGNORECASE
                )

                if match:
                    capacidad_mah = int(match.group(1))

                # Ya tenemos lo necesario.
                # No necesitamos esperar que ups.py termine.
                if (
                    porcentaje is not None
                    and voltaje_mv is not None
                    and estado is not None
                ):
                    break


            # Detener el programa externo después
            # de obtener una lectura.
            if proceso.poll() is None:
                proceso.terminate()

                try:
                    proceso.wait(timeout=1)

                except subprocess.TimeoutExpired:
                    proceso.kill()


            # Debemos tener como mínimo porcentaje y voltaje.
            if porcentaje is None or voltaje_mv is None:

                raise RuntimeError(
                    "UPS no entregó una lectura completa"
                )


            data = {
                "percent": porcentaje,

                "voltage": round(
                    voltaje_mv / 1000.0,
                    3
                ),

                "current": corriente_ma,

                "capacity": capacidad_mah,

                "state": estado or "DESCONOCIDO"
            }

            self.last_data = data

            return data


        except Exception as e:

            # Evitamos imprimir el traceback gigante
            logger.warning(
                f"UPS sin lectura nueva | "
                f"{type(e).__name__}: {e}"
            )

            return self.last_data


        finally:

            if proceso is not None:

                try:

                    if proceso.poll() is None:
                        proceso.kill()

                except Exception:
                    pass