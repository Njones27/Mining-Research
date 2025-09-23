//
// Created by Nathan Jones on 9/9/25.
//

#include "Movement.h"
#include <AccelStepper.h>

extern AccelStepper stepperY;
extern AccelStepper stepperX;
extern const long deltaSteps;

void Movement::moveYDown(int steps) {
    stepperY.moveTo(stepperY.currentPosition() + steps * deltaSteps);
    Serial.println("Command: DOWN");
}

void Movement::moveYUp(int steps) {
    stepperY.moveTo(stepperY.currentPosition() - steps * deltaSteps);
    Serial.println("Command: UP");
}

void Movement::moveXLeft(int steps) {
    stepperX.moveTo(stepperX.currentPosition() + steps * deltaSteps);
    Serial.println("Command: LEFT");
}

void Movement::moveXRight(int steps) {
    stepperX.moveTo(stepperX.currentPosition() - steps * deltaSteps);
    Serial.println("Command: RIGHT");
}
