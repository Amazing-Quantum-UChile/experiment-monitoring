#include <Adafruit_MAX31865.h>

// Pin configuration for Arduino Mega
// Hardware SPI: CS = 10, MOSI = 51, MISO = 50, SCK = 52
Adafruit_MAX31865 thermo = Adafruit_MAX31865(9);

// Reference resistor value (RREF)
// For PT100 boards (marked '431'), use 430.0 Ohms
// For PT1000 boards (marked '4301'), use 4300.0 Ohms
#define RREF      430.0

// Nominal resistance of your sensor at 0°C (PT100 = 100.0)
#define RNOMINAL  100.0

// CALIBRATION: Add or subtract degrees to match your reference sensor
float calibrationOffset = 0.0; 

void setup() {
  Serial.begin(9600); 
  Serial.println("Initializing MAX31865...");
  // Set to MAX31865_2WIRE, 3WIRE, or 4WIRE depending on your probe
  thermo.begin(MAX31865_3WIRE); 
}

void loop() {
  uint16_t rtd = thermo.readRTD();
  float ratio = rtd;
  ratio /= 32768;

  float resistance = RREF * ratio;
  Serial.print("Resistance = "); 
  Serial.print(resistance, 2);
  Serial.println(" Ohms");

  // Calculate temperature and apply the manual offset
  float temp = thermo.temperature(RNOMINAL, RREF) + calibrationOffset;
  
  Serial.print("Temperature = ");
  Serial.print(temp);
  Serial.println(" C");

  // Error Checking
  uint8_t fault = thermo.readFault();
  if (fault) {
    Serial.print("Fault detected: ");
    if (fault & MAX31865_FAULT_HIGHTHRESH) Serial.println("RTD High Threshold");
    if (fault & MAX31865_FAULT_LOWTHRESH)  Serial.println("RTD Low Threshold");
    if (fault & MAX31865_FAULT_REFINLOW)   Serial.println("REFIN- > 0.85 x VBIAS");
    if (fault & MAX31865_FAULT_REFINHIGH)  Serial.println("REFIN- < 0.85 x VBIAS (FORCE- open)");
    if (fault & MAX31865_FAULT_RTDINLOW)   Serial.println("RTDIN- < 0.85 x VBIAS (FORCE- open)");
    if (fault & MAX31865_FAULT_OVUV)       Serial.println("Under/Over voltage");
    thermo.clearFault();
  }
  
  Serial.println("-----------------------");
  delay(2000);
}