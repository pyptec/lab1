# Bitacora

## 2026-11-09 — Prompt 1

- Objetivo: preparar dependencias reales, instalador aislado y documentacion para Raspberry Pi sin modificar logica.
- Numeracion: primera entrada de esta copia; no se encontro bitacora previa ni evidencia de numeracion anterior.
- Prompt utilizado: solicitud adjunta «Estoy trabajando en un proyecto Python llamado lab1 en una Raspberry Pi»: revisar todos los .py, clasificar imports, generar requirements.txt e install_dependencies.sh, validar con .venv, registrar cambios y preservar logica y contenido previo.
- Archivos revisados: main.py, test_an1.py, test_modbus.py, api/__init__.py, api/server.py, core/__init__.py, core/alerts.py, core/config_loader.py, core/engine.py, core/logger.py, core/outputs.py, core/rtc.py, core/sensors.py, core/storage.py, core/ups.py, reporting/__init__.py, reporting/generator.py; tambien README.md, config.yaml y tht03r.yml.
- Imports externos: yaml, flask, matplotlib.pyplot, minimalmodbus, serial, gpiozero, smbus2. Ubicaciones y clasificacion completa en DEPENDENCIAS.md.
- Dependencias agregadas: PyYAML, Flask, matplotlib, minimalmodbus, pyserial, gpiozero, smbus2; lgpio como controlador indirecto de GPIO. Sin versiones por ausencia de .venv verificable.
- Sistema: python3-venv, python3-full; python3-dev, build-essential, swig, liblgpio-dev para compilar lgpio. Hardware requiere interfaces I2C/UART, controlador RTC y permisos de dispositivos.
- Archivos creados: requirements.txt, install_dependencies.sh, DEPENDENCIAS.md, BITACORA.md.
- Archivo modificado: README.md, solo seccion de requisitos para remitir al instalador y retirar referencia obsoleta a util/modbusdevices.
- Validaciones realizadas: lectura recursiva de los 17 archivos Python e inventario de imports con rg; revision de llamadas externas y configuracion; consulta de documentacion oficial de gpiozero y smbus2. No se ejecuto main.py ni scripts de hardware.
- Pendientes: instalacion apt/pip y validacion de imports en Raspberry Pi no ejecutadas en este equipo Windows; script UPS externo ausente, dependencias desconocidas y Python del sistema independiente del venv; ruta absoluta del YAML requiere revision. No hay garantia de funcionamiento hardware con solo instalar paquetes.

- Validacion final adicional: analisis AST de los 17 archivos correcto; bash -n con Git Bash correcto; instalador con LF y sin BOM; git diff --check sin errores; git diff de archivos .py vacio. WSL no dispone de /bin/bash; se utilizo Git Bash para comprobar sintaxis. No se instalaron paquetes ni se ejecutaron imports del entorno Raspberry Pi.

## 2026-11-09 — Prompt 2

- Problema reportado y prompt utilizado: diagnosticar carga/uso de tht03r.yml, corregir lo minimo, revisar dependencias y completar README, instalador y bitacora sin alterar parametros Modbus ni control.
- Causa raiz comprobada: config.yaml y el valor predeterminado de core/sensors.py apuntaban a /home/pi/lab1/lab1/tht03r.yml, inexistente en esta copia Windows, aunque el YAML existe en la raiz. test_modbus.py dependia del directorio actual y mostraba una ruta absoluta obsoleta.
- YAML validado con PyYAML: sintaxis y jerarquia medidores.tht03r_sensor correctas; debug y simular son bool false, parity es str N; registros Temperature/Humidity y control correctos. control, simular y metadatos auxiliares de registros no son consumidos por los lectores actuales.
- Archivos revisados: los mismos 17 archivos Python enumerados en Prompt 1 (excluyendo .venv), config.yaml, tht03r.yml, README.md, requirements.txt, install_dependencies.sh y DEPENDENCIAS.md.
- Python modificado: core/sensors.py resuelve cfg_file relativo a la raiz del proyecto, conserva rutas absolutas y abre UTF-8; test_modbus.py usa el YAML junto al script, abre UTF-8 y muestra la ruta real en errores. No cambian lecturas, control ni parametros.
- Configuracion modificada: solo sensor_tht03r.cfg_file en config.yaml pasa a tht03r.yml.
- Cambios en tht03r.yml: ninguno. Puerto, slave_id, baudrate, registros y control intactos.
- Dependencias encontradas: PyYAML, Flask, matplotlib, minimalmodbus, pyserial, gpiozero, smbus2; lgpio indirecto en Linux. Estandar/local excluidos. pathlib agregado al codigo pertenece a la biblioteca estandar.
- requirements.txt: lgpio restringido mediante sys_platform == "linux". Sin fijar versiones porque la verificacion Windows no demuestra compatibilidad completa en Raspberry Pi.
- README.md ampliado con preparacion Windows/Linux, venv, pip, imports por plataforma, ejecucion, configuracion, diagnostico serie, causa YAML, salidas y API; conserva informacion util anterior.
- install_dependencies.sh: revisado y conservado sin cambios; cumple preparacion aislada, apt, verificacion Python y parada ante errores.
- DEPENDENCIAS.md: agregadas aclaraciones sobre rutas y plataformas. .gitignore creado para excluir .venv/ generado durante la validacion.
- Validaciones reales: creado .venv en Windows con Python 3.10; pip install -r requirements.txt completo; pip check: No broken requirements found; bash -n correcto con Git Bash.
- Imports: yaml, flask, matplotlib.pyplot, minimalmodbus, serial y gpiozero correctos en .venv. smbus2 instalado pero su import en Windows falla con ModuleNotFoundError: fcntl; requiere Unix, no se agrega fcntl a requirements. lgpio omitido correctamente por marcador Linux.
- AST: 17 archivos parseados e inventario externo coincide con requirements (mas lgpio indirecto).
- Regresion de rutas: cargado YAML con ruta configurada, predeterminada y absoluta, y con test_modbus.cargar_sensor desde otro directorio; todas correctas. _create_instrument sustituido por mock para impedir apertura serie.
- Imports internos: 12 modulos importados sin iniciar hardware; core.logger sustituido por logger en memoria para evitar crear sistema.log. No se valida asi la inicializacion real del logger. test_an1.py no importado porque ejecuta I2C al cargarlo.
- Pendientes: no ejecutado main.py ni hardware/Modbus, no ejecutado instalador apt en Raspberry Pi; lgpio/smbus2 requieren validacion Linux. Script externo UPS ausente; no se conocen sus dependencias.

## 2026-11-09 — Prompt 3

- Objetivo y prompt: permitir operacion continua sin RTC, /dev/ttyS0 o sensor THT03R, registrar fallos y recuperar automaticamente al volver el hardware. El mensaje recibido termina en "PRINC"; se implementaron los requisitos completos recibidos antes de ese corte.
- Diagnostico: AmbientSensor propagaba SerialException durante construccion e impedia inicializar GPIO/servicios; las lecturas fallidas devolvian None pero el motor intentaba formatearlo como float y AlertManager usaba max con None. RTC ya permitia continuar pero solo registraba ERROR y no notificaba recuperacion.
- Archivos revisados: core/sensors.py, core/rtc.py, core/engine.py, core/alerts.py, core/storage.py, reporting/generator.py, api/server.py, api/templates/index.html, config.yaml y documentacion; implementacion instalada de minimalmodbus para comprobar apertura/cierre y excepciones.
- Archivos modificados: core/sensors.py, core/rtc.py, core/engine.py, core/alerts.py, README.md y BITACORA.md. Archivo creado: tests/test_hardware_failures.py.
- Cambios: capturas especificas de errores de E/S y Modbus; cierre de conexion fallida y reintento por ciclo; WARNING con causa y reintento, INFO al recuperar lecturas; reloj del sistema si RTC falla; log con -- para valores ausentes; alertas usan temperaturas disponibles. None se conserva como dato ausente, sin simulacion.
- No se modificaron configuracion YAML, pines, umbrales, parametros Modbus, UPS, API ni dependencias. No se agrego systemd porque no se solicito configurar un servicio.
- Validaciones reales: siete pruebas unittest con .venv Windows, todas OK. Cubren puerto ausente en arranque y recuperacion, desconexion serie, timeout/respuesta invalida y recuperacion, error de configuracion no oculto, RTC ausente/invalido y recuperacion, alertas parciales/sin datos, dos ciclos del motor manteniendo GPIO/UPS/almacenamiento/API, y reportes sin datos completos. Modbus/GPIO/UPS simulados; RTC con archivos temporales; Flask mediante test_client sin servidor de red.
- Primera ejecucion: seis pruebas pasaron y una fallo por fixture de reporte sin timestamp; se completo el fixture y la suite final paso (7/7). No fue un fallo de produccion.
- git diff --check sin errores; logger y cache Matplotlib se mantuvieron en carpeta temporal al ejecutar las pruebas.
- Pendientes: cambios realizados en la copia local Windows, no desplegados ni ejecutados en /home/pi/lab1. No se hicieron lecturas fisicas, ni ejecucion real de main.py, ni validacion de recuperacion con dispositivos reales. Los reportes requieren suficientes datos como antes; relojes y dependencias del script UPS externo conservan sus limitaciones anteriores.
