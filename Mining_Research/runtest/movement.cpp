//
// Created by Nathan Jones on 9/9/25.
//

#include "Movement.h"
#include <AccelStepper.h>

extern AccelStepper stepperY;
extern AccelStepper stepperX;
extern const long deltaSteps;

// Fast motion profile for snappy short moves
static inline void applyFastProfile(AccelStepper &s) {
    s.setMaxSpeed(4000);      // velocity (steps/s)
    s.setAcceleration(20000); // acceleration (steps/s^2)
}

void Movement::moveYDown(int steps)
{
    applyFastProfile(stepperY);
    long target = stepperY.currentPosition() + (long)steps * deltaSteps;
    stepperY.moveTo(target);
    Serial.println("Command: DOWN");
}

void Movement::moveYUp(int steps)
{
    applyFastProfile(stepperY);
    long target = stepperY.currentPosition() - (long)steps * deltaSteps;
    stepperY.moveTo(target);
    Serial.println("Command: UP");
}

void Movement::moveXLeft(int steps)
{
    applyFastProfile(stepperX);
    long target = stepperX.currentPosition() + (long)steps * deltaSteps;
    stepperX.moveTo(target);
    Serial.println("Command: LEFT");
}

void Movement::moveXRight(int steps)
{
    applyFastProfile(stepperX);
    long target = stepperX.currentPosition() - (long)steps * deltaSteps;
    stepperX.moveTo(target);
    Serial.println("Command: RIGHT");
}
