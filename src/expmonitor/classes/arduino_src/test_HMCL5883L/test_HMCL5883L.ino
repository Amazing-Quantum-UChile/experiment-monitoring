#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_HMC5883_U.h>

Adafruit_HMC5883_Unified mag = Adafruit_HMC5883_Unified(12345); // Create the sensor object

void setup() {
  Serial.begin(9600);
  
  // Connect to HMC5883L
  if (!mag.begin()) {
    Serial.println("Error: HMC5883L not found.");
  }
  else {
    Serial.println("Connected to HMC5883L.");
    // Choose the Gain 1_3 | 1_9 | 8_1 (from the most sensitive to the less sensitive)
    mag.setMagGain(HMC5883_MAGGAIN_1_3);  
    // mag.setMagGain(HMC5883_MAGGAIN_8_1);
  }
}

void loop() {
  sensors_event_t event;
  // Read data
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

  delay(1500); // Small delay to avoid saturating the Serial monitor
}