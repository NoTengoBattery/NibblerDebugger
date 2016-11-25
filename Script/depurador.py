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
from time import sleep

from ensamblador import ensamblar
from ensamblador_reverso import decodificar_datos, disasm
from receptor import *

min_x = 90
min_y = 28

l_cmd_enviado = ""
l_disasm_enviado = ""


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
        init_pair(4, COLOR_BLUE, COLOR_WHITE)

    pantalla.border(0)
    pantalla.nodelay(1)

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

    def val3opb(no, cmpr, val_si, val_no, bits):
        ret = []
        for i in range(bits):
            ret.append(val_si if (no >> i & 1) == cmpr else val_no)
        return ret

    def rewrite():
        global l_cmd_enviado
        global l_disasm_enviado
        """
        Actualiza la información que se presenta en la pantalla.
        """
        ventana_pc.addstr(1, 1, "PC: 0x{0:04X}, {0:02d}".format(pc))
        ventana_pc.addstr(2, 1, "FETCHD: I[0x{0:01X}] O[0x{1:01X}], 0x{2:02X}".format(ejec >> 4, ejec & 0xF, ejec))
        ventana_pc.addstr(3, 1, "PROGBYTE: I[0x{0:01X}] O[0x{1:01X}], 0x{2:02X}".format(progb >> 4, progb & 0xF, progb))
        ventana_pc.addstr(4, 1, "FASE: {0:s}".format(val3op(fase, "EJECUTANDO", "OBTENIENDO")))

        ventana_datos.addstr(1, 1, "DATOS: 0x{0:02X}".format(datos))
        ventana_datos.addstr(2, 1, "BOTONES: 0x{0:02X}".format(boton))
        ventana_datos.addstr(3, 1, "| LEFT|RIGHT| DOWN|  UP |", A_BOLD | color_pair(3))
        botones_str = val3opb(boton, 0, "_=_", "___", 4)
        ventana_datos.addstr(4, 1, "| {0:s} | {1:s} | {2:s} | {3:s} |".
                             format(botones_str[0],
                                    botones_str[1],
                                    botones_str[2],
                                    botones_str[3]),
                             A_BOLD | color_pair(4))
        ventana_datos.addstr(5, 1, "ACCUMULADOR: 0x{0:02X}, {0:02d}".format(accum))
        ventana_datos.addstr(6, 1, "SALIDA: 0x{0:02X}".format(salida))

        ventana_comandos.addstr(comando + "\n")
        if disasm_enviado != l_disasm_enviado:
            ventana_disasm.addstr(disasm_enviado)
            l_disasm_enviado = disasm_enviado

        micro0 = val3opb(u0, 0, "ACTIVADO", "DESACTIV", 8)
        nmicro0 = val3opb(u0, 0, "DESACTIV", "ACTIVADO", 8)
        ventana_banderas.addstr(3, 1, "{0:s}\t{1:s}\t{2:s}\t{3:s}".format(
            micro0[0],
            micro0[1],
            micro0[2],
            micro0[3]
        ), A_BOLD | color_pair(4))

        ventana_banderas.addstr(5, 1, "{0:s}\t{1:s}\t{2:s}\t{3:s}".format(
            micro0[4],
            micro0[5],
            nmicro0[6],
            nmicro0[7]
        ), A_BOLD | color_pair(4))

        micro1 = val3opb(u1, 0, "ACTIVADO", "DESACTIV", 8)
        nmicro1 = val3opb(u1, 0, "DESACTIV", "ACTIVADO", 8)

        ventana_banderas.addstr(8, 1, "{0:s}\t{1:s}\t{2:s}\t{3:s}".format(
            nmicro1[0],
            nmicro1[1],
            nmicro1[2],
            micro1[3]
        ), A_BOLD | color_pair(4))

        ventana_banderas.addstr(10, 1, "{0:s}\t{1:s}\t{2:s}\t{3:s}".format(
            micro1[4],
            micro1[5],
            micro1[6],
            nmicro1[7]
        ), A_BOLD | color_pair(4))
        ventana_banderas.addstr(11, 1, "CERO: {0:s},\tACARREO: {1:s},\tFASE: {2:s},\tRESET: {3:s}"
                                .format(val3op(cero, "Sí", "No"),
                                        val3op(acarreo, "Sí", "No"),
                                        val3op(fase, "Sí", "No"),
                                        val3op(reset, "Sí", "No")), A_BOLD)

        if cmd_enviado != l_cmd_enviado:
            ventana_entrada.addstr("{0:s}\n".format(cmd_enviado), A_BOLD)
            l_cmd_enviado = cmd_enviado

    key = KEY_RESIZE
    enviado_arduino = deque([])  # type: deque
    datosio = deque([])
    datosio.extend(abrir_puerto(puerto, baud, str(modo)))
    comando = datos = pc = ejec = u0 = u1 = cero = acarreo = fase = reset = boton = progb = accum = salida = 0
    cmd_enviado = "Inicializando..."
    disasm_enviado = ""
    while key != ord('q'):
        if key != -1 or len(datosio) > 0 or len(enviado_arduino) > 0:
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
                    for j in range(len(enviado_arduino)):
                        cmd_enviado = enviado_arduino.popleft()
                        disasm_enviado = disasm(pc, ejec, progb, fase, acarreo, cero)
                        rewrite()
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
        indata = leer_puerto()
        sleep(0.075)
        if indata:
            datosio.append(indata)

        # Teclas que se envían automáticamente
        if key == ord('r') or key == ord('R'):
            datosio.extend(escribir_puerto('R'))
            enviado_arduino.append("R")
            key = -1
        elif key == ord('o') or key == ord('O'):
            datosio.extend(escribir_puerto('O'))
            enviado_arduino.append("O")
            key = -1
        elif key == ord('c') or key == ord('C'):
            datosio.extend(escribir_puerto('C'))
            enviado_arduino.append("C")
            key = -1
        elif key == ord('p') or key == ord('P'):
            datosio.extend(escribir_puerto('P'))
            enviado_arduino.append("P")
            key = -1
        elif key == ord('b') or key == ord('B'):
            pantalla.nodelay(0)
            val = int(pantalla.getstr())
            pantalla.nodelay(1)
            datosio.extend(escribir_puerto("B " + str(val)))
            enviado_arduino.append("B " + str(val))
            key = -1
        elif (key == ord('i') or key == ord('I')) and modo == 1:
            pantalla.nodelay(0)
            instr = pantalla.getstr()
            pantalla.nodelay(1)
            try:
                asmed, larga = ensamblar(instr)
            except:
                ventana_entrada.addstr("Instrucción inválida", A_BOLD | color_pair(4))
            datosio.extend(escribir_puerto("I " + str(asmed) + " " + str(larga)))
            enviado_arduino.append("I " + str(asmed) + " " + str(larga))
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
