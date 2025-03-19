#include <SD.h>
#include <SPI.h>

const int chipSelect = 4;
const int ledPin = 3;
const int ledMeter = 2;
const int legSwitchPin = 5;    // Push button pin
const int motorSignalPin = 8;  // Pin to read motor signal/LED status
bool systemStarted = false;
const int homeSignalPin = 6;
int previousHomeState = -1;       // Track home signal changes
int previousMotorState = -1;
bool isHomePosition = false; 

int step = 1;
int fileIndex = 1;

void setup() {
  pinMode(ledPin, OUTPUT);
  pinMode(ledMeter, OUTPUT);
  pinMode(legSwitchPin, INPUT_PULLUP);
  pinMode(homeSignalPin, INPUT_PULLUP);
  pinMode(motorSignalPin, INPUT);

  Serial.begin(38400);
  while (!Serial) {
    ;  // Wait for serial port to connect
  }

  Serial.println("SD card Initializing...");
  if (!SD.begin(chipSelect)) {
    Serial.println("SD card initialization failed!");
    return;
  }
  Serial.println("SD card initialized.");
  delay(300);

  Serial.println("Checking connection from Hioki...");
  Serial1.begin(38400);
  delay(500);
  Serial.println("Serial1 initialized");
  Serial.println("Sending command and getting response from Hioki...");

  Serial1.print("*IDN?\n");
  delay(300);

  String responseBack = "";
  while (Serial1.available()) {
    char d = Serial1.read();
    responseBack += d;
  }

  if (responseBack.length() > 0) {
    Serial.println("Hioki RM3545-02 Response:");
    digitalWrite(ledMeter, HIGH);
    Serial.println(responseBack);
  } else {
    Serial.println("No response from Hioki!");
  }

}

void writeToSdCard(String data) {
  String filename = "data" + String(fileIndex) + ".txt";
  File file = SD.open(filename, FILE_WRITE);
  if (file) {
    file.println("Step " + String(step) + ", " + data);
    file.close();
    delay(10);
  } else {
    Serial.println("Data write failed!");
  }
}

String readFromHioki() {
  Serial1.print("FETC?\n");
  delay(10);
  String response = "";
  while (Serial1.available()) {
    char c = Serial1.read();
    response += c;
  }
  return response;
}

String formatHiokiData(String rawData) {
  rawData.trim();
  float value = rawData.toFloat();
  value *= 1000;
  if (value > 99999) {
    value = 9999;
  }
  // Format the value to two decimal places with unit "m Ohms"
  char formattedValue[15];
  snprintf(formattedValue, sizeof(formattedValue),"%.2f",  value);

  return String(formattedValue);
}
void loop() {
  // Read the leg switch state
  int legSwitchState = digitalRead(legSwitchPin);

  // Check if the leg switch is activated
  if (legSwitchState == HIGH) {
    // Enter monitoring loop
    while (true) {
      // Read the current motor and home signal states
      int currentMotorState = digitalRead(motorSignalPin);
      int currentHomeState = digitalRead(homeSignalPin);

      // Detect motor state change
      if (currentMotorState != previousMotorState) {
        previousMotorState = currentMotorState;

        if (currentMotorState == HIGH) {  // Motor stopped
          digitalWrite(ledPin, LOW);
          delay(200);
          if (isHomePosition) {
            
            String hiokiData = readFromHioki();
            if (hiokiData.length() > 0) {
              String formattedData = formatHiokiData(hiokiData);
              writeToSdCard(formattedData);  // Write as final step
              Serial.println( String(step) +","+ formattedData);
              delay(10);
              step = 1;      // Reset for next recording
              fileIndex = 1; // Reset step count
            }
          } else {
            
            String hiokiData = readFromHioki();
            if (hiokiData.length() > 0) {
              String formattedData = formatHiokiData(hiokiData);
              writeToSdCard(formattedData);  // Write as current step
              Serial.println( String(step) +","+ formattedData);
              step++;        // Increment for next recording
              fileIndex++;
            }
          }
        } else {  // Motor moving
          digitalWrite(ledPin, HIGH);
        }
      }

      // Detect home position state change
      if (currentHomeState != previousHomeState) {
        previousHomeState = currentHomeState;

        if (currentHomeState == HIGH) {
          delay(10);
          isHomePosition = true;
        } else {
          delay(10);
          isHomePosition = false;
        }
      }

      legSwitchState = digitalRead(legSwitchPin);
      delay(50);
      // Exit monitoring loop if leg switch is deactivated
      if (legSwitchState == LOW) {
        break;
      }

      delay(50);
    }
  }
}
