const int relayPin = 13;  // relay connected to pin 13
const int intercomButton = 2;  // Intercom button connected to pin 2
const int ledPin = 3;  // LED pin for simulating intercom ringing

void setup() {
  Serial.begin(9600);
  pinMode(relayPin, OUTPUT);
  pinMode(intercomButton, INPUT_PULLUP);  // Internal pull-up resistor
  pinMode(ledPin, OUTPUT);  // LED pin for simulating intercom ringing
  attachInterrupt(digitalPinToInterrupt(intercomButton), intercomInterrupt, FALLING);

  // Relay is initially in the closed position
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
    } else if (command == "RING_INTERCOM") {
      // Trigger the intercom or take any other action
      handleIntercomSignal();
    }
  }
}

void intercomInterrupt() {
  // Interrupt routine for the intercom button
  // Trigger the relay to open the gate
  digitalWrite(relayPin, LOW);
  delay(15000);  // Keep the gate open for 15 seconds (adjust as needed)
  digitalWrite(relayPin, HIGH);
}

void handleIntercomSignal() {
  // Additional function to handle the intercom signal
  // Implement the logic to ring the intercom inside the house
  // You may use a separate output pin to trigger a relay connected to the intercom button
  // Add necessary delay or debounce if needed
  // For example, you can blink an LED to simulate ringing
  digitalWrite(ledPin, HIGH);
  delay(INTERCOM_NOTIFY_DELAY);
  digitalWrite(ledPin, LOW);
}