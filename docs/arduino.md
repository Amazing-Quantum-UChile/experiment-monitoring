# Arduino
## Current code
The code which runs on the Arduino is the [`main.ino`](src/expmonitor/classes/arduino_src/main/main.ino) which is given in the [`arduino_src`](src/expmonitor/classes/arduino_src/main/main.ino) folder. We connect to the Arduino using a Serial protocol on the USB0 port. The Arduino check the Serial port and if the user send one of the following requests, it returns a measurement (string of coma separated numbers) from one of its sensors. 

* Request "a": reads the 16 Analog channels and returns their value. Output: "A0,A1,A2,..., A15"
* Request "b" reads the magnetic field from the HMC5883 magnetic field sensor.
* Request "h": reads temperature and humidity using the AHT10 sensor. Output: "temperature, humidity"
* Request "p" reads temperature, humidity and pressure from the AHT20+BMP280 sensor. Output: "temperature, humidity, temperature, pressure" .
* Request "t": reads temperature from MAX31865 sensors (2 sensors). Returns "T1, T2"
 

## Connecting sensors to the arduino


### Restricted Pins - Arduino Mega 2560
The Arduino Mega 2560 features 54 digital pins and 16 analog pins. While most can be used for any purpose, several are reserved for specific hardware communication protocols. These should not be used for General I/O (simple On/Off signals) or Chip Select (CS) (the "trigger" signal used to tell a specific SPI sensor to wake up and talk).

Using these reserved pins for other tasks can cause your code to crash, prevent your sensors from communicating, or stop your computer from recognize the Arduino.
Restricted Pins to Avoid

The following pins are reserved for system functions and should stay clear:

| Pin(s) | Function | Reason to Avoid |
| :--- | :--- | :--- |
| 0 & 1 | RX / TX | Used for USB Serial communication (Uploading code / Serial Monitor). |
| 13 | Internal LED | Connected to the onboard "L" LED; toggles during boot/reset, can cause glitches. |
| 20 & 21 | I2C Bus | Communication ports we will use with  AHT10 sensors for example (SDA/SCL). |
| 50 - 52 | SPI Bus | Communication ports we will use with MAX31865 data lines (MISO/MOSI/SCK). |
| 53 | SS (Hardware) | Must be set to `OUTPUT` for the Mega to act as SPI Master; risky for CS. |
| VCC/GND| Power | These are not programmable pins; they provide constant power/ground. |
| RESET | System | Touching this will reboot your Arduino immediately. |
| AREF | Analog Ref | Used for analog voltage reference only; not for digital signals. |


### MAX31865 (RTD Temperature - PT100/PT1000)
Protocol: SPI (Serial Peripheral Interface).
Note: Connect to the Hardware SPI pins of the Arduino Mega.

| MAX31865 Pin | Arduino Mega Pin | Function |
| :--- | :--- | :--- |
| VIN | 5V | Power Supply |
| GND | GND | Ground |
| CLK | 52 | SPI Clock |
| SDO  | 50 | Master In Slave Out |
| SDI  | 51 | Master Out Slave In |
| CS | 2-9 or 22-49 | Chip Select (Software defined) |



---

### AHT10 (Humidity & Ambient Temp)
Protocol: I2C (Inter-Integrated Circuit).
Note: Ensure no other I2C device shares the same address (0x38).

| AHT10 Pin | Arduino Mega Pin | Function |
| :--- | :--- | :--- |
| VIN | 5V | Power Supply |
| GND | GND | Ground |
| SDA | 20 | I2C Data |
| SCL | 21 | I2C Clock |

## Arduino Python class
The Arduino board object is defined in the [arduino.py](../src/expmonitor/classes/arduino.py) file. We instantiate the Arduino board in the [config.py](../src/expmonitor/config.py) file before we instantiate the sensors plugged on the board. Any sensor connected to the Arduino board takes the board as an argument to which it will query measurements. 


