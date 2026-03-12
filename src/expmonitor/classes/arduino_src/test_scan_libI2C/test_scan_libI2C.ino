#include <Wire.h>

void setup() {
  Wire.begin();
  
  // Set to 9600 baud as per your request
  Serial.begin(9600);
  
  // Safety timeout to prevent the Arduino from freezing if the bus is unstable
  Wire.setWireTimeout(3000, true); 

  Serial.println("\n--- I2C Scanner Ready (9600 baud) ---");
}

void loop() {
  byte error, address;
  int nDevices = 0;

  Serial.println("Scanning...");

  for (address = 1; address < 127; address++) {
    // The i2c_scanner uses the return value of
    // the Write.endTransmission to see if
    // a device did acknowledge to the address.
    Wire.beginTransmission(address);
    error = Wire.endTransmission();

    if (error == 0) {
      Serial.print("Device found at address 0x");
      if (address < 16) Serial.print("0");
      Serial.print(address, HEX);

      // Identification Guide
      if (address == 0x38) Serial.println(" -> AHT20 (Humidity/Temp)");
      else if (address == 0x76 || address == 0x77) Serial.println(" -> BMP280 (Pressure/Temp)");
      else if (address == 0x1E) Serial.println(" -> HMC5883L Magnetometer");
      else if (address == 0x0D) Serial.println(" -> QMC5883L Magnetometer (Clone)");
      else Serial.println(" -> Unknown device");

      nDevices++;
    }
    else if (error == 4) {
      Serial.print("Unknown error at address 0x");
      if (address < 16) Serial.print("0");
      Serial.println(address, HEX);
    }
  }

  if (nDevices == 0) {
    Serial.println("No I2C devices found. Check wiring and power.");
  } else {
    Serial.println("Scan complete.");
  }

  delay(2000); 
}