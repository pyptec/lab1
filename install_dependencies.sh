#!/usr/bin/env bash
set -euo pipefail
trap 'echo "Error de instalacion en la linea $LINENO." >&2' ERR
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"

command -v python3 >/dev/null 2>&1 || {
    echo "Falta Python 3. Instala python3 con apt y vuelve a ejecutar." >&2
    exit 1
}
command -v apt-get >/dev/null 2>&1 || {
    echo "Este instalador requiere Raspberry Pi OS / Debian con apt-get." >&2
    exit 1
}
[[ -f requirements.txt ]] || { echo "Falta requirements.txt." >&2; exit 1; }

# Solo apt necesita privilegios; pip se ejecuta siempre dentro de .venv.
apt_cmd=(apt-get)
if (( EUID != 0 )); then
    command -v sudo >/dev/null 2>&1 || {
        echo "Falta sudo para instalar dependencias del sistema." >&2
        exit 1
    }
    apt_cmd=(sudo apt-get)
fi
packages=(python3-venv python3-full python3-dev build-essential swig liblgpio-dev)
missing=()
for package in "${packages[@]}"; do
    if ! dpkg-query -W -f='${Status}' "$package" 2>/dev/null | grep -qx 'install ok installed'; then
        missing+=("$package")
    fi
done
if (( ${#missing[@]} )); then
    "${apt_cmd[@]}" update
    "${apt_cmd[@]}" install -y "${missing[@]}"
fi

if [[ ! -e .venv ]]; then
    python3 -m venv .venv
fi
[[ -x .venv/bin/python && -f .venv/pyvenv.cfg ]] || {
    echo ".venv existe pero no es un entorno virtual Linux valido." >&2
    exit 1
}
.venv/bin/python -c 'import sys; assert sys.prefix != sys.base_prefix, "Python debe pertenecer a un entorno virtual"'
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m pip check
MPLBACKEND=Agg .venv/bin/python -c "import yaml, flask, matplotlib.pyplot, minimalmodbus, serial, gpiozero, smbus2, lgpio; print('Dependencias principales OK')"

echo "Instalacion Python completada; el hardware no se ha probado."
if [[ ! -f /home/pi/UPS_HAT_E/ups.py ]]; then
    echo "PENDIENTE: falta /home/pi/UPS_HAT_E/ups.py; sus dependencias no estan verificadas."
else
    echo "PENDIENTE: revisar dependencias de /home/pi/UPS_HAT_E/ups.py (usa /usr/bin/python3)."
fi
echo "Revisa I2C, UART, RTC, permisos de dispositivos y la ruta cfg_file de config.yaml."
