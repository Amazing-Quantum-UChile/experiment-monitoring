
// Global configuration
const int NUM_CHANNELS = 16;      // Number of ADC pins to read (A0 to A11)
const int SAMPLES_PER_READ = 10;  // Number of samples for averaging ADC


void setup() {
  // put your setup code here, to run once:
Serial.begin(9600);
}

void loop() {
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
