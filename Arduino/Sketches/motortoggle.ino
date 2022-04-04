#include "DHT.h"

//Digital pin associated with water pump
#define MOTOR_PIN 23 
#define MOISTURE_SENSOR_PIN A0
#define MOISTURE_SENSOR_PWR 53 

#define SENSOR_DELAY 10 
#define LOOP_DELAY_MIN 10 

#define DHTPIN 22 // what digital pin we're connected to 
#define DHTTYPE DHT22 // DHT 22 (AM2302), AM2321 define 

#define MOTOR_DURATION 10000 //how long to run the motor for (ms) define 
#define MOISTURE_THRESHOLD 10 // percent water remaining define WETTEST_READING 258 define 
#define DRIEST_READING 1004
#define WETTEST_READING 258

int WATER_MODE = false; 
DHT dht(DHTPIN, DHTTYPE); 

void setup() {
  Serial.begin(9600);
  Serial.println("Serial (9600) connection opened!");
  
  pinMode(MOTOR_PIN, OUTPUT);
  pinMode(MOISTURE_SENSOR_PWR, OUTPUT);
  pinMode(MOISTURE_SENSOR_PIN, INPUT);

  dht.begin();
  
  /*for (int t = 2048; t > 15; t/=2) {
    digitalWrite(MOTOR_PIN, HIGH);
    delay(t);
    digitalWrite(MOTOR_PIN, LOW);
    delay(t);
  }*/
  
}

void loop() {
  
  if (WATER_MODE) {
    runMotor();
    WATER_MODE = false;
    delay((uint32_t) LOOP_DELAY_MIN*60*10000);
  }
  
  // Reading temperature or humidity takes about 250 milliseconds!
  // Sensor readings may also be up to 2 seconds 'old' (its a very slow sensor)
  float h = dht.readHumidity();
  // Read temperature as Celsius (the default)
  float t = dht.readTemperature();
  // Read temperature as Fahrenheit (isFahrenheit = true)
  float f = dht.readTemperature(true);
  // Check if any reads failed and exit early (to try again).
  if (isnan(h) || isnan(t) || isnan(f)) {
    Serial.println("Failed to read from DHT sensor!");
    return;
  }
  // Compute heat index in Fahrenheit (the default)
  float hif = dht.computeHeatIndex(f, h);
  // Compute heat index in Celsius (isFahreheit = false)
  float hic = dht.computeHeatIndex(t, h, false);
  
  int mappedValue = readMoisture();
  Serial.print(h);
  Serial.print(" ");
  Serial.print(f);
  Serial.print(" ");
  Serial.print(mappedValue);
  
  if (mappedValue < MOISTURE_THRESHOLD) {
      WATER_MODE = true;
  }
  
  Serial.println();
  delay((uint32_t) 1000);
}

//converts the moisture sensor reading to a user friendly value
int moistureFn(int val) {
  float delta = DRIEST_READING - WETTEST_READING;
  float result = 0.0;
  
  val = val - WETTEST_READING;
  result = val / delta;
  result = result * 100;
  result = 100 - result;
  return (int) result;
}

int readMoisture() {
  digitalWrite(MOISTURE_SENSOR_PWR, HIGH);
  
  delay(SENSOR_DELAY);
  int sensorValue = analogRead(MOISTURE_SENSOR_PIN);
  int mappedValue = moistureFn(sensorValue);
  digitalWrite(MOISTURE_SENSOR_PWR, LOW);
  return mappedValue;
}

void runMotor() {
  digitalWrite(MOTOR_PIN, HIGH);
  delay(MOTOR_DURATION);
  digitalWrite(MOTOR_PIN, LOW);
}
