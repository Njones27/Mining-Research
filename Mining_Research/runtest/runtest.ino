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
long deltaSteps = 500L;
uint16_t xLidarDistance = 0, yLidarDistance = 0;
unsigned int lastSensorRead = 0;
const unsigned int sensorInterval = 100;

bool loggingActive = false;
bool autoRunning = false;

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

  // Auto-start logging and movement
  delay(3000);
  loggingActive = true;
  autoRunning = true;
  Serial.println("timestamp_ms,hPos,vPos,xLidar,yLidar");
  Serial.println("Starting automatic movement and logging.");
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
            loggingActive = false;
            Serial.println("EMERGENCY STOP!");
        }
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
            Serial.print(now); Serial.print(',');
            Serial.print(stepperX.currentPosition()); Serial.print(',');
            Serial.print(stepperY.currentPosition()); Serial.print(',');
            Serial.print(xLidarDistance); Serial.print(',');
            Serial.println(yLidarDistance);
        }
    }

    // Run steppers
    stepperY.run();
    stepperX.run();

//    // Single movement
//    static bool hasMoved = false;
//    if (autoRunning && !hasMoved && stepperY.distanceToGo() == 0) {
//        movement.moveYDown(10); // 10 steps = 1.25", so 1 step = 1/8"
//        hasMoved = true;
//        Serial.println("Test done");
//    }

    // Continuous movement
    static bool hasMoved = false;
    static int moveState = 0;

    if (autoRunning && !hasMoved && stepperY.distanceToGo() == 0 && stepperX.distanceToGo() == 0) {
        // 10 steps = 1.25", so 1 step = 1/8"
            switch (moveState) {
                // Left to right sweep
                case 0: movement.moveYDown(40); break;
                case 1: movement.moveXLeft(10); break;
                case 2: movement.moveYUp(40); break;
                case 3: movement.moveXLeft(10); break;
                case 4: movement.moveYDown(40); break;
                case 5: movement.moveXLeft(10); break;
                case 6: movement.moveYUp(40); break;
                case 7: movement.moveXLeft(10); break;
                case 8: movement.moveYDown(40); break;
                case 9: movement.moveXLeft(10); break;

                // Bottom to top sweep
                case 10: movement.moveYUp(10); break;
                case 11: movement.moveXRight(40); break;
                case 12: movement.moveYUp(10); break;
                case 13: movement.moveXLeft(40); break;
                case 14: movement.moveYUp(10); break;
                case 15: movement.moveXRight(40); break;
                case 16: movement.moveYUp(10); break;
                case 17: movement.moveXLeft(40); break;
                case 18: movement.moveYUp(10); break;
                case 19: movement.moveXRight(40); break;

                default:
                    hasMoved = true;
                    Serial.println("Test done");
                    return;
            }
            moveState++;
    }

}
