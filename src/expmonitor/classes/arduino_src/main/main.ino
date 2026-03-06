/*
 * DEVICE: Arduino Mega 2560
 * DESCRIPTION: Code which return sensor data upon request
 Request "a": reads the 16 Analog channels and returns their value. Output: "A0,A1,A2,..., A15"
 Request "h": reads temperature and humidity using the AHT10 sensor. Output: "temperature, humidity"
 Request "t": reads temperature from MAX31865 sensors (2 sensors). Returns "T1, T2"
 */
#include <avr/wdt.h> // Library for the Watchdog: this library reboot the arduino if a sensor block more than XX second (safety tiner)
#include <Adafruit_AHTX0.h>
#include <Adafruit_MAX31865.h>

///////////////////////////////
// Global configuration
///////////////////////////////
const char TRIGGER_ADC = 'a';    // Single byte trigger for ADC from Python
const char TRIGGER_AHT = 'h'; // Single byte trigger for humidity sensor
const char TRIGGER_MAX = 't'; // Single byte trigger for MAX temperature sensor

// ADC
const int NUM_CHANNELS = 16;      // Number of ADC pins to read (A0 to A11)
const int SAMPLES_PER_READ = 10;  // Number of samples for averaging ADC
// AHT10 sensor
Adafruit_AHTX0 aht; // Create the AHT10 sensor object

// MAX31865
#define NUM_MAX 2 // Number of temperature sensors
#define RREF      430.0 // resistance for PT100 sensors.
#define RNOMINAL  100.0 // nominal resistance at 0°. 
Adafruit_MAX31865 temp_max[NUM_MAX] = {
  Adafruit_MAX31865(10, 51, 50, 52),
  Adafruit_MAX31865(9, 51, 50, 52)
};
float max_offsets[NUM_MAX] = {0, -7}; //offset because each sensor was badly soldered and constructed



void setup() {
  // wdt_enable(WDTO_2S); // Enable the watchdog with an 2-second safety timer
  Serial.begin(9600);

  /////////////////////
  // Connect to devices
  /////////////////////
  bool connection_success = true;
  String message = "";
  String prefix = "";
  
  // AHT10 sensor
  if (!aht.begin()) {
    connection_success = false;
    message = message+"AHT10 not found; ";
  }

  // MAX31865
  for (int i = 0; i < NUM_MAX; i++) {
    temp_max[i].begin(MAX31865_3WIRE);// Initialize the sensor
    }


  //////////////////////
  // Return info to user
  //////////////////////
  if (connection_success) {
    prefix = "1 ";
  } else {
    prefix = "0. Error: ";
  }
  // we return the error message
  Serial.println(prefix + message);
}

void loop() {
  // Check if the SBC has sent data to the Arduino
  if (Serial.available() > 0) {
    // Read the incoming byte
    char incomingByte = Serial.read();

    // *****************************  
    // ADC READING
    // *****************************
    
    // If the trigger byte 'a' is received, start the measurement cycle
    if (incomingByte == TRIGGER_ADC) {
      
      // Loop through each analog pin
      for (int pin = 0; pin < NUM_CHANNELS; pin++) {
        long runningSum = 0;

        // OVERSAMPLING: Read the pin multiple times
        for (int i = 0; i < SAMPLES_PER_READ; i++) {
          runningSum += analogRead(pin);
          // Small delay to allow the ADC capacitor to settle
          delayMicroseconds(50);
        }

        // Calculate the mathematical average
        float averagedValue = (float)runningSum / SAMPLES_PER_READ;

        // Print the result to the Serial buffer
        Serial.print(averagedValue);

        // Format as Comma Separated Values (CSV)
        // Add a comma after every value except the very last one
        if (pin < (NUM_CHANNELS - 1)) {
          Serial.print(",");
        }
      }

      // Send a Newline character (\n) to signal the end of the data string
      Serial.println();
    }
    
    // *****************************
    // HUMIDITY SENSOR AHT10 READING
    // *****************************
    if (incomingByte == TRIGGER_AHT) {
      sensors_event_t humidity, temp;
      // Read data. 
      bool measureSuccess = aht.getEvent(&humidity, &temp);
      // If no data found, reconnect and redo the measurement
      if (!measureSuccess) { 
        aht.begin();
      measureSuccess = aht.getEvent(&humidity, &temp);
      };
      // Return the measurement
      if (measureSuccess) { 
      Serial.print(temp.temperature);
      Serial.print(",");
      Serial.println(humidity.relative_humidity);// println for last line
      }
      else{// if no signal read, we send back nan and nan.
        Serial.println("nan,nan");
      }
    }

    // *****************************
    // TEMPERATURE SENSOR MAX31865
    // *****************************
    if (incomingByte == TRIGGER_MAX) {
        for (int i = 0; i < NUM_MAX; i++) {
          // Read raw temperature
          float rawTemp = temp_max[i].temperature(RNOMINAL, RREF);
          // Apply individual offset
          float calibratedTemp = rawTemp + max_offsets[i];
          if ((calibratedTemp < -200) | calibratedTemp>300 ) { // Unconnexion detection
              Serial.print("nan"); 
          }
          else{
          Serial.print(calibratedTemp);}
          if (i < NUM_MAX - 1) Serial.print(",");
        }
      Serial.println();
    }
  }
}