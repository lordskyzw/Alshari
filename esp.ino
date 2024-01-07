#include <MFRC522.h>

// Define RFID and other variables
constexpr uint8_t RST_PIN = 5;        
constexpr uint8_t SS_PIN = 21;      
MFRC522 rfid(SS_PIN, RST_PIN);
String tag = "";
String incoming = "";

// Define pin assignments
const int led = 26;
const int grn = 27;
const int red = 14;
const int m1 = 13;
const int m2 = 12;
const int irReceiverPin = 15; // IR receiver pin for obstacle detection

const int encoderPinA = 16;  // Encoder Pin A
const int encoderPinB = 17;  // Encoder Pin B
volatile long encoderPos = 0;
long lastEncoderPos = 0;
int encoderTargetPosOpen = 1000;   // Encoder position when gate is fully open
int encoderTargetPosClosed = 0;    // Encoder position when gate is fully closed

bool gateClosing = false; // Flag to indicate if the gate is closing
bool gateMoving = false;  // Flag to indicate if the gate is moving

void setup() {
  pinMode(led, OUTPUT);
  pinMode(grn, OUTPUT);
  pinMode(red, OUTPUT);
  pinMode(m1, OUTPUT);
  pinMode(m2, OUTPUT);
  pinMode(irReceiverPin, INPUT); // Initialize IR receiver pin as input
  pinMode(encoderPinA, INPUT_PULLUP); // Enable internal pull-up
  pinMode(encoderPinB, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(encoderPinA), updateEncoder, CHANGE);
  attachInterrupt(digitalPinToInterrupt(encoderPinB), updateEncoder, CHANGE);
  Serial.begin(115200);
  SPI.begin();      
  rfid.PCD_Init();
  moveToInitialPosition();
}

void loop() {
  readTag();
  readSerialCommands();
  controlGate();
}

void moveToClosedPosition() {
  // Check if the gate is already in the closed position
  if (encoderPos != encoderTargetPosClosed) {
    closeGate();

    // Continuously monitor until the gate is fully closed
    while (encoderPos != encoderTargetPosClosed) {
      if (digitalRead(irReceiverPin) == LOW) {
        pauseGate();
        return;
      }
    }
    pauseGate(); // Stop the gate once it's fully closed
  }
}

void openGate() {
  encoderTargetPos = encoderTargetPosOpen;
  gateMoving = true;
  digitalWrite(red, HIGH);
  digitalWrite(grn, LOW);
  digitalWrite(m1, HIGH);
  digitalWrite(m2, LOW);
  gateClosing = false;
}

void closeGate() {
  encoderTargetPos = encoderTargetPosClosed;
  gateMoving = true;
  digitalWrite(red, LOW);
  digitalWrite(grn, HIGH);
  digitalWrite(m1, LOW);
  digitalWrite(m2, HIGH);
  gateClosing = true;
}

void pauseGate() {
  digitalWrite(m1, LOW);
  digitalWrite(m2, LOW);
  gateClosing = false;
}

void updateEncoder() {
  int MSB = digitalRead(encoderPinA); // MSB = most significant bit
  int LSB = digitalRead(encoderPinB); // LSB = least significant bit

  int encoded = (MSB << 1) | LSB; // Converting the 2 pin value to single number
  int sum = (lastEncoded << 2) | encoded; // Adding it to the previous encoded value

  if (sum == 0b1101 || sum == 0b0100 || sum == 0b0010 || sum == 0b1011) encoderPos++;
  if (sum == 0b1110 || sum == 0b0111 || sum == 0b0001 || sum == 0b1000) encoderPos--;

  lastEncoded = encoded; // Store this value for next time
}


void readTag() {
  if (!rfid.PICC_IsNewCardPresent()) {
    return;
  }
  if (rfid.PICC_ReadCardSerial()) {
    tag = "";
    for (byte i = 0; i < 4; i++) {
      tag += String(rfid.uid.uidByte[i], HEX);
    }
    Serial.println(tag);
    digitalWrite(led, HIGH);
    delay(50);
    digitalWrite(led, LOW);
    rfid.PICC_HaltA();
    rfid.PCD_StopCrypto1();
  }
}

void readSerialCommands() {
  if (Serial.available() > 0) {
    incoming = Serial.readStringUntil('\n');
    incoming.trim();
    if (incoming == "openGate") {
      openGate();
    } else if (incoming == "closeGate") {
      closeGate();
    } else if (incoming == "pauseGate") {
      pauseGate();
    } else {
      Serial.println("Incorrect Command");
    }
  }
}

void controlGate() {
  if (gateMoving) {
    // Check if the IR sensor is triggered and the gate is closing
    if (digitalRead(irReceiverPin) == LOW && gateClosing) {
      pauseGate(); // Stop the gate if the IR beam is broken during closing
      Serial.println("Obstacle detected, gate stopped.");
    } else {
      // Check if the gate has reached its target position
      if (encoderPos == encoderTargetPos) {
        gateMoving = false; // Stop the gate if the target position is reached
        pauseGate(); // Use pauseGate function to stop the motor
        Serial.println("Target position reached, gate stopped.");
      } else {
        // Adjust the motor control to move towards the target position
        if (encoderPos < encoderTargetPos) {
          openGate(); // Continue opening the gate
        } else {
          closeGate(); // Continue closing the gate
        }
      }
    }
  }
}


