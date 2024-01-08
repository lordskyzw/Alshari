// this is the prototype version, it exclude the IR Sensor

#include <MFRC522.h>

// Define RFID and other variables
constexpr uint8_t RST_PIN = 5;        
constexpr uint8_t SS_PIN = 21;      
MFRC522 rfid(SS_PIN, RST_PIN);
String tag = "";
String incoming = "";

// Define pin assignments
const int m1 = 13;
const int m2 = 12;
const int motionSensorPin = 34;
// const int encoderPinA = 16;  // Encoder Pin A
// const int encoderPinB = 17;  // Encoder Pin B
// volatile int lastEncoded = 0;
// volatile long encoderTargetPos = 0;
// volatile long encoderPos = 0;
// long lastEncoderPos = 0;
// int encoderTargetPosOpen = 1000;   // Encoder position when gate is fully open
// int encoderTargetPosPedestrian = 250; // Encoder position when gate is open for pedestrian
// int encoderTargetPosClosed = 0;    // Encoder position when gate is fully closed
bool gateClosing = false;
bool gateMoving = false; 

void setup() {
  // pinMode(led, OUTPUT);
  // pinMode(grn, OUTPUT);
  // pinMode(red, OUTPUT);
  pinMode(m1, OUTPUT);
  pinMode(m2, OUTPUT);
  pinMode(motionSensorPin, INPUT);
  // pinMode(encoderPinA, INPUT_PULLUP); // Enable internal pull-up
  // pinMode(encoderPinB, INPUT_PULLUP);
  // attachInterrupt(digitalPinToInterrupt(encoderPinA), updateEncoder, CHANGE);
  // attachInterrupt(digitalPinToInterrupt(encoderPinB), updateEncoder, CHANGE);
  Serial.begin(115200);
  SPI.begin();      
  rfid.PCD_Init();
  //moveToClosedPosition();
}

void loop() {
  checkVehiclePresence();
  readSerialCommands();
  //controlGate();
}

void checkVehiclePresence(){
  if (digitalRead(motionSensorPin) == HIGH) {
    Serial.println("Vehicle detected");
  }
}

// void moveToClosedPosition() {
//   while (encoderPos != encoderTargetPosClosed) {
//     closeGate();
//   }
//   pauseGate();
// }

void openGate() {
  //encoderTargetPos = encoderTargetPosOpen;
  gateMoving = true;
  digitalWrite(red, HIGH);
  digitalWrite(grn, LOW);
  digitalWrite(m1, HIGH);
  digitalWrite(m2, LOW);
  gateClosing = false;
}

void closeGate() {
  //encoderTargetPos = encoderTargetPosClosed;
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
    }
    else {
      Serial.println("Incorrect Command");
    }
  }
}

// void controlGate() {
//   //after handling opening of the gate and closing of the gate during (if (gateMoving))), it closes the gate as that is the default state
//   if (gateMoving) {
//     if (encoderPos == encoderTargetPos) {
//       gateMoving = false; 
//       pauseGate(); 
//       Serial.println("Target position reached, gate stopped.");
//     } else {
//       if (encoderPos < encoderTargetPos) {
//         openGate();
//       } else {
//         closeGate();
//       }
//     }
//   } else {
//     delay(15000);
//     closeGate();
//   }
// }



