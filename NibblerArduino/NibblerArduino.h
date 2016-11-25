#ifndef NIBBLER_ARDUINO_H
#define NIBBLER_ARDUINO_H

/*
    Utilizando definiciones del preprocesador porque las variables consumen memoria del Arduino, aunque GCC debería
    optimizar las constantes conocidas. Como sea, esto agrega claridad sin sobresaturar el código y permite visualizar
    los pines de Arduino y su conexión de forma tabular conveniente

    Copyright (c) 2016 Oever González

    Se concede permiso, de forma gratuita, a cualquier persona que obtenga una copia de este software y de los archivos
    de documentación asociados (el "Software"), para utilizar el Software sin restricción, incluyendo sin limitación
    los derechos a usar, copiar, modificar, fusionar, publicar, distribuir, sublicenciar, y/o vender copias del
    Software, y a permitir a las personas a las que se les proporcione el Software a hacer lo mismo, sujeto a las
    siguientes condiciones:

    El aviso de copyright anterior y este aviso de permiso se incluirán en todas las copias o partes sustanciales del
    Software.

    EL SOFTWARE SE PROPORCIONA "TAL CUAL", SIN GARANTÍA DE NINGÚN TIPO, EXPRESA O IMPLÍCITA, INCLUYENDO PERO NO
    LIMITADO A GARANTÍAS DE COMERCIALIZACIÓN, IDONEIDAD PARA UN PROPÓSITO PARTICULAR Y NO INFRACCIÓN. EN NINGÚN CASO
    LOS AUTORES O TITULARES DEL COPYRIGHT SERÁN RESPONSABLES DE NINGUNA RECLAMACIÓN, DAÑOS U OTRAS RESPONSABILIDADES,
    YA SEA EN UNA ACCIÓN DE CONTRATO, AGRAVIO O CUALQUIER OTRO MOTIVO, QUE SURJA DE O EN CONEXIÓN CON EL SOFTWARE O EL
    USO U OTRO TIPO DE ACCIONES EN EL SOFTWARE.
*/

/*
 La tasa de transferencia hacia el puerto serial, 115200 es el baud rate estándar de la terminal serial del Kernel de
 Linux
 */
#define BAUDRATE 115200

// Determina la dirección del programa (PC), conéctese a los 3 contadores
#define PC0 24
#define PC1 25
#define PC2 2
#define PC3 3
#define PC4 4
#define PC5 5
#define PC6 6
#define PC7 7
#define PC8 8
#define PC9 9
#define PC10 10
#define PC11 11
// Determina el estado actual del bus de datos, conéctese directamente al bus de datos
#define DATA0 12
#define DATA1 44
#define DATA2 14
#define DATA3 15
// Determina el estado actual del bus de operando, conéctese a la salida del FETCH
#define OPRND0 16
#define OPRND1 17
#define OPRND2 18
#define OPRND3 19
// Determina el estado actual del bus de instrucción, conéctese a la salida del FETCH
#define INSTR0 20
#define INSTR1 21
#define INSTR2 22
#define INSTR3 23
// Se conecta a las banderas de la ROM de microcódigo 0
#define MICRO0_0 26 // nLOADOUT
#define MICRO0_1 27 // nOEOPERAND
#define MICRO0_2 28 // nOEIN
#define MICRO0_3 29 // nOEALU
#define MICRO0_4 30 // nWERAM
#define MICRO0_5 31 // nCSPRAM
#define MICRO0_6 32 // S0
#define MICRO0_7 33 // S1
// Se conecta a las banderas de la ROM de microcódigo 1
#define MICRO1_0 34 // S2
#define MICRO1_1 35 // S3
#define MICRO1_2 36 // M
#define MICRO1_3 37 // nCARRYIN
#define MICRO1_4 38 // nLOADFLAGS
#define MICRO1_5 39 // nLOADA
#define MICRO1_6 40 // nLOADPC
#define MICRO1_7 41 // INCPC
// Determinan el estado de /ZERO y /CARRY, conéctese a las salidas de FLAGS
#define nZERO 42
#define nCARRY 49
// Determina el estado de la fase, conéctese a la salida de PHASE-reset
#define PHASE 50
// Este pin se conecta a la entrada del botón de reset
#define nRESET 43
// Este pin se conecta a la señal de reloj del circuito
#define RELOJ 13
// Esta serie de pines van conectados a las entradas de los botones UP, DOWN, LEFT y RIGHT
#define nBOTON0 45
#define nBOTON1 46
#define nBOTON2 47
#define nBOTON3 48
// Se conectan a las salidas de la ROM del programa
#define PROG0 A0
#define PROG1 A1
#define PROG2 A2
#define PROG3 A3
#define PROG4 A4
#define PROG5 A5
#define PROG6 A6
#define PROG7 A7
// Se conectan a las salidas del acumulador
#define ACC0 A8
#define ACC1 A9
#define ACC2 A10
#define ACC3 A11
// Se conectan a las salidas del OUT
#define OUT0 A12
#define OUT1 A13
#define OUT2 A14
#define OUT3 A15

// Volver a definir
#define ALTO HIGH
#define BAJO LOW
#define nALTO LOW
#define nBAJO HIGH
#define ENTRADA INPUT
#define SALIDA OUTPUT

#endif
