# Dependencias e instalacion en Raspberry Pi

Revision estatica de los 17 archivos Python del repositorio, incluidos scripts de prueba. No existe .venv en esta copia; las versiones quedan sin fijar.

| Paquete pip | Import | Archivos y lineas |
|---|---|---|
| PyYAML | yaml | core/config_loader.py:1; core/sensors.py:2; test_modbus.py:1 |
| Flask | flask | api/server.py:1 |
| matplotlib | matplotlib.pyplot | reporting/generator.py:1 |
| minimalmodbus | minimalmodbus | core/sensors.py:3; test_modbus.py:2 |
| pyserial | serial | core/sensors.py:4; test_modbus.py:3 |
| gpiozero | gpiozero | core/outputs.py:2 |
| smbus2 | smbus2 | test_an1.py:1 |
| lgpio | controlador de gpiozero | Dependencia de ejecucion indirecta para GPIO en .venv; no hay import directo del proyecto. |

Libreria estandar excluida: sys, os, time, datetime, threading, logging, logging.handlers, csv, json, random, subprocess, re.
Modulos locales excluidos: core y sus modulos, api.server, reporting.generator y todos los imports relativos.
No aparecen imports de util ni modbusdevices: la nota antigua del README estaba desactualizada.
Las dependencias transitivas de pip se resuelven automaticamente.

## Sistema y hardware

El instalador usa apt solo para paquetes ausentes: python3-venv, python3-full, python3-dev, build-essential, swig, liblgpio-dev. Los cuatro ultimos permiten compilar el controlador lgpio si no hay wheel compatible.
No se necesitan hwclock, i2c-tools ni python3-smbus para los imports del codigo revisado.
RTC y temperatura SoC se leen por sysfs (core/rtc.py:12-13, core/sensors.py:11); requieren soporte y configuracion del kernel, no otro paquete pip.
test_an1.py usa SMBus(1): se necesita I2C habilitado y acceso a /dev/i2c-1.
GPIO requiere acceso a /dev/gpiochip*, y Modbus acceso al puerto configurado /dev/ttyS0.
Habilita las interfaces correspondientes y configura el RTC segun el hardware; consulta raspi-config y los permisos de los grupos gpio, i2c y dialout. El instalador no cambia interfaces, grupos ni overlays.

**Pendiente externo:** core/ups.py:12,38-42 ejecuta /home/pi/UPS_HAT_E/ups.py mediante /usr/bin/python3. Ese archivo no esta disponible: no se pueden identificar sus imports ni garantizar la UPS. Instalar paquetes en .venv no los hace visibles a ese proceso. Hay que revisar ese script antes de decidir paquetes apt; no se inventan dependencias ni se instala Python global con pip.

**Ruta existente:** config.yaml establece /home/pi/lab1/lab1/tht03r.yml (tambien valor predeterminado en core/sensors.py:40). Comprueba que existe en la Pi: ejecutar desde ~/lab1 no corrige esa ruta absoluta. No se modifica la configuracion en esta tarea.

## Instalacion y validacion

Ejecutar como usuario habitual con sudo disponible:

```bash
cd ~/lab1
chmod +x install_dependencies.sh
./install_dependencies.sh
```

El instalador usa exclusivamente .venv/bin/python para pip, comprueba pip check y todos los imports externos sin importar modulos locales ni inicializar sensores. No usar sudo pip ni --break-system-packages.

Validacion manual:

```bash
MPLBACKEND=Agg .venv/bin/python -c "import yaml, flask, matplotlib.pyplot, minimalmodbus, serial, gpiozero, smbus2, lgpio; print('Dependencias principales OK')"
```

Despues de revisar configuracion y hardware:

```bash
source .venv/bin/activate
python main.py
```

Esta validacion de imports no prueba sensores, GPIO, Modbus, RTC ni UPS. No ejecutar test_an1.py como prueba de imports: accede a I2C al cargarlo.

Fuentes de instalacion verificadas:
- https://gpiozero.readthedocs.io/en/stable/installing.html (lgpio y prerrequisitos de compilacion).
- https://pypi.org/project/smbus2/ (nombre de distribucion).
- https://www.raspberrypi.com/documentation/computers/configuration.html (interfaces hardware).

## Actualizacion 2026-11-09, Prompt 2

lgpio se restringe a Linux mediante marcador de plataforma. La ruta absoluta del YAML descrita antes se corrigio: config.yaml usa tht03r.yml y core/sensors.py resuelve rutas relativas desde la raiz del proyecto. test_modbus.py usa su propia ubicacion. Las referencias de linea anteriores corresponden a la revision inicial.

Validacion Windows Prompt 2: smbus2 requiere fcntl (estandar Unix), por lo que su import solo se valida en Linux. Los otros seis paquetes directos se importaron en .venv Windows; pip check correcto. No se agrega fcntl como paquete externo.
