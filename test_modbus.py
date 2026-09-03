import yaml
import minimalmodbus
import serial


def cargar_sensor():
    with open("tht03r.yml", "r") as f:
        cfg = yaml.safe_load(f)

    sensor = cfg["medidores"]["tht03r_sensor"]
    return sensor


def crear_instrumento(sensor):
    instrumento = minimalmodbus.Instrument(
        sensor["port"],
        int(sensor["slave_id"])
    )

    instrumento.mode = minimalmodbus.MODE_RTU

    instrumento.serial.baudrate = int(sensor["baudrate"])
    instrumento.serial.bytesize = int(sensor["bytesize"])
    instrumento.serial.stopbits = int(sensor["stopbits"])
    instrumento.serial.timeout = float(sensor["timeout"])

    parity_map = {
        "N": serial.PARITY_NONE,
        "E": serial.PARITY_EVEN,
        "O": serial.PARITY_ODD
    }

    instrumento.serial.parity = parity_map.get(
        str(sensor["parity"]).upper(),
        serial.PARITY_NONE
    )

    instrumento.clear_buffers_before_each_transaction = True
    instrumento.close_port_after_each_call = True

    if sensor.get("debug", False):
        instrumento.debug = True

    return instrumento


def leer_sensor():
    sensor = cargar_sensor()
    instrumento = crear_instrumento(sensor)

    print("===================================")
    print("PRUEBA SENSOR THT03R MODBUS RTU")
    print("===================================")
    print(f"Puerto   : {sensor['port']}")
    print(f"Slave ID : {sensor['slave_id']}")
    print(f"Baudrate : {sensor['baudrate']}")
    print("-----------------------------------")

    for reg in sensor["registers"]:

        nombre = reg["name"]
        address = int(reg["address"])
        fc = int(reg.get("fc", 3))
        decimals = int(reg.get("decimals", 0))

        try:
            valor = instrumento.read_register(
                registeraddress=address,
                number_of_decimals=decimals,
                functioncode=fc,
                signed=False
            )

            if nombre.lower() == "temperature":
                unidad = "°C"

            elif nombre.lower() == "humidity":
                unidad = "%RH"

            else:
                unidad = ""

            print(
                f"{nombre:12}: {valor} {unidad}"
            )

        except Exception as e:
            print(
                f"ERROR leyendo {nombre} "
                f"(registro {address}): "
                f"{type(e).__name__}: {e}"
            )

    print("===================================")


if __name__ == "__main__":
    try:
        leer_sensor()

    except FileNotFoundError:
        print("ERROR: No se encontró el archivo tht03r.yml")
        print("Debe estar en:")
        print("/home/pi/lab1/lab1/tht03r.yml")

    except KeyError as e:
        print(f"ERROR en la estructura del YAML: falta {e}")

    except PermissionError:
        print("ERROR: Sin permisos para acceder al puerto serie")

    except Exception as e:
        print(
            f"ERROR GENERAL: {type(e).__name__}: {e}"
        )