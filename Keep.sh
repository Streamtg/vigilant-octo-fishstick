#!/bin/bash

echo "[KeepAlive] Iniciando simulación de uso de RAM y red (cada 6 horas)..."

while true
do
    # Uso de RAM aleatorio entre 30 y 100 MB
    RAM_MB=$((30 + RANDOM % 71))
    dd if=/dev/zero of=/tmp/fillmem bs=1M count=$RAM_MB status=none
    rm -f /tmp/fillmem

    # Selección aleatoria de archivo de red
    if [ $((RANDOM % 2)) -eq 0 ]; then
        NET_FILE="https://speed.hetzner.de/100MB.bin"
    else
        NET_FILE="https://speed.hetzner.de/10MB.bin"
    fi

    # Tráfico de red
    curl -s "$NET_FILE" -o /dev/null
    ping -c $((1 + RANDOM % 5)) google.com > /dev/null 2>&1

    echo "[KeepAlive] Actividad ejecutada → RAM: ${RAM_MB}MB | Archivo: ${NET_FILE}"

    # Esperar 6 horas antes de la próxima actividad
    sleep 21600  # 6 horas en segundos
done
