#include <AccelStepper.h>
#include <SoftwareSerial.h>
#include "Movement.h"

// Define pins
#define Y_STEP_PIN 6    // Vertical
#define Y_DIR_PIN 7
#define X_STEP_PIN 9    // Horizontal
#define X_DIR_PIN 8

#define YLIDAR_RX_PIN 2
#define YLIDAR_TX_PIN 3
#define XLIDAR_RX_PIN 4
#define XLIDAR_TX_PIN 5

// Create objects
AccelStepper stepperY(AccelStepper::DRIVER, Y_STEP_PIN, Y_DIR_PIN);
AccelStepper stepperX(AccelStepper::DRIVER, X_STEP_PIN, X_DIR_PIN);
Movement movement;

SoftwareSerial yLidarSerial(YLIDAR_RX_PIN, YLIDAR_TX_PIN);
SoftwareSerial xLidarSerial(XLIDAR_RX_PIN, XLIDAR_TX_PIN);

// Define global variables
static bool hasMoved = false;
long deltaSteps = 500L;
uint16_t xLidarDistance = 0, yLidarDistance = 0;
unsigned int lastSensorRead = 0;
const unsigned int sensorInterval = 100;

bool loggingActive = false;
bool autoRunning = false;


void setup() {
  Serial.begin(9600);
  stepperY.setMaxSpeed(1000);
  stepperY.setAcceleration(500);
  stepperX.setMaxSpeed(1000);
  stepperX.setAcceleration(500);
  stepperY.setCurrentPosition(0);
  stepperX.setCurrentPosition(0);

  // Auto-start logging and movement
  delay(3000);
  loggingActive = false;
  autoRunning = true;
}

void loop() {
    // Emergency stop check
    if (Serial.available()) {
        String cmd = Serial.readStringUntil('\n');
        cmd.trim(); cmd.toLowerCase();
        if (cmd == "stop") {
            stepperY.stop();
            stepperX.stop();
            autoRunning = false;
            Serial.println("EMERGENCY STOP!");
        }
        if (cmd == "down") {
            if (autoRunning && !hasMoved && stepperY.distanceToGo() == 0) {
                movement.moveYDown(20); // 10 steps = 1.25", so 1 step = 1/8"
                hasMoved = true;
            }
        }
        if (cmd == "up") {
            if (autoRunning && !hasMoved && stepperY.distanceToGo() == 0) {
                movement.moveYUp(20); // 10 steps = 1.25", so 1 step = 1/8"
                hasMoved = true;
            }
        }
        if (cmd == "left") {
            if (autoRunning && !hasMoved && stepperX.distanceToGo() == 0) {
                movement.moveXLeft(20); // 10 steps = 1.25", so 1 step = 1/8"
                hasMoved = true;
            }
        }
        if (cmd == "right") {
            if (autoRunning && !hasMoved && stepperX.distanceToGo() == 0) {
                movement.moveXRight(20); // 10 steps = 1.25", so 1 step = 1/8"
                hasMoved = true;
            }
        }
        else {
            hasMoved = false;
            autoRunning = true;
            Serial.println("Movement Condition RESET");
        }

    }

    // Run steppers
    stepperY.run();
    stepperX.run();
}
