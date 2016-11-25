#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import array


def decodificar_datos(arr):  # type: (array) -> (int, int, int, int, int, bool, bool, bool, bool, int, int, int, int)
    """
    Separa y decodifica todos los datos obtenidos por Arduino
    :return: comando, datos, pc, ejec, u0, u1, cero, acarreo, fase, reset, boton, progb, acc, out
    :param arr: array a decodificar
    """
    # El primer byte es el comando
    comando = arr[0]  # type: int
    # El segundo byte es el bus de datos
    datos = arr[1]  # type: int
    # El tercer byte es el primer byte de PC y el cuarto es el segundo byte de PC
    pc = arr[2] | arr[3] << 8  # type: int
    # El quinto byte es la instruccion en ejecución
    ejec = arr[4]  # type: int
    # El sexto byte son las banderas de la MICRO0
    u0 = arr[5]  # type: int
    # El séptimo byte son las banderas de la MICROq
    u1 = arr[6]  # type: int
    # El octavo byte cotiene carry, zero, phase y reset
    cero = arr[7] >> 0 & 1 == 1  # type: bool
    acarreo = arr[7] >> 1 & 1 == 1  # type: bool
    fase = arr[7] >> 2 & 1 == 1  # type: bool
    reset = arr[7] >> 3 & 1 == 1  # type: bool
    # El noveno byte contiene el estado actual de los botones
    boton = arr[8]  # type: int
    # por último, el décimo byte contiene el PROGRAMBYTE
    progb = arr[9]  # type: int
    # leer ACUMULADOR
    acc = arr[10]  # type: int
    # leer OUT
    out = arr[11]  # type: int

    # Determina el comando en palabras
    if comando == ord('o'):
        comando = "OBTENER"
    elif comando == ord('C'):
        comando = "PULSO"
    elif comando == ord('c'):
        comando = "pulso"
    elif comando == ord('P'):
        comando = "PROPAGAR"
    elif comando == ord('p'):
        comando = "propagar"
    elif comando == ord('a'):
        comando = "AJUSTE_FASE"
    elif comando == ord('n'):
        comando = "AJUSTE_EJEC"
    elif comando == ord('B'):
        comando = "BOTON " + str(boton)
    elif comando == ord('b'):
        comando = "boton"
    elif comando == ord('R'):
        comando = "RESET"
    elif comando == ord('r'):
        comando = "reset"
    elif comando == ord('I'):
        comando = "INSTRUCCION"
    elif comando == ord('i'):
        comando = "instruccion " + disasm(pc, ejec, progb, fase, acarreo, cero)
    else:
        comando = "Comando desconocido!"
    return arr[0], comando, datos, pc, ejec, u0, u1, cero, acarreo, fase, reset, boton, progb, acc, out


# JC: DIR
# JNC: DIR
# COMPI: INM
# COMPM: DIR
# LIT: INM
# IN: NA
# LD: DIR
# ST: DIR
# JZ: DIR
# JNZ: DIR
# ADDI: INM
# ADDM: DIR
# JMP: DIR
# OUT: NA
# NORI: INM
# NORM: DIR

def disasm(addr, fetch, progb, fase, carry, cero):
    """
    Desensamblador rápido para el juego de instrucciones de la CPU Nibbler. Este desensamblador requiere conocer:
        1. La dirección (PC) actual
        2. El byte que está almacenado en el fetch
        3. El byte del programa
        4. La fase
        5. El estado de acarreo
        6. El estado de cero
    :param addr: La dirección (PC) actual
    :param fetch: El byte que está almacenado en el fetch
    :param progb: El byte del programa
    :param fase: La fase
    :param carry: El estado de acarreo
    :param cero: El estado de cero
    :return:
    """

    # Si la fase es 0, retornar
    if fase != 0:
        return ""
    # Diccionario con las instrucciones
    # ("INSTR", INMD, CARRY, CERO)
    instr_dicc = {
        0: ("JC", 1, 1, 0),
        1: ("JNC", 1, 1, 0),
        2: ("COMPI", 0, 0, 0),
        3: ("COMPM", 1, 0, 0),
        4: ("LIT", 0, 0, 0),
        5: ("IN", 0, 0, 0),
        6: ("LD", 1, 0, 0),
        7: ("ST", 1, 0, 0),
        8: ("JZ", 1, 0, 1),
        9: ("JNZ", 1, 0, 1),
        10: ("ADDI", 0, 0, 0),
        11: ("ADDM", 1, 0, 0),
        12: ("JMP", 1, 0, 0),
        13: ("OUT", 0, 0, 0),
        14: ("NORI", 0, 0, 0),
        15: ("NORM", 1, 0, 0)
    }
    # Extraer la instrucción desde Fetch
    instr_bin, opernd = (fetch >> 4, fetch & 0xF)
    # Obtener la instruccion desde el dicc.
    instr_asm, usa_dir, usa_carry, usa_cero = instr_dicc[instr_bin]
    retorno = "0x{0:04X}:\t{1:s}\t".format(addr, instr_asm)
    if usa_dir == 0:
        retorno += "0x{0:01X}\t".format(opernd)
    elif usa_dir == 1:
        retorno += "0x{0:04X}\t".format(opernd << 8 | progb)
    if usa_carry == 1:
        retorno += "[C: {0:s}]".format("Sí" if carry else "No")
    if usa_cero:
        retorno += "[Z: {0:s}]".format("Sí" if carry else "No")
    retorno += '\n'
    return retorno
