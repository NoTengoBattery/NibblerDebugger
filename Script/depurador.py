#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
Depurador para la CPU Nibbler basado en Python 2 y Arduino Mega. Este depurador tiene como dependencia `curses` y
`pyserial`. Si no sabe como instalar bibliotecas para Python, visite el siguiente enlace:
http://rukbottoland.com/blog/como-instalar-un-paquete-python-con-pip/

Este depurador está basado en `curses`, por lo cual *solo se ejecutará en UNIX/UNIX-like* como macOS y GNU/Linux. Para
mayor comodidad, instale los binarios y las bibliotecas de desarrollo de ncurses desde el gestro de paquetedes de su
distribución de Linux, y en macOS desde su gestor de paquetes favorito (homebrew y macports funcionan bien).

macOS cuenta con una versión de ncurses instalada de fábrica, si no da problemas, evite instalar una nueva.

Este script, el esamblador y el ensamblador reverso son software libre bajo la licencia MIT (también conocida como X11).

Copyright (c) 2016 Oever González
"""
import sys
from curses import *
from math import floor

from ensamblador import ensamblar
from ensamblador_reverso import decodificar_datos, disasm
from receptor import *

min_x = 90
min_y = 28


def interface(pantalla):
    """
    Código de `curses` que muestra la interfaz del depurador.
    :param pantalla: la stdscr de `curses`
    """
    if has_colors():
        start_color()
        init_pair(1, COLOR_BLACK, COLOR_WHITE)
        init_pair(2, COLOR_CYAN, COLOR_BLACK)
        init_pair(3, COLOR_YELLOW, COLOR_BLUE)
        init_pair(4, COLOR_YELLOW, COLOR_RED)

    pantalla.border(0)

    # Calcula las dimensiones iniciales
    y_principal, x_principal = pantalla.getmaxyx()
    x_principal = min_x if min_x > x_principal else x_principal
    y_principal = min_y if min_y > y_principal else y_principal

    # Inicializa los objetos para las ventanas y los marcos. En este punto no tienen dimensiones definidas.
    ventana_principal = newwin(y_principal, x_principal, 0, 0)
    ventana_pc = newwin(y_principal, x_principal, 1, 1)
    ventana_datos = newwin(y_principal, x_principal, 1, 1)
    marco_comandos = newwin(y_principal, x_principal, 1, 1)
    ventana_comandos = newwin(y_principal, x_principal, 1, 1)
    ventana_comandos.scrollok(True)
    ventana_comandos.idlok(True)
    marco_disasm = newwin(y_principal, x_principal, 1, 1)
    ventana_disasm = newwin(y_principal, x_principal, 1, 1)
    ventana_disasm.scrollok(True)
    ventana_disasm.idlok(True)
    ventana_banderas = newwin(y_principal, x_principal, 1, 1)
    marco_entrada = newwin(y_principal, x_principal, 1, 1)
    ventana_entrada = newwin(y_principal, x_principal, 1, 1)
    ventana_entrada.scrollok(True)
    ventana_entrada.idlok(True)

    def val3op(cond, val_si, val_no):
        return val_si if cond else val_no

    def rewrite():
        """
        Actualiza la información que se presenta en la pantalla.
        """
        ventana_pc.addstr(1, 1, "PC: 0x{0:04X}".format(pc))
        ventana_pc.addstr(2, 1, "FETCHD: I[0x{0:01X}] O[0x{1:01X}], 0x{2:02X}".format(ejec >> 4, ejec & 0xF, ejec))
        ventana_pc.addstr(3, 1, "PROGBYTE: I[0x{0:01X}] O[0x{1:01X}]".format(progb >> 4, progb & 0xF))
        ventana_pc.addstr(4, 1, "FASE: {0:s}".format("OBTENIENDO" if fase == 0 else "EJECUTANDO"))

        ventana_datos.addstr(1, 1, "DATOS: 0x{0:02X}".format(datos))
        ventana_datos.addstr(2, 1, "BOTONES: 0x{0:02X}".format(boton))
        ventana_datos.addstr(3, 1, "| LEFT|RIGHT| DOWN|  UP |", A_BOLD | color_pair(3))
        ventana_datos.addstr(4, 1, "| {0:s} ".format("_=_" if boton >> 0 & 1 == 0 else "___"),
                             A_BOLD | color_pair(3 if boton >> 0 & 1 == 0 else 4))
        ventana_datos.addstr("| {0:s} ".format("_=_" if boton >> 1 & 1 == 0 else "___"),
                             A_BOLD | color_pair(3 if boton >> 1 & 1 == 0 else 4))
        ventana_datos.addstr("| {0:s} ".format("_=_" if boton >> 2 & 1 == 0 else "___"),
                             A_BOLD | color_pair(3 if boton >> 2 & 1 == 0 else 4))
        ventana_datos.addstr("| {0:s} |".format("_=_" if boton >> 3 & 1 == 0 else "___"),
                             A_BOLD | color_pair(3 if boton >> 3 & 1 == 0 else 4))
        ventana_datos.addstr(5, 1, "ACCUMULADOR: 0x{0:02X}".format(accum))
        ventana_datos.addstr(6, 1, "SALIDA: 0x{0:02X}".format(salida))

        ventana_comandos.addstr(comando + "\n")

        ventana_disasm.addstr(disasm(pc, ejec, progb, fase, acarreo, cero))

        ventana_banderas.addstr(3, 1, "{0:s}\t".format("ACTIVADO" if u0 >> 0 & 1 == 0 else "DESACTIV"),
                                A_BOLD | color_pair(3 if u0 >> 0 & 1 == 0 else 4))
        ventana_banderas.addstr("{0:s}\t".format("ACTIVADO" if u0 >> 1 & 1 == 0 else "DESACTIV"),
                                A_BOLD | color_pair(3 if u0 >> 1 & 1 == 0 else 4))
        ventana_banderas.addstr("{0:s}\t".format("ACTIVADO" if u0 >> 2 & 1 == 0 else "DESACTIV"),
                                A_BOLD | color_pair(3 if u0 >> 2 & 1 == 0 else 4))
        ventana_banderas.addstr("{0:s}".format("ACTIVADO" if u0 >> 3 & 1 == 0 else "DESACTIV"),
                                A_BOLD | color_pair(3 if u0 >> 3 & 1 == 0 else 4))
        ventana_banderas.addstr(5, 1, "{0:s}\t".format("ACTIVADO" if u0 >> 4 & 1 == 0 else "DESACTIV"),
                                A_BOLD | color_pair(3 if u0 >> 4 & 1 == 0 else 4))
        ventana_banderas.addstr("{0:s}\t".format("ACTIVADO" if u0 >> 5 & 1 == 0 else "DESACTIV"),
                                A_BOLD | color_pair(3 if u0 >> 5 & 1 == 0 else 4))
        ventana_banderas.addstr("{0:s}\t".format("ACTIVADO" if u0 >> 6 & 1 == 1 else "DESACTIV"),
                                A_BOLD | color_pair(3 if u0 >> 6 & 1 == 1 else 4))
        ventana_banderas.addstr("{0:s}".format("ACTIVADO" if u0 >> 7 & 1 == 1 else "DESACTIV"),
                                A_BOLD | color_pair(3 if u0 >> 7 & 1 == 1 else 4))
        ventana_banderas.addstr(8, 1, "{0:s}\t".format("ACTIVADO" if u1 >> 0 & 1 == 1 else "DESACTIV"),
                                A_BOLD | color_pair(3 if u1 >> 0 & 1 == 1 else 4))
        ventana_banderas.addstr("{0:s}\t".format("ACTIVADO" if u1 >> 1 & 1 == 1 else "DESACTIV"),
                                A_BOLD | color_pair(3 if u1 >> 1 & 1 == 1 else 4))
        ventana_banderas.addstr("{0:s}\t".format("ACTIVADO" if u1 >> 2 & 1 == 1 else "DESACTIV"),
                                A_BOLD | color_pair(3 if u1 >> 2 & 1 == 1 else 4))
        ventana_banderas.addstr("{0:s}".format("ACTIVADO" if u1 >> 3 & 1 == 0 else "DESACTIV"),
                                A_BOLD | color_pair(3 if u1 >> 3 & 1 == 0 else 4))
        ventana_banderas.addstr(10, 1, "{0:s}\t".format("ACTIVADO" if u1 >> 4 & 1 == 0 else "DESACTIV"),
                                A_BOLD | color_pair(3 if u1 >> 4 & 1 == 0 else 4))
        ventana_banderas.addstr("{0:s}\t".format("ACTIVADO" if u1 >> 5 & 1 == 0 else "DESACTIV"),
                                A_BOLD | color_pair(3 if u1 >> 5 & 1 == 0 else 4))
        ventana_banderas.addstr("{0:s}\t".format("ACTIVADO" if u1 >> 6 & 1 == 0 else "DESACTIV"),
                                A_BOLD | color_pair(3 if u1 >> 6 & 1 == 0 else 4))
        ventana_banderas.addstr("{0:s}".format("ACTIVADO" if u1 >> 7 & 1 == 1 else "DESACTIV"),
                                A_BOLD | color_pair(3 if u1 >> 7 & 1 == 1 else 4))
        ventana_banderas.addstr(11, 1, "CERO: {0:d},\tACARREO: {1:d},\tFASE: {2:d},\tRESET: {3:d}"
                                .format(cero, acarreo, fase, reset), A_BOLD)

        ventana_entrada.addstr((str(chr(cmd)) if cmd > 0 else "INV") + "|", A_BOLD | color_pair(2))

    key = KEY_RESIZE
    datosio = deque([])
    datosio.extend(abrir_puerto(puerto, baud, str(modo)))
    tmpio = datosio.popleft()
    datosio.appendleft(tmpio)
    cmd, comando, datos, pc, ejec, u0, u1, cero, acarreo, \
    fase, reset, boton, progb, accum, salida = decodificar_datos(tmpio)
    while key != ord('q'):
        if key != -1 or len(datosio) > 0:
            if key == KEY_RESIZE:
                y_principal, x_principal = pantalla.getmaxyx()
                # Configura los mínimos absolutos y calcula la ventana principal
                x_principal = min_x if min_x > x_principal else x_principal
                y_principal = min_y if min_y > y_principal else y_principal
                ventana_principal.resize(y_principal, x_principal)
                ventana_principal.clear()
                ventana_principal.box()
                ventana_principal.addstr(0, 1, "Depurador de la CPU Nibbler ({0:s})".format(
                    "MODO PROGRAMA" if modo == 0 else "MODO INSTRUCCIÓN"),
                                         A_BOLD | color_pair(1))

                # Calcula las dimensiones de las ventanas internas
                y_principal, x_principal = ventana_principal.getmaxyx()
                y_principal -= 2
                x_principal -= 2
                x_pc = int(floor(x_principal / 3))  # Ocupa 1/3 de la ventana en X
                y_pc = int(floor(y_principal / 4))  # Ocupa 1/4 de la ventana en Y
                x_data = int(floor(x_principal / 3))  # Ocupa 1/3 de la ventana en X
                y_data = int(floor(y_principal / 4))  # Ocupa 1/4 de la ventana en Y
                x_comando = int(floor(x_principal / 3))  # Ocupa 1/3 de la ventana en X
                y_comando = int(floor(y_principal / 2))  # Ocupa 1/2 de la ventana en Y
                x_disasm = int(floor(x_principal / 3))  # Ocupa 1/3 de la ventana en X
                y_disasm = int(floor(y_principal / 2))  # Ocupa 1/2 de la ventana en Y
                x_banderas = int(floor(x_principal * 2 / 3))  # Ocupa 2/3 de la ventana en X
                y_banderas = int(floor(y_principal / 2))  # Ocupa 1/2 de la ventana en Y
                x_entrada = int(floor(x_principal * 2 / 3))  # Ocupa 2/3 de la ventana en X
                y_entrada = int(floor(y_principal / 4))  # Ocupa 1/4 de la ventana en Y

                ventana_pc.resize(y_pc, x_pc)
                ventana_pc.clear()
                ventana_pc.box()
                ventana_pc.addstr(0, 1, "PC, INST/OPRND y PROGBYTE", A_BOLD | color_pair(2))

                ventana_datos.resize(y_data, x_data)
                ventana_datos.mvwin(1, x_pc + 1)
                ventana_datos.clear()
                ventana_datos.box()
                ventana_datos.addstr(0, 1, "BUS DE DATOS", A_BOLD | color_pair(2))

                marco_comandos.resize(y_comando, x_comando)
                marco_comandos.mvwin(1, x_pc + x_data + 1)
                marco_comandos.box()
                marco_comandos.addstr(0, 1, "REGISTRO DE COMANDOS", A_BOLD | color_pair(2))
                ventana_comandos.resize(y_comando - 2, x_comando - 2)
                ventana_comandos.mvwin(2, x_pc + x_data + 2)

                marco_disasm.resize(y_disasm, x_disasm)
                marco_disasm.mvwin(y_comando + 1, x_pc + x_data + 1)
                marco_disasm.box()
                marco_disasm.addstr(0, 1, "DESENSAMBLADOR", A_BOLD | color_pair(2))

                ventana_disasm.resize(y_disasm - 2, x_disasm - 2)
                ventana_disasm.mvwin(y_comando + 2, x_pc + x_data + 2)

                ventana_banderas.resize(y_banderas, x_banderas)
                ventana_banderas.mvwin(y_pc + 1, 1)
                ventana_banderas.clear()
                ventana_banderas.box()
                ventana_banderas.addstr(0, 1, "BANDERAS", A_BOLD | color_pair(2))
                ventana_banderas.addstr(1, 1, "MICROROM0", A_BOLD)
                ventana_banderas.addstr(2, 1, "nLOADOUT\tnOEPERAND\tnOEIN\t\tnOEALU")
                ventana_banderas.addstr(4, 1, "nWERAM\t\tnCSPRAM\t\tS0ALU\t\tS1ALU")
                ventana_banderas.addstr(6, 1, "MICROROM1", A_BOLD)
                ventana_banderas.addstr(7, 1, "S2ALU\t\tS3ALU\t\tMALU\t\tnCARRYIN")
                ventana_banderas.addstr(9, 1, "nLDFLAGS\tnLOADA\t\tnLOADPC\t\tINCPC")

                marco_entrada.resize(y_entrada, x_entrada)
                marco_entrada.mvwin(y_banderas + y_pc + 1, 1)
                marco_entrada.box()
                marco_entrada.addstr(0, 1, "ENTRADA DE COMANDOS", A_BOLD | color_pair(2))
                ventana_entrada.resize(y_entrada - 2, x_entrada - 2)
                ventana_entrada.mvwin(y_banderas + y_pc + 2, 2)

            if len(datosio) > 0 or key == KEY_RESIZE:
                for i in range(len(datosio)):
                    cmd, comando, datos, pc, ejec, u0, u1, \
                    cero, acarreo, fase, reset, boton, progb, accum, salida = decodificar_datos(datosio.popleft())
                rewrite()
            if key == KEY_RESIZE:
                rewrite()

            try:
                pantalla.addstr(y_principal + 1, 1, "> ")
                pantalla.refresh()
                ventana_principal.refresh()
                ventana_pc.refresh()
                ventana_datos.refresh()
                marco_comandos.refresh()
                ventana_comandos.refresh()
                marco_disasm.refresh()
                ventana_disasm.refresh()
                ventana_banderas.refresh()
                marco_entrada.refresh()
                ventana_entrada.refresh()
                pantalla.refresh()
            except:
                continue

        echo(True)

        key = pantalla.getch()

        # Teclas que se envían automáticamente
        if key == ord('r') or key == ord('R'):
            datosio.extend(escribir_puerto('R'))
            key = -1
        elif key == ord('o') or key == ord('O'):
            datosio.extend(escribir_puerto('O'))
            key = -1
        elif key == ord('c') or key == ord('C'):
            datosio.extend(escribir_puerto('C'))
            key = -1
        elif key == ord('p') or key == ord('P'):
            datosio.extend(escribir_puerto('P'))
            key = -1
        elif key == ord('b') or key == ord('B'):
            char1 = chr(pantalla.getch())
            char2 = chr(pantalla.getch())
            val = int(char1 + char2)
            datosio.extend(escribir_puerto("B " + str(val)))
            key = -1
        elif (key == ord('i') or key == ord('I')) and modo == 1:
            instr = pantalla.getstr(0, 0, 15)
            asmed, larga = ensamblar(instr)
            datosio.extend(escribir_puerto("I " + str(asmed) + " " + str(larga)))
            key = -1


args = sys.argv
try:
    puerto = args[1]
    baud = int(args[2])
    modo = int(args[3])
except IndexError:
    raise IndexError("Se requieren los siguientes argumentos en el siguiente orden:"
                     "\n\t1. El puerto serial"
                     "\n\t2. La tasa de baudios"
                     "\n\t3. Modo de operación")

wrapper(interface)
