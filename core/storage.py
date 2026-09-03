import csv
import json
import os


class DataStorage:

    def __init__(self, config):

        self.csv_file = (
            config["general"]["archivos_salida"]["csv"]
        )

        self.json_file = (
            config["general"]["archivos_salida"]["json"]
        )

        self._ensure_csv_header()

    def _ensure_csv_header(self):

        if not os.path.exists(self.csv_file):

            with open(
                self.csv_file,
                "w",
                newline=""
            ) as f:

                writer = csv.writer(f)

                writer.writerow([
                    "timestamp",
                    "temp_celsius_soc",
                    "temp_celsius_amb",
                    "humidity_percent"
                ])

    def save_reading(
        self,
        timestamp_iso,
        temp_soc,
        temp_amb,
        humidity
    ):

        with open(
            self.csv_file,
            "a",
            newline=""
        ) as f:

            writer = csv.writer(f)

            writer.writerow([
                timestamp_iso,
                temp_soc,
                temp_amb,
                humidity
            ])

    def export_json(self, history):

        with open(
            self.json_file,
            "w"
        ) as f:

            json.dump(
                history,
                f,
                indent=4
            )