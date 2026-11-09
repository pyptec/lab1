# Proyecto de temperatura

Sistema de monitoreo para Raspberry Pi: temperatura SoC, sensor THT03R por Modbus RTU, GPIO, RTC, UPS, almacenamiento CSV/JSON, reportes y API Flask.

## Requisitos

Python 3, Git si se clona el repositorio y Raspberry Pi con el hardware conectado: THT03R, interfaz serie Modbus, entradas/salidas GPIO, RTC y UPS cuando se utilicen. El script test_an1.py requiere un ADS1115 por I2C. El puerto serie debe estar habilitado y ser accesible.
Windows permite preparar dependencias y validar configuraciones/imports; la ejecucion completa requiere dispositivos y rutas Linux. No hay simulacion completa de hardware.

## Estructura básica del proyecto

```text
proyecto_temperatura/
|-- main.py
|-- config.yaml
|-- tht03r.yml
|-- requirements.txt
|-- install_dependencies.sh
|-- README.md
|-- DEPENDENCIAS.md
|-- BITACORA.md
|-- test_modbus.py
|-- test_an1.py
|-- core/              # motor, sensores, GPIO, RTC, UPS, alertas, almacenamiento
|-- api/
|   |-- server.py
|   `-- templates/index.html
`-- reporting/generator.py
```

## Crear entorno virtual en Windows

```powershell
cd D:\promate\cursos\U_javeriana\sistemas-embebidos\proyecto\proyecto_temperatura\proyecto_temperatura
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Si PowerShell bloquea la activacion, permite scripts solo en la sesion actual:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

## Crear entorno virtual en Raspberry Pi / Linux

Copia o clona el repositorio y ajusta la ruta si usaste otro nombre:

```bash
cd ~/proyecto_temperatura
sudo apt update
sudo apt install -y python3-venv python3-full
python3 -m venv .venv
source .venv/bin/activate
```

Antes de instalar lgpio desde fuentes:

```bash
sudo apt install -y python3-dev build-essential swig liblgpio-dev
```

Alternativa automatizada (prepara .venv, paquetes apt, pip e imports):

```bash
chmod +x install_dependencies.sh
./install_dependencies.sh
source .venv/bin/activate
```

## Actualizar pip

Con el entorno virtual activado, en ambas plataformas:

```bash
python -m pip install --upgrade pip
```

## Instalar dependencias

```bash
pip install -r requirements.txt
```

PyYAML, Flask, matplotlib, minimalmodbus, pyserial, gpiozero y smbus2 corresponden a imports directos. lgpio es el controlador indirecto de GPIO Zero y se instala solo en Linux. No hay versiones fijadas: no se ha comprobado una combinacion completa en Raspberry Pi. Clasificacion y ubicaciones en DEPENDENCIAS.md.

## Verificar instalación

Con .venv activado:

```bash
python -m pip check
python -c "import yaml, flask, matplotlib, minimalmodbus, serial, gpiozero; print('Dependencias Windows OK')"
python -c "from pathlib import Path; import yaml; d=yaml.safe_load(Path('tht03r.yml').read_text(encoding='utf-8')); print(d['medidores']['tht03r_sensor'])"
```

En Raspberry Pi/Linux verifica ademas I2C y el controlador:

```bash
python -c "import yaml, flask, matplotlib, minimalmodbus, serial, gpiozero, smbus2, lgpio; print('Dependencias Raspberry Pi OK')"
```

smbus2 se instala en Windows pero su import requiere fcntl (biblioteca estandar Unix); no esta disponible en Windows y no debe agregarse como paquete pip. La prueba Windows lo excluye.

Los imports no prueban el hardware. No importes test_an1.py para comprobar dependencias: accede a I2C al cargarse.

## Ejecutar el proyecto

Desde la raiz del repositorio y con .venv activado.

Windows (la ejecucion completa necesita hardware Linux y no se garantiza en Windows):

```powershell
python main.py
```

Raspberry Pi/Linux:

```bash
python main.py
```

config.yaml define intervalos (5 segundos), reportes (cada 30 lecturas), umbrales, GPIO y salidas. Ctrl+C detiene el monitoreo y solicita un reporte final.

Para borrar salidas anteriores mediante la opcion existente:

```bash
python main.py --clean
```

## Configuración de tht03r.yml

El YAML conserva la jerarquia medidores.tht03r_sensor. config.yaml selecciona cfg_section: tht03r_sensor y cfg_file: tht03r.yml. Las rutas relativas de cfg_file se resuelven desde la raiz del proyecto; se siguen aceptando rutas absolutas.

- port: /dev/ttyS0, puerto serie configurado.
- slave_id: 4, direccion Modbus del instrumento.
- baudrate: 9600; bytesize: 8; parity: N; stopbits: 1; timeout: 1.
- debug y simular son booleanos false. El lector actual no utiliza simular para sustituir el hardware.
- registers contiene Temperature (address 0) y Humidity (address 1), fc 3 y decimals 1. El lector usa name, address, fc y decimals. Se conservan readWrite, scale, unit y alias, aunque este lector no los consume.
- control conserva hu_ppm_low: 85, hu_ppm_high: 90, temp_c_low: 18 y temp_c_high: 19. No hay codigo Python que consuma estas claves actualmente; no cambian el control GPIO existente.

## Puerto serial en Raspberry Pi

El proyecto configura /dev/ttyS0: debe existir, estar habilitado y tener permisos de lectura/escritura para el usuario:

```bash
ls -l /dev/ttyS0
groups
test -r /dev/ttyS0 && test -w /dev/ttyS0 && echo "Puerto accesible"
```

Comprueba el grupo propietario (habitualmente dialout) y la configuracion UART. GPIO requiere acceso a /dev/gpiochip*, test_an1.py a /dev/i2c-1; RTC y temperatura SoC se leen desde /sys/class/rtc/rtc0 y /sys/class/thermal/thermal_zone0/temp.

## Solución de problemas

### ModuleNotFoundError

En Linux:

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

En Windows activa .venv con .\.venv\Scripts\Activate.ps1 y repite la instalacion.

### externally-managed-environment

Se esta usando el Python administrado por el sistema. Activa .venv y usa su pip; no instales paquetes Python globalmente.

### Error cargando tht03r.yml

La causa encontrada era la ruta absoluta /home/pi/lab1/lab1/tht03r.yml en config.yaml y como valor predeterminado de core/sensors.py; no existe en esta copia Windows. La sintaxis YAML, los tipos y la jerarquia eran correctos.
Ahora cfg_file es tht03r.yml y el lector lo resuelve desde la raiz del proyecto. test_modbus.py tambien carga desde su propia ubicacion. Si persiste, comprueba que el archivo este copiado, sus permisos y cfg_section. main.py sigue requiriendo iniciarse desde la raiz para cargar config.yaml.

### Error de puerto serial

Verifica /dev/ttyS0 y sus permisos con los comandos anteriores. Un fallo al abrir el puerto despues de cargar el YAML es un problema distinto; Windows no dispone de ese dispositivo Linux. No se modifico el puerto configurado.

### UPS externa

core/ups.py ejecuta /home/pi/UPS_HAT_E/ups.py con /usr/bin/python3. Ese script no esta incluido; sus dependencias no se pueden determinar. Los paquetes de .venv no se comparten automaticamente con ese proceso. Hay que revisar el script externo antes de decidir dependencias apt.

## Salidas y API

El sistema guarda sistema.log (rotacion de 10 MB y cinco copias), datos.csv, datos.json, reporte.txt, reporte.md y grafica_temperatura.png.
El dashboard configurado esta en http://localhost:5001/ y los endpoints son /status, /temp y /history. Ejemplo:

```bash
curl http://localhost:5001/status
curl http://localhost:5001/temp
curl http://localhost:5001/history
```

Las alertas imprimen colores; el envio de correo actual es simulado.

## Salir del entorno virtual

```bash
deactivate
```

## Funcionamiento con RTC o THT03R temporalmente ausentes

El arranque no se cancela si falta /dev/ttyS0. Si el puerto no existe, el sensor no responde o una respuesta Modbus es invalida, se registra WARNING con la causa y se devuelve None para temperatura ambiente y humedad. Se libera la conexion fallida y se reconstruye en la siguiente lectura del motor (intervalo configurado, actualmente 5 segundos, mas el tiempo de lectura). Cuando las lecturas vuelven, se registra INFO de recuperacion. No se simulan valores ni se presentan lecturas antiguas como actuales.

Si falta el RTC, se registra WARNING y se usa datetime.now() del sistema; se vuelve a probar el RTC en cada ciclo y se registra su recuperacion. Esto no garantiza que el reloj del sistema este sincronizado.

El log muestra -- para temperaturas/humedad ausentes; la API y el JSON usan null, y el CSV deja esos campos vacios. Las alertas se evaluan con las temperaturas disponibles. Si ninguna esta disponible, se registra una advertencia sin comparar None. Los reportes existentes se omiten con advertencia mientras no haya suficientes datos; no se altera su formato ni se inventan muestras.

GPIO, UPS y API mantienen su comportamiento existente. No se captura indiscriminadamente cualquier error del motor: errores de configuracion o programacion siguen visibles. No se modifican puerto, slave_id, baudrate, registros, umbrales ni pines.

Pruebas sin hardware:

```bash
cd /home/pi/lab1
.venv/bin/python -m unittest discover -s tests -p 'test_hardware_failures.py' -v
```

La suite sustituye los dispositivos por mocks; no abre UART ni GPIO. El logger real puede crear sistema.log en el directorio actual. Se verifican desconexion/recuperacion, RTC ausente, alertas con None, continuidad del motor, API y omision segura de reportes. La validacion realizada fue en Windows con .venv; queda pendiente repetirla y comprobar hardware real en Raspberry Pi.

Ejecucion habitual en Raspberry Pi:

```bash
cd /home/pi/lab1
source .venv/bin/activate
python main.py
```
