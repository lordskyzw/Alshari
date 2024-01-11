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
const int red = 26;
const int grn = 27;
const int blue = 14;
// const int encoderPinA = 16;  // Encoder Pin A
// const int encoderPinB = 17;  // Encoder Pin B

// define variables
// volatile int lastEncoded = 0;
// volatile long encoderTargetPos = 0;
// volatile long encoderPos = 0;
// long lastEncoderPos = 0;
// int encoderTargetPosOpen = 1000;   // Encoder position when gate is fully open
// int encoderTargetPosPedestrian = 250; // Encoder position when gate is open for pedestrian
// int encoderTargetPosClosed = 0;    // Encoder position when gate is fully closed
unsigned long lastVehicleDetectTime = 0;  // Global variable to store the last detection time
int lastPIRState = LOW;  // Global variable to store the PIR state
const unsigned long vehicleDetectInterval = 5000;  // Interval of 5 s
unsigned long stime;
bool gateClosing = false;
bool gateMoving = false; 
String gateState = "";

void setup() {
  // pinMode(led, OUTPUT);
  // pinMode(grn, OUTPUT);
  // pinMode(red, OUTPUT);
  pinMode(m1, OUTPUT);
  pinMode(m2, OUTPUT);
  pinMode(motionSensorPin, INPUT);
  pinMode(blue, OUTPUT);
  pinMode(red, OUTPUT);
  pinMode(grn, OUTPUT);
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

void checkVehiclePresence() {
// we need to check if it has been 5 seconds since the last detection

  if (digitalRead(motionSensorPin) == HIGH) {
    if (lastPIRState == LOW){//if the last state was low, then the vehicle has just arrived
      digitalWrite(blue, HIGH);
      Serial.println("Vehicle detected");
      lastPIRState = HIGH;
    }
  }
  else {//no motion detected
    digitalWrite(blue, LOW);
    if (lastPIRState == HIGH) {
      lastPIRState = LOW;
      digitalWrite(blue, LOW);
    }
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
  // digitalWrite(red, HIGH);
  // digitalWrite(grn, LOW);
  digitalWrite(m1, HIGH);
  digitalWrite(m2, LOW);
  gateClosing = false;
}

void closeGate() {
  //encoderTargetPos = encoderTargetPosClosed;
  gateMoving = true;
  // digitalWrite(red, LOW);
  // digitalWrite(grn, HIGH);
  digitalWrite(m1, LOW);
  digitalWrite(m2, HIGH);
  gateClosing = true;
}

void pauseGate() {
  digitalWrite(m1, LOW);
  digitalWrite(m2, LOW);
  gateClosing = false;
  gateMoving = false;
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
      pauseGate();\
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



