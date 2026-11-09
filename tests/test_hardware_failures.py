"""Pruebas de tolerancia a fallos; no requieren dispositivos fisicos."""
import unittest
from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import Mock, patch

import minimalmodbus
import serial
import yaml

from core.sensors import AmbientSensor
from core.rtc import RTCReader
from core.alerts import AlertManager
from core.engine import MonitoringEngine
from api import server

ROOT = Path(__file__).resolve().parents[1]


class HardwareFailuresTest(unittest.TestCase):
    def setUp(self):
        self.config = yaml.safe_load((ROOT / "config.yaml").read_text(encoding="utf-8"))

    def test_missing_port_then_sensor_returns(self):
        instrument = Mock()
        instrument.read_register.side_effect = [23.5, 62.0]
        with patch("core.sensors.minimalmodbus.Instrument",
                   side_effect=[serial.SerialException("puerto ausente"),
                                serial.SerialException("puerto ausente"), instrument]), \
             patch("core.sensors.logger") as log:
            sensor = AmbientSensor(self.config)
            self.assertIsNone(sensor.instrument)
            self.assertEqual(sensor.read(), (None, None))
            self.assertEqual(sensor.read(), (23.5, 62.0))
            self.assertTrue(sensor._available)
            self.assertTrue(log.warning.called)
            self.assertTrue(log.info.called)

    def test_modbus_disconnect_and_recovery(self):
        for error in (serial.SerialException("device reports readiness but returned no data"),
                      minimalmodbus.NoResponseError("sin respuesta"),
                      minimalmodbus.InvalidResponseError("respuesta corrupta")):
            with self.subTest(error=type(error).__name__):
                broken, healthy = Mock(), Mock()
                broken.read_register.side_effect = error
                healthy.read_register.side_effect = [24.0, 55.0]
                with patch("core.sensors.minimalmodbus.Instrument",
                           side_effect=[broken, healthy]):
                    sensor = AmbientSensor(self.config)
                    self.assertEqual(sensor.read(), (None, None))
                    self.assertIsNone(sensor.instrument)
                    self.assertEqual(sensor.read(), (24.0, 55.0))
                    broken.serial.close.assert_called()

    def test_bad_config_is_not_hidden_as_hardware_failure(self):
        with patch("core.sensors.minimalmodbus.Instrument",
                   side_effect=ValueError("direccion invalida")):
            with self.assertRaises(ValueError):
                AmbientSensor(self.config)

    def test_rtc_missing_then_available(self):
        with TemporaryDirectory() as folder:
            rtc = RTCReader()
            rtc.date_path = str(Path(folder) / "date")
            rtc.time_path = str(Path(folder) / "time")
            self.assertIsNone(rtc.read_datetime())
            Path(rtc.date_path).write_text("2026-11-09", encoding="utf-8")
            Path(rtc.time_path).write_text("14:30:00", encoding="utf-8")
            self.assertEqual(rtc.read_datetime(), datetime(2026, 11, 9, 14, 30))
            Path(rtc.time_path).write_text("invalid", encoding="utf-8")
            self.assertIsNone(rtc.read_datetime())
            Path(rtc.time_path).write_text("14:31:00", encoding="utf-8")
            self.assertEqual(rtc.read_datetime(), datetime(2026, 11, 9, 14, 31))

    def test_alerts_use_available_temperature(self):
        manager = AlertManager(self.config)
        with patch("core.alerts.logger") as log, patch.object(manager, "send_email") as email:
            manager.check_alerts(90.0, None)
            email.assert_called_once()
            manager.check_alerts(None, 75.0)
            self.assertTrue(log.warning.called)
            manager.check_alerts(None, None)
            manager.check_alerts(40.0, None)

    def test_engine_keeps_gpio_ups_storage_and_api_alive(self):
        with patch("core.engine.GPIOController") as gpio_cls, \
             patch("core.engine.DataStorage") as storage_cls, \
             patch("core.engine.UPSReader") as ups_cls, \
             patch("core.engine.ReportGenerator") as report_cls, \
             patch("core.sensors.minimalmodbus.Instrument",
                   side_effect=serial.SerialException("puerto ausente")), \
             patch.object(RTCReader, "read_datetime", return_value=None), \
             patch("core.engine.SoCSensor") as soc_cls, \
             patch("core.engine.time.sleep", side_effect=[None, KeyboardInterrupt]):
            self.config["general"]["lecturas_para_reporte"] = 1
            soc_cls.return_value.read_temperature.side_effect = [55.0, None]
            gpio = gpio_cls.return_value
            gpio.check_door_change.return_value = True
            gpio.fan_state = False
            gpio.pilot_state = True
            ups_cls.return_value.read.return_value = dict(
                percent=80, voltage=12.0, current=0.2, capacity=1000, state="DESCARGANDO")
            engine = MonitoringEngine(self.config)
            engine.run()
            self.assertEqual(len(engine.history), 2)
            self.assertEqual(gpio.update_fan.call_count, 2)
            self.assertEqual(gpio.update_pilot.call_count, 2)
            gpio.cleanup.assert_called_once()
            self.assertEqual(ups_cls.return_value.read.call_count, 2)
            self.assertEqual(storage_cls.return_value.save_reading.call_count, 2)
            self.assertEqual(storage_cls.return_value.export_json.call_count, 2)
            self.assertEqual(report_cls.return_value.generar_reportes.call_count, 3)
            with patch.object(server, "_engine", engine):
                with server.app.test_client() as client:
                    self.assertEqual(client.get("/status").status_code, 200)
                    data = client.get("/temp").get_json()
                    self.assertIsNone(data["ambient_temp"])
                    self.assertIsNone(data["humidity"])
                    self.assertEqual(data["battery_percent"], 80)
                    self.assertEqual(len(client.get("/history").get_json()), 2)

    def test_reports_skip_unavailable_data_without_crashing(self):
        from reporting.generator import ReportGenerator
        reporter = ReportGenerator(self.config)
        with patch.object(reporter, "_generar_txt") as output:
            reporter.generar_reportes(
                [dict(timestamp=datetime.now().isoformat(), soc_temp=50.0, ambient_temp=None, humidity=None)],
                datetime.now())
            output.assert_not_called()


if __name__ == "__main__":
    unittest.main()
