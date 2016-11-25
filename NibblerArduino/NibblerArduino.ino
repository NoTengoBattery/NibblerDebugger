/**
    Depurador para la CPU Nibbler. Este programa funciona como código del depurador, en este caso un Arduino Mega 2560.
    Este programa es el código goma que se encarga de leer y escribir desde y hacia la CPU Nibbler. Su único fin es
    obtener la información de la CPU con los pines físicos del Arduino.

    El verdadero depurador es un escript de Pitón, que corre en UNIX (como macOS y Linux).

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

#include "NibblerArduino.h"

int sel = 0;

/*
    Configura Arduino para incializar la CPU Nibbler. En primer lugar, configura todos los puertos para entradas. Esto
    es porque la CPU Nibbler no está diseñada para ser depurada físicamente y la mayoría de datos de la CPU solamente
    se pueden leer directamente desde Arduino. Si se progama como salida, podría ocurrir contención en el pin de
    Arduino.
*/
void setup() {
  // Inicializa la conexión serial
  Serial.begin(BAUDRATE);
  while (!Serial) {
  }
  // Inicializa todos los puertos como entrada
  DDRA = 0x00;
  DDRB = 0x00;
  DDRC = 0x00;
  DDRD = 0x00;
  DDRE = 0x00;
  DDRF = 0x00;
  DDRG = 0x00;
  DDRH = 0x00;
  DDRJ = 0x00;
  DDRK = 0x00;
  DDRL = 0x00;
  // Incializa las salidas
  pinMode(RELOJ, SALIDA);
  digitalWrite(RELOJ, BAJO);
  // Inicializa la CPU en reset
  pinMode(nRESET, SALIDA);
  digitalWrite(nRESET, nALTO);
  // Inicializa los 4 botones como salidas y los pone como "no presionado"
  pinMode(nBOTON0, SALIDA);
  digitalWrite(nBOTON0, nBAJO);
  pinMode(nBOTON1, SALIDA);
  digitalWrite(nBOTON1, nBAJO);
  pinMode(nBOTON2, SALIDA);
  digitalWrite(nBOTON2, nBAJO);
  pinMode(nBOTON3, SALIDA);
  digitalWrite(nBOTON3, nBAJO);
  digitalWrite(RELOJ, BAJO);
  digitalWrite(RELOJ, ALTO);
  // Cuando el puerto está listo, avisar
  Serial.write(64);
  // Intenta detectar el modo de operación
  bool valido = false;
  while (!valido) {
    if (Serial.available() > 0) {
      sel = Serial.read();
    }
    switch (sel) {
      case '0':
        Serial.println("0p0");
        valido = true;
        break;
      case '1':
        Serial.println("0p1");
        valido = true;
        break;
    }
  }
  // Si ya inicializó, resetear la CPU
  resetCPU();
}

/*
  En este loop se selecciona la función que ejecutará el programa. El progama cuenta con dos modos:
  1. el modo de depuración de progama y
  2. el modo de depuración de instrucción
  El primer modo requiere que la memoria del programa esté conectada y tenga un programa válido para la CPU Nibbler.
  En el segundo modo se requiere que la memoria del programa esté completamente desconectada, pues Arduino configurará
  los pines como salidas. Esto podría significar contention si la memoria del programa está conectada.
*/
void loop() {
  switch (sel) {
    case '0':
      // Cuando la selección es 0, utilizar
      depurarPrograma();
      break;
    case '1' :
      // Cambia los pines de la memoria del programa a salidas
      pinMode(PROG0, SALIDA);
      pinMode(PROG1, SALIDA);
      pinMode(PROG2, SALIDA);
      pinMode(PROG3, SALIDA);
      pinMode(PROG4, SALIDA);
      pinMode(PROG5, SALIDA);
      pinMode(PROG6, SALIDA);
      pinMode(PROG7, SALIDA);
      depurarInstruccion();
      break;
  }
}

/*
  Este está diseñado para depurar la CPU con la ROM del programa conectada.

  Comandos:
    O: Obtener estado actuar
    R: Aplicar la rutina RESET
    B DEC: Cambia el valor de los botones a los primeros 4 bits LSB del número decimal DEC
    C: Envía un pulso de reloj a la CPU
    P: Envía un pulso de propagación a la CPU
*/
void depurarPrograma() {
  int comando = 0;
  if (Serial.available() > 0) {
    // read the incoming byte:
    comando = Serial.read();
  }
  switch (comando) {
    case 'O' :
      enviarEstado('o');
      break;
    case 'R' :
      resetCPU();
      break;
    case 'B' :
      escribirBOTON(Serial.parseInt());
      break;
    case 'C' :
      pulso();
      break;
    case 'P' :
      propagar();
      break;
    case '0':
      Serial.println("0p0");
      break;
  }
}

/*
  Este está diseñado para depurar la CPU con la ROM del programa conectada.

  Comandos:
    O: Obtener estado actuar
    R: Aplicar la rutina RESET
    B DEC: Cambia el valor de los botones a los primeros 4 bits LSB del número decimal DEC
    C: Envía un pulso de reloj a la CPU
    P: Envía un pulso de propagación a la CPU
    I (PROG[0] | PROG[1]) (ESLARGA): envía una instrucción PROG con los bytes en MSB y 1 si la instrucción es larga
*/
void depurarInstruccion() {
  int comando = 0;
  if (Serial.available() > 0) {
    comando = Serial.read();
  }
  switch (comando) {
    case 'O' :
      enviarEstado('o');
      break;
    case 'R' :
      resetCPU();
      escribirPROGBYTE(0,  0);
      break;
    case 'B' :
      escribirBOTON(Serial.parseInt());
      break;
    case 'C' :
      pulso();
      break;
    case 'P' :
      propagar();
      break;
    case 'I' :
      escribirPROGBYTE(Serial.parseInt(),  Serial.parseInt());
      break;
    case '1':
      Serial.println("0p1");
      break;
  }
}

void enviarEstado(char t) {
  // Envía el valor leído desde el puerto:
  //[PROGBYTE, BOTON, RPCZ, FLAGS1, FLAGS0, FETCH, PC[1], PC[0], DATOS]
  char data[14];
  uint16_t PC = leerPC();
  char spr =  0;
  data[0] = '\n';
  data[1] = '\r';
  data[2] = t;
  data[3] = leerDATOS();
  data[4] = uint8_t(PC & 0xFF);
  data[5] = uint8_t(PC >> 8 & 0xFF);
  data[6] = leerOPERANDO_INSTRUCCION();
  data[7] = leerFLAGS0();
  data[8] = leerFLAGS1();
  data[9] = (leerZERO() <<  0 | leerCARRY() <<  1 |  leerPHASE() << 2 |  leerRESET()) & 0xF;
  data[10] = leerBOTON();
  data[11] = leerPROG();
  data[12] = leerACC();
  data[13] = leerOUT();
  Serial.write(data, sizeof(data));
  Serial.flush();
}

void pulso() {
  enviarEstado('C');
  digitalWrite(RELOJ, BAJO);
  digitalWrite(RELOJ, ALTO);
  enviarEstado('c');

}

void propagar() {
  // Cuando PHASE sea 0, sabemos que es la etapa FETCH
  enviarEstado('P');
  if (!leerPHASE()) {
    digitalWrite(RELOJ, BAJO);
    digitalWrite(RELOJ, ALTO);
    enviarEstado('a');
  }
  while (leerPHASE()) {
    digitalWrite(RELOJ, BAJO);
    digitalWrite(RELOJ, ALTO);
    enviarEstado('n');
  }
  enviarEstado('p');
}

uint16_t leerPC() {
  // Una variable de 16 bits
  uint16_t PC = 0;
  // Shift lógico para cada valor del PC
  PC |= (digitalRead(PC0)) << 0;
  PC |= (digitalRead(PC1)) << 1;
  PC |= (digitalRead(PC2)) << 2;
  PC |= (digitalRead(PC3)) << 3;
  PC |= (digitalRead(PC4)) << 4;
  PC |= (digitalRead(PC5)) << 5;
  PC |= (digitalRead(PC6)) << 6;
  PC |= (digitalRead(PC7)) << 7;
  PC |= (digitalRead(PC8)) << 8;
  PC |= (digitalRead(PC9)) << 9;
  PC |= (digitalRead(PC10)) << 10;
  PC |= (digitalRead(PC11)) << 11;
  PC &= 0xFFF;
  return PC;
}

uint8_t leerDATOS() {
  // Una variable de 8 bits
  uint8_t DATOS = 0;
  // Shift lógico para cada valor del BUS DATOS
  DATOS |= (digitalRead(DATA0)) << 0;
  DATOS |= (digitalRead(DATA1)) << 1;
  DATOS |= (digitalRead(DATA2)) << 2;
  DATOS |= (digitalRead(DATA3)) << 3;
  DATOS &= 0xF;
  return DATOS;
}

uint8_t leerOPERANDO_INSTRUCCION() {
  // Una variable de 8 bits
  uint8_t OPRND_INSTR = 0;
  // Shift lógico para cada valor del OPERANDO/INSTRUCCION
  OPRND_INSTR |= (digitalRead(OPRND0)) << 0;
  OPRND_INSTR |= (digitalRead(OPRND1)) << 1;
  OPRND_INSTR |= (digitalRead(OPRND2)) << 2;
  OPRND_INSTR |= (digitalRead(OPRND3)) << 3;
  OPRND_INSTR |= (digitalRead(INSTR0)) << 4;
  OPRND_INSTR |= (digitalRead(INSTR1)) << 5;
  OPRND_INSTR |= (digitalRead(INSTR2)) << 6;
  OPRND_INSTR |= (digitalRead(INSTR3)) << 7;
  return OPRND_INSTR;
}

uint8_t leerPROG() {
  // Una variable de 8 bits
  uint8_t PROGRAMA = 0;
  // Shift lógico para cada valor del PROGBYTE
  PROGRAMA |= (digitalRead(PROG0)) << 0;
  PROGRAMA |= (digitalRead(PROG1)) << 1;
  PROGRAMA |= (digitalRead(PROG2)) << 2;
  PROGRAMA |= (digitalRead(PROG3)) << 3;
  PROGRAMA |= (digitalRead(PROG4)) << 4;
  PROGRAMA |= (digitalRead(PROG5)) << 5;
  PROGRAMA |= (digitalRead(PROG6)) << 6;
  PROGRAMA |= (digitalRead(PROG7)) << 7;
  return PROGRAMA;
}

bool leerZERO() {
  return digitalRead(nZERO) ==  LOW ;
}

bool leerCARRY() {
  return digitalRead(nCARRY) ==  LOW;
}

bool leerPHASE() {
  return digitalRead(PHASE) ==  HIGH;
}

bool leerRESET() {
  return digitalRead(nRESET) ==  LOW;
}

uint8_t leerFLAGS0() {
  // Una variable de 8 bits
  uint8_t FLAGSCERO = 0;
  // Shift lógico para cada valor del FLAGS0
  FLAGSCERO |= (digitalRead(MICRO0_0)) << 0;
  FLAGSCERO |= (digitalRead(MICRO0_1)) << 1;
  FLAGSCERO |= (digitalRead(MICRO0_2)) << 2;
  FLAGSCERO |= (digitalRead(MICRO0_3)) << 3;
  FLAGSCERO |= (digitalRead(MICRO0_4)) << 4;
  FLAGSCERO |= (digitalRead(MICRO0_5)) << 5;
  FLAGSCERO |= (digitalRead(MICRO0_6)) << 6;
  FLAGSCERO |= (digitalRead(MICRO0_7)) << 7;
  return FLAGSCERO;
}

uint8_t leerFLAGS1() {
  // Una variable de 8 bits
  uint8_t FLAGSUNO = 0;
  // Shift lógico para cada valor del FLAGS0
  FLAGSUNO |= (digitalRead(MICRO1_0)) << 0;
  FLAGSUNO |= (digitalRead(MICRO1_1)) << 1;
  FLAGSUNO |= (digitalRead(MICRO1_2)) << 2;
  FLAGSUNO |= (digitalRead(MICRO1_3)) << 3;
  FLAGSUNO |= (digitalRead(MICRO1_4)) << 4;
  FLAGSUNO |= (digitalRead(MICRO1_5)) << 5;
  FLAGSUNO |= (digitalRead(MICRO1_6)) << 6;
  FLAGSUNO |= (digitalRead(MICRO1_7)) << 7;
  return FLAGSUNO;
}

uint8_t leerBOTON() {
  // Una variable de 8 bits
  uint8_t BOTON = 0;
  // Shift lógico para cada valor de los botones
  BOTON |= (!(digitalRead(nBOTON0))) << 0;
  BOTON |= (!(digitalRead(nBOTON1))) << 1;
  BOTON |= (!(digitalRead(nBOTON2))) << 2;
  BOTON |= (!(digitalRead(nBOTON3))) << 3;
  BOTON &= 0xF;
  return BOTON;
}

uint8_t leerACC() {
  // Una variable de 8 bits
  uint8_t ACC = 0;
  // Shift lógico para cada valor de los botones
  ACC |= ((digitalRead(ACC0))) << 0;
  ACC |= ((digitalRead(ACC1))) << 1;
  ACC |= ((digitalRead(ACC2))) << 2;
  ACC |= ((digitalRead(ACC3))) << 3;
  ACC &= 0xF;
  return ACC;
}

uint8_t leerOUT() {
  // Una variable de 8 bits
  uint8_t OUT = 0;
  // Shift lógico para cada valor de los botones
  OUT |= ((digitalRead(OUT0))) << 0;
  OUT |= ((digitalRead(OUT1))) << 1;
  OUT |= ((digitalRead(OUT2))) << 2;
  OUT |= ((digitalRead(OUT3))) << 3;
  OUT &= 0xF;
  return OUT;
}

void escribirBOTON(uint8_t boton) {
  enviarEstado('B');
  // Shift lógico para cada valor de los botones
  // Esta línea la programaré cual ingeniero de Samsung
  digitalWrite(nBOTON0, (boton >> 0) & 1 == ALTO ? nALTO : nBAJO);
  digitalWrite(nBOTON1, (boton >> 1) & 1 == ALTO ? nALTO : nBAJO);
  digitalWrite(nBOTON2, (boton >> 2) & 1 == ALTO ? nALTO : nBAJO);
  digitalWrite(nBOTON3, (boton >> 3) & 1 == ALTO ? nALTO : nBAJO);
  enviarEstado('b');
}

void resetCPU() {
  // Inicializa la CPU en reset
  digitalWrite(nRESET, nALTO);
  enviarEstado('R');
  // Lanza los primeros 2 pulsos para propagar el reset
  propagar();
  escribirBOTON(0);
  digitalWrite(nRESET, nBAJO);
  enviarEstado('r');
}

void escribirPROGBYTE(int larga,  uint16_t progb) {
  enviarEstado('I');
  propagar();
  // Shift lógico para cada valor de los botones
  // Esta línea la programaré cual ingeniero de Samsung
  digitalWrite(PROG0, (progb >> 0) & ALTO);
  digitalWrite(PROG1, (progb >> 1) & ALTO);
  digitalWrite(PROG2, (progb >> 2) & ALTO);
  digitalWrite(PROG3, (progb >> 3) & ALTO);
  digitalWrite(PROG4, (progb >> 4) & ALTO);
  digitalWrite(PROG5, (progb >> 5) & ALTO);
  digitalWrite(PROG6, (progb >> 6) & ALTO);
  digitalWrite(PROG7, (progb >> 7) & ALTO);
  if (larga > 0) {
    pulso();
    digitalWrite(PROG0, (progb >> 8) & ALTO);
    digitalWrite(PROG1, (progb >> 9) & ALTO);
    digitalWrite(PROG2, (progb >> 10) & ALTO);
    digitalWrite(PROG3, (progb >> 11) & ALTO);
    digitalWrite(PROG4, (progb >> 12) & ALTO);
    digitalWrite(PROG5, (progb >> 13) & ALTO);
    digitalWrite(PROG6, (progb >> 14) & ALTO);
    digitalWrite(PROG7, (progb >> 15) & ALTO);
  }
  propagar();
  enviarEstado('i');
}
