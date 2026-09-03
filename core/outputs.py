from gpiozero import OutputDevice
from .logger import logger


class GPIOController:

    def __init__(self, config):

        gpio_cfg = config.get("gpio", {})

        # ==========================================
        # VENTILADOR
        # ==========================================

        fan_cfg = gpio_cfg.get("ventilador", {})

        self.fan_pin = int(
            fan_cfg.get("pin", 11)
        )

        self.fan_temp_on = float(
            fan_cfg.get("temp_on", 50.0)
        )

        self.fan_temp_off = float(
            fan_cfg.get("temp_off", 45.0)
        )

        self.fan_active_high = bool(
            fan_cfg.get("active_high", True)
        )

        # ==========================================
        # PILOTO
        # ==========================================

        pilot_cfg = gpio_cfg.get("piloto", {})

        self.pilot_pin = int(
            pilot_cfg.get("pin", 5)
        )

        self.pilot_interval = int(
            pilot_cfg.get(
                "cambiar_cada_ciclos",
                3
            )
        )

        self.pilot_active_high = bool(
            pilot_cfg.get("active_high", True)
        )

        # ==========================================
        # CREAR SALIDAS
        # ==========================================

        self.fan = OutputDevice(
            self.fan_pin,
            active_high=self.fan_active_high,
            initial_value=False
        )

        self.pilot = OutputDevice(
            self.pilot_pin,
            active_high=self.pilot_active_high,
            initial_value=False
        )

        self.fan_state = False
        self.pilot_state = False

        logger.info(
            f"GPIO inicializado | "
            f"Ventilador GPIO{self.fan_pin} | "
            f"Piloto GPIO{self.pilot_pin}"
        )

        logger.info(
            f"Control ventilador | "
            f"ON >= {self.fan_temp_on}°C | "
            f"OFF <= {self.fan_temp_off}°C"
        )

    # =================================================
    # VENTILADOR
    # =================================================

    def update_fan(self, soc_temp):

        if soc_temp is None:
            logger.warning(
                "Temperatura SoC inválida. "
                "No se modifica el ventilador."
            )
            return

        # ---------------------------------------------
        # ENCENDER
        # ---------------------------------------------

        if (
            soc_temp >= self.fan_temp_on
            and not self.fan_state
        ):

            self.fan.on()
            self.fan_state = True

            logger.info(
                f"VENTILADOR ON | "
                f"SoC={soc_temp}°C "
                f"GPIO{self.fan_pin}"
            )

        # ---------------------------------------------
        # APAGAR
        # ---------------------------------------------

        elif (
            soc_temp <= self.fan_temp_off
            and self.fan_state
        ):

            self.fan.off()
            self.fan_state = False

            logger.info(
                f"VENTILADOR OFF | "
                f"SoC={soc_temp}°C "
                f"GPIO{self.fan_pin}"
            )

    # =================================================
    # PILOTO
    # =================================================

    def update_pilot(self, ciclo):

        if ciclo <= 0:
            return

        if ciclo % self.pilot_interval != 0:
            return

        self.pilot_state = not self.pilot_state

        if self.pilot_state:

            self.pilot.on()

            logger.info(
                f"PILOTO ON | "
                f"GPIO{self.pilot_pin}"
            )

        else:

            self.pilot.off()

            logger.info(
                f"PILOTO OFF | "
                f"GPIO{self.pilot_pin}"
            )

    # =================================================
    # CIERRE SEGURO
    # =================================================

    def cleanup(self):

        try:

            self.fan.off()
            self.pilot.off()

            self.fan_state = False
            self.pilot_state = False

            self.fan.close()
            self.pilot.close()

            logger.info(
                "GPIO liberados correctamente."
            )

        except Exception as e:

            logger.error(
                f"Error liberando GPIO: {e}"
            )