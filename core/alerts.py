from .logger import logger

class AlertManager:
    def __init__(self, config):
        self.umbral_alerta = config["alertas"]["umbral_alerta"]
        self.umbral_critico = config["alertas"]["umbral_critico"]
        self.email_destino = config["alertas"]["email_destino"]

    def check_alerts(self, temp_soc, temp_amb):
        """
        Verifica los umbrales e imprime alertas en terminal (Nivel 3).
        Rojo: Crítico
        Amarillo/Naranja: Alerta
        """
        max_temp = max(temp_soc, temp_amb)
        
        # Secuencias de escape ANSI para colores en terminal
        COLOR_RESET = "\033[0m"
        COLOR_YELLOW = "\033[93m"
        COLOR_RED = "\033[91m"

        if max_temp >= self.umbral_critico:
            msg = f"¡CRÍTICO! Temperatura excedió los {self.umbral_critico}°C (Actual: {max_temp}°C)"
            print(f"{COLOR_RED}{msg}{COLOR_RESET}")
            logger.error(msg)
            self.send_email(msg)
        elif max_temp >= self.umbral_alerta:
            msg = f"¡ALERTA! Temperatura excedió los {self.umbral_alerta}°C (Actual: {max_temp}°C)"
            print(f"{COLOR_YELLOW}{msg}{COLOR_RESET}")
            logger.warning(msg)

    def send_email(self, mensaje):
        """Simulación de envío de correo."""
        # En un sistema real se usaría smtplib u otra API
        logger.info(f"[EMAIL SIMULADO enviado a {self.email_destino}]: {mensaje}")
