from smbus2 import SMBus
import time


ADS1115_ADDR = 0x48

REG_CONVERSION = 0x00
REG_CONFIG = 0x01


def leer_an1():

    with SMBus(1) as bus:

        # ADS1115:
        # Single-shot
        # AIN1 respecto a GND
        # PGA = +/-4.096 V
        # 128 muestras/segundo
        # Comparator deshabilitado

        config = 0xD383

        bus.write_i2c_block_data(
            ADS1115_ADDR,
            REG_CONFIG,
            [
                (config >> 8) & 0xFF,
                config & 0xFF
            ]
        )

        # Esperar conversión
        time.sleep(0.02)

        data = bus.read_i2c_block_data(
            ADS1115_ADDR,
            REG_CONVERSION,
            2
        )

        raw = (data[0] << 8) | data[1]

        # Convertir a signed 16 bits
        if raw > 32767:
            raw -= 65536

        # PGA +/-4.096 V
        voltaje_adc = raw * 4.096 / 32768.0

        # Divisor 4K7 / 4K7
        voltaje_an1 = voltaje_adc * 2.0

        return raw, voltaje_adc, voltaje_an1


try:

    raw, vadc, van1 = leer_an1()

    print("==============================")
    print("LECTURA ANALÓGICA AN1")
    print("==============================")
    print(f"RAW ADS1115 : {raw}")
    print(f"Voltaje ADC : {vadc:.3f} V")
    print(f"Voltaje AN1 : {van1:.3f} V")
    print("==============================")

except Exception as e:

    print(
        f"ERROR: {type(e).__name__}: {e}"
    )