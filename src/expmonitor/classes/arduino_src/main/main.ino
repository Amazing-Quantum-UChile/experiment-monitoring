/*
 * DEVICE: Arduino Mega 2560
 * DESCRIPTION: Code which return sensor data upon request
 Request "a": reads the 16 Analog channels and returns their value. Output: "A0,A1,A2,..., A15"
 Request "h": reads temperature and humidity using the AHT10 sensor. Output: "temperature, humidity"
 Request "t": reads temperature from MAX31865 sensors (2 sensors). Returns "T1, T2"
 Request "p" reads temperature, humidity and pressure from the AHT20+BMP280 sensor. Output: "temperature, humidity, temperature, pressure" .
 */
#include <avr/wdt.h> // Library for the Watchdog: this library reboot the arduino if a sensor block more than XX second (safety tiner)
#include <Adafruit_Sensor.h>
#include <Adafruit_AHTX0.h>
#include <Adafruit_MAX31865.h>
#include <Adafruit_BMP280.h>
#include <Adafruit_HMC5883_U.h>
#include <Wire.h>


///////////////////////////////
// Global configuration
///////////////////////////////
const char TRIGGER_ADC = 'a';    // Single byte trigger for ADC from Python
const char TRIGGER_AHT = 'h'; // Single byte trigger for humidity sensor
const char TRIGGER_BMP = 'p'; // Single byte trigger for pressure and humidity sensor
const char TRIGGER_MAX = 't'; // Single byte trigger for MAX temperature sensor
const char TRIGGER_MAGN = 'b'; // Single byte trigger for magnetic field sensor

// ADC
const int NUM_CHANNELS = 16;      // Number of ADC pins to read (A0 to A11)
const int SAMPLES_PER_READ = 10;  // Number of samples for averaging ADC
// AHT10/20 sensor and BMP280 sensors
Adafruit_AHTX0 aht; // Create the AHT sensor object
Adafruit_BMP280 bmp; 

// MAX31865
#define NUM_MAX 2 // Number of temperature sensors
#define RREF      430.0 // resistance for PT100 sensors.
#define RNOMINAL  100.0 // nominal resistance at 0°. 
Adafruit_MAX31865 temp_max[NUM_MAX] = {
  Adafruit_MAX31865(10, 51, 50, 52),
  Adafruit_MAX31865(9, 51, 50, 52)
};
float max_offsets[NUM_MAX] = {-6.5, 2}; //offset because each sensor was badly soldered and constructed


// HMC5883 magentic field sensor
Adafruit_HMC5883_Unified mag = Adafruit_HMC5883_Unified(12345); // Create the sensor object

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
    message = message+"AHT10/20 not found; ";
  }

  // BMP280
  if (!bmp.begin()) {
    connection_success = false;
    message = message+"BMP280 not found; ";
  } else {
    /* * CONFIGURATION: High Precision Mode
     * Mode: NORMAL (Sensor measures automatically)
     * Temp Oversampling: X4 (Stable temperature, low self-heating)
     * Pressure Oversampling: X16 (Ultra High Resolution)
     * IIR Filter: X16 (Filters out sudden pressure spikes/noise)
     * Standby Time: 1000ms (1 second gap between measurements, we do not read the data when the arduino query)
     */
    bmp.setSampling(Adafruit_BMP280::MODE_NORMAL,     
                    Adafruit_BMP280::SAMPLING_X4,     
                    Adafruit_BMP280::SAMPLING_X16,    
                    Adafruit_BMP280::FILTER_X16,      
                    Adafruit_BMP280::STANDBY_MS_1000); 
  }

  // MAX31865
  for (int i = 0; i < NUM_MAX; i++) {
    temp_max[i].begin(MAX31865_3WIRE);// Initialize the sensor
    }

  // HMC5883L
  mag.begin(); // this does not return boolean
  
  // check if we can speak with the device
  Wire.beginTransmission(0x1E);
  if (Wire.endTransmission() != 0) { 
    connection_success = false;
    message = message + "HMC5883L not found; ";
  } 
  // Choose the Gain 1_3 | 1_9 | 8_1 (from the most sensitive to the less sensitive)
  mag.setMagGain(HMC5883_MAGGAIN_1_3);  
  // mag.setMagGain(HMC5883_MAGGAIN_8_1);
  

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

    // *******************************************************
    // PRESSURE AND HUMIDITY SENSOR AHT20+BMP280 READING
    // *******************************************************
    if (incomingByte == TRIGGER_BMP) {
      /// --- AHT20 SECTION ---
      sensors_event_t humidity, tempAHT;
      bool ahtSuccess = aht.getEvent(&humidity, &tempAHT);

      // If AHT20 fails, attempt reconnection
      if (!ahtSuccess) { 
        aht.begin();
        ahtSuccess = aht.getEvent(&humidity, &tempAHT);
      }

      // --- BMP280 SECTION ---
      float tempBMP = bmp.readTemperature();
      float pressHPa = bmp.readPressure() / 100.0;

      // If BMP280 fails (returns nan), attempt reconnection
      if (isnan(tempBMP) || isnan(pressHPa)) {
        bmp.begin(0x76);
        tempBMP = bmp.readTemperature();
        pressHPa = bmp.readPressure() / 100.0;
      }
      // 3. Output Data (Format:TempAHT ,Humidity,TempBMP,Pressure)
      if (ahtSuccess) {
        Serial.print(tempAHT.temperature, 2); Serial.print(",");
        Serial.print(humidity.relative_humidity, 2); Serial.print(",");
      } else {
        Serial.print("nan,nan,");
      }
      // Print BMP Data
      if (!isnan(tempBMP)) {
        Serial.print(tempBMP, 2); Serial.print(",");
        Serial.println(pressHPa, 2); 
      } else {
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

  // *****************************
  // MAGNETIC FIELD SENSOR HMC5883L
  // *****************************
  if (incomingByte == TRIGGER_MAGN) {
      sensors_event_t event;
      bool measureSuccess = mag.getEvent(&event);
      // If no data found, reconnect and redo the measurement
      if (!measureSuccess) { 
        mag.begin();
        measureSuccess = mag.getEvent(&event);
      }
    // Return the measurement
  if (measureSuccess) { 
    // Conversion from micro-Tesla (uT) to Gauss (G)
    float x_Gauss = event.magnetic.x / 100.0;
    float y_Gauss = event.magnetic.y / 100.0;
    float z_Gauss = event.magnetic.z / 100.0;

    Serial.print(x_Gauss, 4); // 4 decimals for precision in Gauss
    Serial.print(",");
    Serial.print(y_Gauss, 4);
    Serial.print(",");
    Serial.println(z_Gauss, 4);
  }
  else {
    // if no signal is read, we send back nan
    Serial.println("nan,nan,nan");
  }
  }
  }
}