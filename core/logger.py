import logging
from logging.handlers import RotatingFileHandler

def setup_logger(log_file="sistema.log"):
    logger = logging.getLogger("TempMonitor")
    logger.setLevel(logging.INFO)

    # Evitar agregar handlers múltiples si se llama varias veces
    if not logger.handlers:
        # Rotating File Handler (Max 10MB, 5 backups) - Requerimiento Nivel 3
        file_handler = RotatingFileHandler(log_file, maxBytes=10*1024*1024, backupCount=5)
        file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

        # Console Handler (Para ver salida estándar en la terminal)
        console_handler = logging.StreamHandler()
        console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

    return logger

logger = setup_logger()
