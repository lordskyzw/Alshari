const int driverPin = 13;  // relay connected to pin 13

void setup() {
  Serial.begin(9600);
  pinMode(driverPin, OUTPUT);
  //relay is initially in the closed position
  digitalWrite(driverPin, HIGH);
}

void loop() {
  if (Serial.available() > 0) {
    // Read the incoming command
    String command = Serial.readStringUntil('\n');

    // Check if the command is to open the gate
    if (command == "OPEN_GATE") {
      // Trigger the relay to open the gate
      digitalWrite(driverPin, LOW);
      delay(15000);
      digitalWrite(driverPin, HIGH); 
    }
  }
}
