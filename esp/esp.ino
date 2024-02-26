#include <ESP32Servo.h>
#include <MFRC522.h>
#include <Arduino.h>

// Constants for pin assignments
constexpr uint8_t RESET_PIN = 5;
constexpr uint8_t SS_PIN = 21;
constexpr int MOTOR_PIN = 12;  // Pin connected to the servo signal
constexpr int MOTION_SENSOR_PIN = 34;
constexpr int BLUE_LED_PIN = 26;
constexpr int GREEN_LED_PIN = 27;
constexpr int RED_LED_PIN = 14;

// Constants for operation
constexpr unsigned long VEHICLE_DETECTION_INTERVAL = 5000; // 5 seconds

// Global variables
Servo gateServo;  // Create a servo object to control the gate
unsigned long lastVehicleDetectedTime = 0;
bool gatePaused = false;
String incomingCommand = "";

void setup() {
  pinMode(MOTION_SENSOR_PIN, INPUT);
  pinMode(RED_LED_PIN, OUTPUT);
  pinMode(GREEN_LED_PIN, OUTPUT);
  pinMode(BLUE_LED_PIN, OUTPUT);
  Serial.begin(115200);
  SPI.begin();
  gateServo.attach(MOTOR_PIN);  // Attach the servo to the motor pin
  closeGate(); 
}

void loop() {
  checkVehiclePresence();
  readSerialCommands();
}

void checkVehiclePresence() {
  bool motionDetected = digitalRead(MOTION_SENSOR_PIN) == HIGH;
  unsigned long currentTime = millis();

  if (motionDetected && (currentTime - lastVehicleDetectedTime > VEHICLE_DETECTION_INTERVAL)) {
    Serial.println("Vehicle detected");
    indicateVehicleDetected();
    lastVehicleDetectedTime = currentTime;
  } else if (!motionDetected) {
    resetVehicleDetectionIndicator();
  }
}

void indicateVehicleDetected() {
  digitalWrite(RED_LED_PIN, HIGH);
}

void resetVehicleDetectionIndicator() {
  digitalWrite(RED_LED_PIN, LOW);
}

void openGate() {
  if (!gatePaused) {
    Serial.println("Opening gate");
    digitalWrite(GREEN_LED_PIN, HIGH);
    gateServo.write(120);  // Move servo to open position
    digitalWrite(GREEN_LED_PIN, LOW);
  }
}

void closeGate() {
  if (!gatePaused) {
    digitalWrite(GREEN_LED_PIN, HIGH);
    Serial.println("Closing gate");
    gateServo.write(0);  // Move servo to closed position
    digitalWrite(GREEN_LED_PIN, LOW);
  }
}

void pauseGate() {
  gatePaused = !gatePaused;  // Toggle the pause state
  if (gatePaused) {
    Serial.println("Gate paused");
  } else {
    Serial.println("Gate unpaused");
  }
}

void readSerialCommands() {
  if (Serial.available() > 0) {
    incomingCommand = Serial.readStringUntil('\n');
    incomingCommand.trim();

    if (incomingCommand == "openGate") {
      openGate();
    } else if (incomingCommand == "closeGate") {
      closeGate();
    } else if (incomingCommand == "pauseGate") {
      pauseGate();
    } else {
      Serial.println("Invalid command");
    }
  }
}
