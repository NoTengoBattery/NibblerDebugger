#!/usr/bin/env python2
# -*- coding: utf-8 -*-
from collections import deque

import serial

archivo_puerto = "/dev/null"  # type: str
tasa_transferencia = 9600  # type: int
tiempo_espera = 0  # type: int
conexion_serial = None  # type: serial
bits = 14


# Envía una cadena de caracteres al puerto serial y espera una respuesta
def escribir_puerto(comando):  # type: () -> list
    """
    Envía un comando al puerto serial, un String tal cual se recibe en `comando`. Posteriormente espera una respuesta
    y divide las respuestas en los bloques enviados por el depurador, como un arreglo de dos dimensiones.
    :param comando: el comando a enviar al depurador Arduino
    :return: una lista de dos dimensiones, en una dimensión son las respuestas de Arduino y en la otra la información
    obtenida
    """
    global conexion_serial
    conexion_serial.write(comando)
    bloques = []
    while conexion_serial.inWaiting() >= bits:
        bloque = leer_puerto()
        if len(bloque) == bits:
            bloques.append(bloque)
    conexion_serial.write([0])
    while conexion_serial.inWaiting():
        conexion_serial.read()
    return bloques


def leer_puerto():  # type: () -> list
    """
    Obtiene un bloque de bytes con el formato conocido desde el depurador y lo devuelve como una lista.
    :return: información obtenida del depurador mediante el puerto serial
    """
    global conexion_serial

    def existe_en_lista(lista1, lista2):  # type: (list, list) -> bool
        """
        Determina si la sublista `lista1` existe en la lista `lista2`, y devuelve True si existe, o False si no.
        :param lista1: sublista
        :param lista2: lista
        :return: True si la sublista existe en la lista
        """
        str1 = ''.join(map(str, lista1))
        str2 = ''.join(map(str, lista2))
        return str1 in str2

    # Alinear el buffer: a veces, el puerto serial no recibe los datos alineados. Esto descarta la información inválida
    # hasta el siguiente bloque de bits válido
    bloque = []
    d = deque(maxlen=2)
    while conexion_serial.inWaiting() and not existe_en_lista([ord('\n'), ord('\r')], d):
        d.append(ord(conexion_serial.read()))
    while conexion_serial.inWaiting() and len(bloque) < bits - 2:
        bloque.append(ord(conexion_serial.read()))

    if len(bloque) == bits - 2:
        bloque.extend(d)
        return bloque
    else:
        return []


def abrir_puerto(archivo, baud, modo):
    """
    Dado el puerto serial, el baudrate y el modo de operación, intenta establecer comunicación con del depurador.
    :param archivo: el archivo de UNIX que representa al puerto serial (debe tener permiso para acceder al archivo,
    o pertenecer al grupo de usuarios `dialout`).
    :param baud:
    :param modo:
    :return:
    """
    global archivo_puerto
    global tasa_transferencia
    global tiempo_espera
    global conexion_serial
    serial_tmp = serial.Serial(port=archivo, baudrate=baud, timeout=tiempo_espera)
    print("Esperando a que Arduino inicialice el puerto...")
    # Cambia el modo a bloqueador del hilo
    serial_tmp.timeout = None
    # Lee un byte que envía Arduino cuando la conexión está lista
    initchr = ord(serial_tmp.read(1))
    if initchr != 64:
        raise IOError("El depurador de Arduino no respondió correctamente a la inicialización. Verifique la conexión "
                      "y que Arduino esté ejecutando el programa correcto.")
    serial_tmp.timeout = tiempo_espera
    line = False
    while not line:
        serial_tmp.write(modo)
        line = serial_tmp.readline()
    if line != "0p" + modo + "\r\n":
        raise IOError("No se puede conectar con el depurador.")
    archivo_puerto = archivo
    tasa_transferencia = baud
    conexion_serial = serial_tmp
    bloques = []
    while conexion_serial.inWaiting() > 0:
        bloque = leer_puerto()
        if len(bloque) != 0:
            bloques.append(bloque)
    conexion_serial.write([0])
    while conexion_serial.inWaiting():
        conexion_serial.read()
    return bloques
