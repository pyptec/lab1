# Sistema de Monitoreo de Temperatura Unificado

Este proyecto implementa una solución de monitoreo de temperatura para Raspberry Pi, cumpliendo con las especificaciones del Proyecto 1. 

## Estructura del Proyecto

El sistema está organizado de la siguiente manera:

- `main.py`: Es el punto de entrada. Inicia el motor principal y el servidor API web en segundo plano.
- `config.yaml`: Archivo central donde se configuran los intervalos, umbrales de alerta y nombres de los archivos de salida.
- `core/`:
  - `sensors.py`: Maneja la lectura de la temperatura interna del SoC y del sensor externo (THT03R). Si el sensor físico falla o no está, usa un generador de valores simulados automáticamente.
  - `engine.py`: El corazón del sistema. Un bucle infinito que lee datos y orquesta a los demás módulos.
  - `storage.py`: Encargado de guardar los datos en formato `.csv` y `.json`.
  - `alerts.py`: Lógica para verificar los umbrales de temperatura y lanzar alertas visuales (con colores en terminal) y simular envíos de correo.
  - `logger.py`: Configura un sistema de *Logging Rotativo*, lo que asegura que los archivos `.log` nunca excedan los 10MB.
- `reporting/`:
  - `generator.py`: Cada `X` lecturas (configurable, por defecto 30), genera un resumen estadístico (TXT), un reporte formateado en Markdown (MD) y una gráfica de las temperaturas a lo largo del tiempo usando Matplotlib (PNG).
- `api/`:
  - `server.py`: Servidor HTTP ligero basado en Flask que expone los datos capturados en tiempo real.

## Requisitos

```bash
pip install pyyaml flask matplotlib
```

*(Nota: Si usas el sensor físico THT03R, el sistema intentará apoyarse en los módulos `util` y `modbusdevices`).*

## Cómo Usarlo

1. Asegúrate de estar en la carpeta raíz (`proyecto_temperatura/`).
2. Revisa el archivo `config.yaml` para cambiar los tiempos de lectura (por defecto, lee cada 5 segundos y genera reportes cada 30 lecturas).
3. Inicia el sistema:

```bash
python main.py
```

### Limpiar Datos Anteriores

Si deseas borrar todo el historial de ejecuciones previas (logs, json, csv, gráficas) sin iniciar el monitoreo, puedes usar la bandera `--clean`:

```bash
python main.py --clean
```

### Ver el Sistema en Acción

Mientras el script se está ejecutando, podrás ver:

1. **La Salida en la Terminal:**
   Verás mensajes informativos con las temperaturas leídas cada pocos segundos. Si la temperatura supera los 70°C o 80°C, verás alertas de color amarillo o rojo.

2. **Los Archivos Creados:**
   En la misma carpeta empezarán a aparecer:
   - `sistema.log`: Historial técnico detallado.
   - `datos.csv` y `datos.json`: Historial de capturas.
   - `reporte.txt`, `reporte.md` y `grafica_temperatura.png`: Estos se generarán/actualizarán automáticamente cada vez que se cumpla el ciclo de reportes.

3. **API REST y Dashboard Web:**
   El sistema levanta un servidor local donde puedes ver los datos en vivo. 
   
   **Dashboard:**
   Abre tu navegador web e ingresa a:
   [http://localhost:5001/](http://localhost:5001/)
   Verás una interfaz simple con los datos en tiempo real y una gráfica.

   **Endpoints (para terminal o integración):**
   - Estado del sistema: `curl http://localhost:5001/status`
   - Última temperatura leída: `curl http://localhost:5001/temp`
   - Historial completo en JSON: `curl http://localhost:5001/history`

Para detener el sistema limpiamente, simplemente presiona `Ctrl + C` en la terminal donde corre `main.py`. El programa detectará la interrupción y generará un reporte final antes de apagarse.
# lab1
