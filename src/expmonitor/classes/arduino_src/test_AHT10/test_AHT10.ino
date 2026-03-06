#include <Adafruit_AHTX0.h>
#include <avr/wdt.h> // Library for the Watchdog: this library reboot the arduino if a sensor block more than XX second (safety tiner)

Adafruit_AHTX0 aht; // Create the sensor object

void setup() {
  wdt_enable(WDTO_2S); // Enable the watchdog with an 2-second safety timer
  Serial.begin(9600);
  // Connect to AHT10 
  if (!aht.begin()) {
  Serial.println("Error: AHT10 not found.");
  }
  else{
  Serial.println("Connected to AHT10.");
  }
}

void loop() {
wdt_reset(); // "Pet the dog" : tells the Arduino "everything is fine"

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
    Serial.print("°C,");
    Serial.print(humidity.relative_humidity);
    Serial.println("%.");// println for last line
    }
    else{// if no signal is read, we send back nan and nan.
      Serial.println("nan,nan");
    }
}

