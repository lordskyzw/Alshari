#include <MFRC522.h>
#include <Arduino.h>

// Constants for LEDC
const int servoChannel = 0;  // Use first channel of 16 available
const int servoFrequency = 50;  // Standard servo frequency 50Hz
const int servoResolution = 10;  // 10 bit resolution

const int servoMinDuty = 512;  // Minimum duty cycle for servo (0 degrees)
const int servoMaxDuty = 2560;  // Maximum duty cycle for servo (180 degrees)
bool gatePaused = false;

// Constants for pin assignments
constexpr uint8_t RESET_PIN = 5;
constexpr uint8_t SS_PIN = 21;
constexpr int MOTOR_PIN = 12;
constexpr int MOTION_SENSOR_PIN = 34;
constexpr int BLUE_LED_PIN = 26;
constexpr int GREEN_LED_PIN = 27;
constexpr int RED_LED_PIN = 14;

// Constants for operation
constexpr unsigned long VEHICLE_DETECTION_INTERVAL = 5000; // 5 seconds

// Global variables
unsigned long lastVehicleDetectedTime = 0;
bool isVehiclePresent = false;
String incomingCommand = "";

// Initialize RFID and LED state
//MFRC522 rfid(SS_PIN, RESET_PIN);

void setup() {
  pinMode(MOTOR_PIN, OUTPUT);
  pinMode(MOTION_SENSOR_PIN, INPUT);
  pinMode(RED_LED_PIN, OUTPUT);
  pinMode(GREEN_LED_PIN, OUTPUT);
  pinMode(BLUE_LED_PIN, OUTPUT);
  Serial.begin(115200);
  SPI.begin();
  //rfid.PCD_Init();
  ledcSetup(servoChannel, servoFrequency, servoResolution);
  ledcAttachPin(MOTOR_PIN, servoChannel);
  
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
    int dutyCycle = servoMinDuty;
    ledcWrite(servoChannel, dutyCycle);
  }
}

void closeGate() {
  if (!gatePaused) {
    Serial.println("Closing gate");
    // Calculate duty cycle for 180 degrees (modify based on your servo)
    int dutyCycle = servoMaxDuty;
    ledcWrite(servoChannel, dutyCycle);
  }
}

void pauseGate() {
  // Pausing the gate movement might require stopping the PWM signal
  // This implementation will just stop updating the duty cycle
  gatePaused = !gatePaused;
  if (gatePaused) {
    Serial.println("Gate paused");
  } else {
    Serial.println("Gate unpaused");
    // Optionally, add logic to resume movement
  }
}

void readSerialCommands() {
  digitalWrite(BLUE_LED_PIN, LOW);
  digitalWrite(RED_LED_PIN, LOW);
  digitalWrite(GREEN_LED_PIN, HIGH);
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
  digitalWrite(GREEN_LED_PIN, LOW);
}
