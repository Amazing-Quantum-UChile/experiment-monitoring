#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BMP280.h>
#include <Adafruit_AHTX0.h>

Adafruit_BMP280 bmp; 
Adafruit_AHTX0 aht;

void setup() {
  Serial.begin(9600);
  Wire.begin();
  // 1. Initialize AHT20
  if (!aht.begin()) {
    Serial.println("Error: AHT20 not found.");
  } else {
    Serial.println("Connected to AHT20.");
  }


  // 2. Initialize BMP280
  if (!bmp.begin()) {
    Serial.println("BMP280 error");
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
    Serial.println("Connected to BMP280.");
  }

  
  Serial.println("------------------------------");
}

void loop() {
  sensors_event_t humidity_event, temp_event;
  
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

  delay(1000); 
}