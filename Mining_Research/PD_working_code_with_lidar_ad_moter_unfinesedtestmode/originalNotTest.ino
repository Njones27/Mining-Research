#include <AccelStepper.h>
#include <SoftwareSerial.h>

// ===== Pin Definitions =====
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
SoftwareSerial yLidarSerial(YLIDAR_RX_PIN, YLIDAR_TX_PIN);
SoftwareSerial xLidarSerial(XLIDAR_RX_PIN, XLIDAR_TX_PIN);

// ===== Global Variables =====
const int deltaSteps = 500L;
uint16_t xLidarDistance = 0;
uint16_t yLidarDistance = 0;
unsigned long lastSensorRead = 0;
const unsigned long sensorInterval = 100;

// ===== Test Scanning State Machine =====
enum TestState {
  TEST_IDLE,
  TEST_MOVE_TO_START,
  TEST_SCAN_ROW
};
TestState testState = TEST_IDLE;

int customStep = 0;
const int customTotalSteps = 9;
long customMoveSteps[] = {
   220L * deltaSteps, // left
   20L * deltaSteps,  // down
   -220L * deltaSteps, // right
   20L * deltaSteps,  // down
   220L * deltaSteps, // left
   20L * deltaSteps,  // down
   -220L * deltaSteps, // right
   20L * deltaSteps,  // down
   220L * deltaSteps  // left
};
bool customIsHorizontal[] = {
  true, false, true, false, true, false, true, false, true
};

// ===== LiDAR Reading Function =====
uint16_t readTFmini(SoftwareSerial &lidarSerial) {
  uint16_t distance = 0;
  const uint8_t frameLength = 9;

  if (lidarSerial.available() >= frameLength) {
    while (lidarSerial.available()) {
      int byte1 = lidarSerial.read();
      if (byte1 == 0x59) {
        if (lidarSerial.available()) {
          int byte2 = lidarSerial.read();
          if (byte2 == 0x59) {
            uint8_t frame[frameLength];
            frame[0] = 0x59;
            frame[1] = 0x59;
            for (int i = 2; i < frameLength; i++) {
              while (!lidarSerial.available()) {}
              frame[i] = lidarSerial.read();
            }
            uint8_t checksum = 0;
            for (int i = 0; i < 8; i++) {
              checksum += frame[i];
            }
            if (checksum == frame[8]) {
              distance = frame[2] + ((uint16_t)frame[3] << 8);
              return distance;
            }
          }
        }
      }
    }
  }
  return distance;
}

// ===== Command Processor =====
void processCommand(String cmd) {
  cmd.trim();
  cmd.toLowerCase();

  if (testState != TEST_IDLE) {
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
  else if (cmd == "up_right") {
    stepperY.moveTo(stepperY.currentPosition() - 15 * deltaSteps);
    stepperX.moveTo(stepperX.currentPosition() + 15 * deltaSteps);
    Serial.println("Command: UP_RIGHT");
  }
  else if (cmd == "up_left") {
    stepperY.moveTo(stepperY.currentPosition() - 15 * deltaSteps);
    stepperX.moveTo(stepperX.currentPosition() - 15 * deltaSteps);
    Serial.println("Command: UP_LEFT");
  }
  else if (cmd == "down_right") {
    stepperY.moveTo(stepperY.currentPosition() + 15 * deltaSteps);
    stepperX.moveTo(stepperX.currentPosition() + 15 * deltaSteps);
    Serial.println("Command: DOWN_RIGHT");
  }
  else if (cmd == "down_left") {
    stepperY.moveTo(stepperY.currentPosition() + 15 * deltaSteps);
    stepperX.moveTo(stepperX.currentPosition() - 15 * deltaSteps);
    Serial.println("Command: DOWN_LEFT");
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
    Serial.println("Starting custom runtest sequence.");
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
  stepperY.setCurrentPosition(0);

  stepperX.setMaxSpeed(1000);
  stepperX.setAcceleration(500);
  stepperX.setCurrentPosition(0);

  Serial.println("Ready. Enter command (up, down, left, right, etc.)");
}

void loop() {
  if (Serial.available() > 0) {
    String input = Serial.readStringUntil('\n');
    input.trim();
    if (input.length() > 0) {
      processCommand(input);
    }
  }

  unsigned long currentMillis = millis();
  if (currentMillis - lastSensorRead >= sensorInterval) {
    lastSensorRead = currentMillis;

    xLidarSerial.listen();
    delay(2);
    uint16_t tempX = readTFmini(xLidarSerial);
    if (tempX != 0) xLidarDistance = tempX;

    yLidarSerial.listen();
    delay(2);
    uint16_t tempY = readTFmini(yLidarSerial);
    if (tempY != 0) yLidarDistance = tempY;

    Serial.print("Vert pos: ");
    Serial.print(stepperY.currentPosition());
    Serial.print(" | Hori pos: ");
    Serial.print(stepperX.currentPosition());
    Serial.print(" || XLidar: ");
    Serial.print(xLidarDistance);
    Serial.print(" | YLidar: ");
    Serial.println(yLidarDistance);
  }

  stepperY.run();
  stepperX.run();

  // Non-blocking custom runtest state machine
  if (testState == TEST_MOVE_TO_START) {
    if (customIsHorizontal[customStep]) {
      stepperX.move(customMoveSteps[customStep]);
    } else {
      stepperY.move(customMoveSteps[customStep]);
    }
    testState = TEST_SCAN_ROW;
  }
  else if (testState == TEST_SCAN_ROW) {
    if (stepperY.distanceToGo() == 0 && stepperX.distanceToGo() == 0) {
      customStep++;
      if (customStep >= customTotalSteps) {
        testState = TEST_IDLE;
        Serial.println("Custom runtest sequence complete.");
      } else {
        testState = TEST_MOVE_TO_START;
      }
    }
  }
}
