//
// Created by Nathan Jones on 9/9/25.
//

#ifndef ARDUINO_MOVEMENT_H
#define ARDUINO_MOVEMENT_H


class Movement {
    public:
        void moveZDown(int steps);
        void moveYDown(int steps);
        void moveYUp(int steps);
        void moveXLeft(int steps);
        void moveXRight(int steps);
};


#endif //ARDUINO_MOVEMENT_H
