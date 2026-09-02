import os
import matplotlib.pyplot as plt
from core.logger import logger
from datetime import datetime

class ReportGenerator:
    def __init__(self, config):
        self.txt_file = config["general"]["archivos_salida"]["reporte_txt"]
        self.md_file = config["general"]["archivos_salida"]["reporte_md"]
        self.png_file = config["general"]["archivos_salida"]["grafica_png"]

    def generar_reportes(self, history, start_time):
        if not history:
            return

        end_time = datetime.now()
        duracion = end_time - start_time

        # Extraer listas de valores
        timestamps = [h["timestamp"] for h in history]
        soc_temps = [h["soc_temp"] for h in history]
        amb_temps = [h["ambient_temp"] for h in history]

        # Cálculos estadísticos (Nivel 1 y 2)
        soc_max, soc_min, soc_avg = max(soc_temps), min(soc_temps), sum(soc_temps)/len(soc_temps)
        amb_max, amb_min, amb_avg = max(amb_temps), min(amb_temps), sum(amb_temps)/len(amb_temps)

        stats = {
            "soc": {"max": soc_max, "min": soc_min, "avg": soc_avg},
            "amb": {"max": amb_max, "min": amb_min, "avg": amb_avg}
        }

        self._generar_txt(stats)
        self._generar_md(stats, start_time, end_time, duracion, len(history))
        self._generar_grafica(timestamps, soc_temps, amb_temps)
        
        logger.info("Reportes estadísticos, MD y gráfica generados.")

    def _generar_txt(self, stats):
        """Genera el reporte en pantalla y texto del Nivel 1."""
        reporte = (
            "================ REPORTE DE TEMPERATURA =================\n"
            f"SoC     -> Max: {stats['soc']['max']:.2f}°C | Min: {stats['soc']['min']:.2f}°C | Promedio: {stats['soc']['avg']:.2f}°C\n"
            f"Ambiente-> Max: {stats['amb']['max']:.2f}°C | Min: {stats['amb']['min']:.2f}°C | Promedio: {stats['amb']['avg']:.2f}°C\n"
            "=========================================================\n"
        )
        print(reporte)
        with open(self.txt_file, "w") as f:
            f.write(reporte)

    def _generar_md(self, stats, start_time, end_time, duracion, total_lecturas):
        """Genera el reporte Markdown estructurado del Nivel 2."""
        md = f"""# Reporte de Monitoreo de Temperatura

**Fecha de generación:** {end_time.strftime("%Y-%m-%d %H:%M:%S")}
**Inicio del monitoreo:** {start_time.strftime("%Y-%m-%d %H:%M:%S")}
**Duración:** {duracion}
**Total de lecturas:** {total_lecturas}

## Estadísticas

| Sensor | Máxima (°C) | Mínima (°C) | Promedio (°C) |
|--------|-------------|-------------|---------------|
| SoC    | {stats['soc']['max']:.2f} | {stats['soc']['min']:.2f} | {stats['soc']['avg']:.2f} |
| Amb.   | {stats['amb']['max']:.2f} | {stats['amb']['min']:.2f} | {stats['amb']['avg']:.2f} |

## Gráfico de Tendencia
![Gráfico de Temperatura]({self.png_file})
"""
        with open(self.md_file, "w") as f:
            f.write(md)

    def _generar_grafica(self, timestamps, soc_temps, amb_temps):
        """Genera gráfica de Temperatura vs Tiempo (Nivel 2)."""
        try:
            # Parseamos los timestamps ISO a objetos datetime para el eje X
            x_times = [datetime.fromisoformat(ts) for ts in timestamps]
            
            plt.figure(figsize=(10, 5))
            plt.plot(x_times, soc_temps, label="SoC Temp", color="red", marker='o')
            plt.plot(x_times, amb_temps, label="Ambient Temp", color="blue", marker='x')
            plt.title("Temperatura vs Tiempo")
            plt.xlabel("Tiempo")
            plt.ylabel("Temperatura (°C)")
            plt.legend()
            plt.grid(True)
            plt.gcf().autofmt_xdate() # Rotar fechas para que quepan
            plt.tight_layout()
            
            plt.savefig(self.png_file)
            plt.close()
        except Exception as e:
            logger.error(f"No se pudo generar la gráfica: {e}")
