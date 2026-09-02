import csv
import json
import os
from datetime import datetime

class DataStorage:
    def __init__(self, config):
        self.csv_file = config["general"]["archivos_salida"]["csv"]
        self.json_file = config["general"]["archivos_salida"]["json"]
        self._ensure_csv_header()

    def _ensure_csv_header(self):
        """Asegura que el archivo CSV tenga su cabecera si no existe (Nivel 2)."""
        if not os.path.exists(self.csv_file):
            with open(self.csv_file, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["timestamp", "temp_celsius_soc", "temp_celsius_amb"])

    def save_reading(self, timestamp_iso, temp_soc, temp_amb):
        """Guarda la lectura actual en CSV."""
        with open(self.csv_file, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([timestamp_iso, temp_soc, temp_amb])

    def export_json(self, history):
        """Exporta el historial completo de lecturas a JSON (Nivel 2)."""
        # history es una lista de diccionarios
        with open(self.json_file, "w") as f:
            json.dump(history, f, indent=4)
