import matplotlib.pyplot as plt

from core.logger import logger
from datetime import datetime


class ReportGenerator:

    def __init__(self, config):

        self.txt_file = (
            config["general"]["archivos_salida"]["reporte_txt"]
        )

        self.md_file = (
            config["general"]["archivos_salida"]["reporte_md"]
        )

        self.png_file = (
            config["general"]["archivos_salida"]["grafica_png"]
        )

    def generar_reportes(
        self,
        history,
        start_time
    ):

        if not history:
            return

        end_time = datetime.now()

        duracion = (
            end_time - start_time
        )

        timestamps = [
            h["timestamp"]
            for h in history
        ]

        soc_temps = [
            h["soc_temp"]
            for h in history
            if h["soc_temp"] is not None
        ]

        amb_temps = [
            h["ambient_temp"]
            for h in history
            if h["ambient_temp"] is not None
        ]

        humidity = [
            h["humidity"]
            for h in history
            if h.get("humidity") is not None
        ]

        if (
            not soc_temps
            or not amb_temps
            or not humidity
        ):
            logger.warning(
                "No hay suficientes datos "
                "para generar reporte."
            )
            return

        stats = {

            "soc": {
                "max": max(soc_temps),
                "min": min(soc_temps),
                "avg": sum(soc_temps)
                       / len(soc_temps)
            },

            "amb": {
                "max": max(amb_temps),
                "min": min(amb_temps),
                "avg": sum(amb_temps)
                       / len(amb_temps)
            },

            "humidity": {
                "max": max(humidity),
                "min": min(humidity),
                "avg": sum(humidity)
                       / len(humidity)
            }
        }

        self._generar_txt(
            stats
        )

        self._generar_md(
            stats,
            start_time,
            end_time,
            duracion,
            len(history)
        )

        self._generar_grafica(
            history
        )

        logger.info(
            "Reportes generados correctamente."
        )

    def _generar_txt(
        self,
        stats
    ):

        reporte = (

            "================ REPORTE =================\n"

            f"SoC -> "
            f"Max: {stats['soc']['max']:.2f}°C | "
            f"Min: {stats['soc']['min']:.2f}°C | "
            f"Promedio: {stats['soc']['avg']:.2f}°C\n"

            f"Ambiente -> "
            f"Max: {stats['amb']['max']:.2f}°C | "
            f"Min: {stats['amb']['min']:.2f}°C | "
            f"Promedio: {stats['amb']['avg']:.2f}°C\n"

            f"Humedad -> "
            f"Max: {stats['humidity']['max']:.2f}% | "
            f"Min: {stats['humidity']['min']:.2f}% | "
            f"Promedio: {stats['humidity']['avg']:.2f}%\n"

            "==========================================\n"
        )

        print(reporte)

        with open(
            self.txt_file,
            "w"
        ) as f:

            f.write(reporte)

    def _generar_md(
        self,
        stats,
        start_time,
        end_time,
        duracion,
        total_lecturas
    ):

        md = f"""# Reporte de Monitoreo

**Fecha de generación:** {end_time.strftime("%Y-%m-%d %H:%M:%S")}

**Inicio:** {start_time.strftime("%Y-%m-%d %H:%M:%S")}

**Duración:** {duracion}

**Total lecturas:** {total_lecturas}

## Temperaturas

| Sensor | Máxima | Mínima | Promedio |
|---|---:|---:|---:|
| SoC | {stats['soc']['max']:.2f} °C | {stats['soc']['min']:.2f} °C | {stats['soc']['avg']:.2f} °C |
| Ambiente | {stats['amb']['max']:.2f} °C | {stats['amb']['min']:.2f} °C | {stats['amb']['avg']:.2f} °C |

## Humedad

| Variable | Máxima | Mínima | Promedio |
|---|---:|---:|---:|
| Humedad relativa | {stats['humidity']['max']:.2f} % | {stats['humidity']['min']:.2f} % | {stats['humidity']['avg']:.2f} % |

## Gráfico

![Monitoreo]({self.png_file})
"""

        with open(
            self.md_file,
            "w"
        ) as f:

            f.write(md)

    def _generar_grafica(
        self,
        history
    ):

        try:

            x_times = [
                datetime.fromisoformat(
                    h["timestamp"]
                )
                for h in history
            ]

            soc = [
                h["soc_temp"]
                for h in history
            ]

            ambiente = [
                h["ambient_temp"]
                for h in history
            ]

            plt.figure(
                figsize=(10, 5)
            )

            plt.plot(
                x_times,
                soc,
                label="SoC"
            )

            plt.plot(
                x_times,
                ambiente,
                label="Temperatura ambiente"
            )

            plt.title(
                "Temperatura vs Tiempo"
            )

            plt.xlabel(
                "Tiempo"
            )

            plt.ylabel(
                "Temperatura °C"
            )

            plt.legend()

            plt.grid(True)

            plt.gcf().autofmt_xdate()

            plt.tight_layout()

            plt.savefig(
                self.png_file
            )

            plt.close()

        except Exception as e:

            logger.error(
                f"No se pudo generar gráfica: {e}"
            )