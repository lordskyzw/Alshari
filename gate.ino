const int relayPin = 13;  // relay connected to pin 13

void setup() {
  Serial.begin(9600);
  pinMode(relayPin, OUTPUT);
  //relay is initially in the closed position
  digitalWrite(relayPin, HIGH);
}

void loop() {
  if (Serial.available() > 0) {
    // Read the incoming command
    String command = Serial.readStringUntil('\n');

    // Check if the command is to open the gate
    if (command == "OPEN_GATE") {
      // Trigger the relay to open the gate
      digitalWrite(relayPin, LOW);
      delay(15000);
      digitalWrite(relayPin, HIGH); 
    }
  }
}
