#include "AccelStepper.h"
#include <SoftwareSerial.h>
#include "Classes/Movement.h"

// Define pins
#define Y_STEP_PIN 6    // Vertical (up/down)
#define Y_DIR_PIN 7
#define X_STEP_PIN 9    // Horizontal (left/right)
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
const long deltaSteps = 500L;
uint16_t xLidarDistance = 0, yLidarDistance = 0;
unsigned int lastSensorRead = 0;
const unsigned int sensorInterval = 100;

enum TestState { TEST_IDLE, TEST_MOVE_TO_START, TEST_SCAN_ROW };
TestState testState = TEST_IDLE;

int customStep = 0;
const int customTotalSteps = 12;
long customMoveSteps[] = {
   146L * deltaSteps,
   120L * deltaSteps,
  -146L * deltaSteps,
  -120L * deltaSteps,
   146L * deltaSteps,
   120L * deltaSteps,
  -146L * deltaSteps,
  -120L * deltaSteps,
   146L * deltaSteps,
   120L * deltaSteps,
  -146L * deltaSteps,
  -120L * deltaSteps,
};
bool customIsHorizontal[] = {
  false, true, false, true, false, true, false, true, false, true, false, true
};

bool loggingActive = false;

// Read lidar
uint16_t readTFmini(SoftwareSerial &lidarSerial) {
  const uint8_t frameLength = 9;
  uint16_t distance = 0;
  if (lidarSerial.available() >= frameLength) {
    while (lidarSerial.available()) {
      if (lidarSerial.read() == 0x59 && lidarSerial.read() == 0x59) {
        uint8_t frame[frameLength];
        frame[0] = 0x59; frame[1] = 0x59;
        for (int i = 2; i < frameLength; i++) {
          while (!lidarSerial.available());
          frame[i] = lidarSerial.read();
        }
        uint8_t checksum = 0;
        for (int i = 0; i < 8; i++) checksum += frame[i];
        if (checksum == frame[8]) {
          distance = frame[2] | (frame[3] << 8);
          return distance;
        }
      }
    }
  }
  return distance;
}

// Logic
void processCommand(String cmd) {
  cmd.trim(); cmd.toLowerCase();
  if (testState != TEST_IDLE && cmd != "emergencystop") {
    Serial.println("Test in progress; manual commands are disabled.");
    return;
  }
  if (cmd == "down") {
    stepperY.moveTo(stepperY.currentPosition() + 15 * deltaSteps);
    Serial.println("Command: DOWN");
  }
  else if (cmd == "up") {
    stepperY.moveTo(stepperY.currentPosition() - 15 * deltaSteps);
    Serial.println("Command: UP");
  }
  else if (cmd == "left") {
    stepperX.moveTo(stepperX.currentPosition() - 15 * deltaSteps);
    Serial.println("Command: LEFT");
  }
  else if (cmd == "right") {
    stepperX.moveTo(stepperX.currentPosition() + 15 * deltaSteps);
    Serial.println("Command: RIGHT");
  }
  else if (cmd == "sethome") {
    stepperY.setCurrentPosition(0);
    stepperX.setCurrentPosition(0);
    Serial.println("Manual Homing: Current position set as (0,0).");
  }
  else if (cmd == "gohome") {
    stepperY.moveTo(0);
    stepperX.moveTo(0);
    Serial.println("Command: GOHOME, returning to home position (0,0).");
  }
  else if (cmd == "runtest") {
    testState = TEST_MOVE_TO_START;
    customStep = 0;
    loggingActive = true;
    // Print a CSV header so the Python side can pick it up
    Serial.println("timestamp_ms,hPos,vPos,xLidar,yLidar");
    Serial.println("Starting custom runtest sequence.");
  }
  else if (cmd == "emergencystop") {
    // Immediately stop everything
    stepperY.stop();
    stepperX.stop();
    testState = TEST_IDLE;
    loggingActive = false;
    Serial.println("EMERGENCY STOP!");
  }
  else {
    Serial.print("Unknown command: ");
    Serial.println(cmd);
  }
}

void setup() {
  Serial.begin(115200);
  yLidarSerial.begin(115200);
  xLidarSerial.begin(115200);
  stepperY.setMaxSpeed(1000);
  stepperY.setAcceleration(500);
  stepperX.setMaxSpeed(1000);
  stepperX.setAcceleration(500);
  stepperY.setCurrentPosition(0);
  stepperX.setCurrentPosition(0);
  Serial.println("Ready. Enter command (up, down, left, right, runtest, etc.)");
}

void loop() {
  // Read incoming command
  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    processCommand(cmd);
  }

  // Periodic sensor & position read
  unsigned long now = millis();
  if (now - lastSensorRead >= sensorInterval) {
    lastSensorRead = now;
    xLidarSerial.listen(); delay(2);
    uint16_t tmpX = readTFmini(xLidarSerial);
    if (tmpX) xLidarDistance = tmpX;
    yLidarSerial.listen(); delay(2);
    uint16_t tmpY = readTFmini(yLidarSerial);
    if (tmpY) yLidarDistance = tmpY;

    if (loggingActive) {
      // CSV data row
      Serial.print(now); Serial.print(',');
      Serial.print(stepperX.currentPosition()); Serial.print(',');
      Serial.print(stepperY.currentPosition()); Serial.print(',');
      Serial.print(xLidarDistance);     Serial.print(',');
      Serial.println(yLidarDistance);
    } else {
      // Regular verbose output
      Serial.print("Vert pos: "); Serial.print(stepperY.currentPosition());
      Serial.print(" | Hori pos: "); Serial.print(stepperX.currentPosition());
      Serial.print(" || XLidar: "); Serial.print(xLidarDistance);
      Serial.print(" | YLidar: "); Serial.println(yLidarDistance);
    }
  }

  // Run steppers & test-state machine
  stepperY.run();
  stepperX.run();

  if (testState == TEST_MOVE_TO_START) {
    if (customIsHorizontal[customStep]) stepperX.move(customMoveSteps[customStep]);
    else                              stepperY.move(customMoveSteps[customStep]);
    testState = TEST_SCAN_ROW;
  }
  else if (testState == TEST_SCAN_ROW) {
    if (stepperY.distanceToGo() == 0 && stepperX.distanceToGo() == 0) {
      customStep++;
      if (customStep >= customTotalSteps) {
        testState = TEST_IDLE;
        loggingActive = false;
        Serial.println("Custom runtest sequence complete.");
      } else {
        testState = TEST_MOVE_TO_START;
      }
    }
  }
}
