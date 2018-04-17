const byte ledPin = 13;
const byte interruptPin = 2;
const byte resetPin = 12;

volatile byte state = LOW;

unsigned long time; 
unsigned long lastTime;

void setup() {
  Serial.begin(9600);
  
  pinMode(ledPin, OUTPUT);
  pinMode(12, OUTPUT);
  pinMode(interruptPin, INPUT_PULLUP);
  
  attachInterrupt(digitalPinToInterrupt(interruptPin), blink, CHANGE);
  
  time = millis();
  lastTime = time;
  analogWrite(resetPin, 255);
  digitalWrite(12, HIGH);
}
 
void loop() {
  digitalWrite(ledPin, state);
  
  time = millis();
  if  (time - lastTime == 5000) {
    Serial.println("Reset");
    lastTime = millis();
    
    digitalWrite(resetPin, LOW); // Rest the device
    delay(500);
    digitalWrite(resetPin, HIGH); // Normal state
    delay(10000);
  }
  else {
    digitalWrite(resetPin, HIGH); // Normal state
  }
}

void blink() {
  state = !state;
  lastTime = millis();
}
