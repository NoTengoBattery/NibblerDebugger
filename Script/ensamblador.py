#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
Un ensamblador simple para la CPU Nibbler
"""


def ensamblar(instr):  # type: (str) -> (int, int)
    """
    Ensambla una instrucción para la CPU Nibbler.
    ADVERTENCIA:
        En las instrucciones largas, el ensablador cambia el orden de los bytes de MSBF a LSBF, esto es para
        simplificar el código de Arduino, por ejemplo, la instrucción `LD 0xABC` debería ensamblarse como 0x6ABC,
        sin embargo, este ensamblador la ensamblará como 0xBC6A.
    :param instr: la instrucción en texto a ensamblar
    :return: el valor numérico de la instrucción ensamblada
    """
    instr_dicc = {
        "JC": (0, 1, 1, 0),
        "JNC": (1, 1, 1, 0),
        "COMPI": (2, 0, 0, 0),
        "COMPM": (3, 1, 0, 0),
        "LIT": (4, 0, 0, 0),
        "IN": (5, 0, 0, 0),
        "LD": (6, 1, 0, 0),
        "ST": (7, 1, 0, 0),
        "JZ": (8, 1, 0, 1),
        "JNZ": (9, 1, 0, 1),
        "ADDI": (10, 0, 0, 0),
        "ADDM": (11, 1, 0, 0),
        "JMP": (12, 1, 0, 0),
        "OUT": (13, 0, 0, 0),
        "NORI": (14, 0, 0, 0),
        "NORM": (15, 1, 0, 0)
    }
    comando = instr.strip().split()
    if len(comando) != 2:
        raise ValueError("La instrucción que se ingresó no parece ser una instrucción con sintaxis correcta.", instr)
    instruccion = comando[0].upper()
    operando = int(comando[1], 0)
    if instruccion in instr_dicc:
        instr_bin, usa_dir, usa_carry, usa_cero = instr_dicc[instruccion]
        if usa_dir:
            return (instr_bin << 4 | (operando >> 8 & 0xF) | ((operando << 8) & 0xFF00)), usa_dir
        else:
            return ((instr_bin << 4 | (operando & 0xF)) & 0xFF), usa_dir
    else:
        raise ValueError("La instrucción {0:s} no existe en el diccionario de instrucciones válidas.", instruccion)
