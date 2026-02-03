#!/usr/bin/env python3
"""
Optimized Motor Controller for JetAcker with pre-activation
Eliminates delay between wheels
"""

import sys
import os
import time
import serial

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hiwonder_protocol import HiwonderProtocol

# Motor configuration
RIGHT_MOTOR_ID = 2
LEFT_MOTOR_ID = 4
LEFT_MOTOR_INVERTED = True

# Pre-activation threshold - speeds below this trigger pre-activation
PRE_ACTIVATE_THRESHOLD = 0.1  # RPS
PRE_ACTIVATE_SPEED = 0.01  # Tiny speed to wake up motors
PRE_ACTIVATE_DELAY = 0.1  # seconds


class MotorController:
    """
    Motor controller with automatic pre-activation to eliminate delays
    """

    def __init__(self, port='/dev/ttyACM0', baudrate=1000000):
        self.port = port
        self.baudrate = baudrate
        self.ser = None
        self.last_speeds = [0.0, 0.0]  # [right, left] in RPS
        self.motors_active = False

    def connect(self):
        """Open serial connection"""
        self.ser = serial.Serial(self.port, self.baudrate, timeout=1)
        self.ser.rts = False
        self.ser.dtr = False
        time.sleep(0.5)
        print(f"Connected to {self.port} at {self.baudrate} baud")

    def warm_up(self):
        """
        Warm up motors with small synchronized movements
        Call this once after connecting to eliminate cold-start delays
        """
        if not self.ser or not self.ser.is_open:
            raise RuntimeError("Serial port not open")

        print("Warming up motors...")

        # Send synchronized tiny movements to both motors
        # This ensures both motors are ready and responsive

        # Apply inversion for left motor
        left_wake = -PRE_ACTIVATE_SPEED if LEFT_MOTOR_INVERTED else PRE_ACTIVATE_SPEED
        right_wake = PRE_ACTIVATE_SPEED

        # Forward pulse
        cmd = HiwonderProtocol.motor_command([
            [RIGHT_MOTOR_ID, right_wake],
            [LEFT_MOTOR_ID, left_wake]
        ])
        self.ser.write(cmd)
        time.sleep(0.3)

        # Reverse pulse
        cmd = HiwonderProtocol.motor_command([
            [RIGHT_MOTOR_ID, -right_wake],
            [LEFT_MOTOR_ID, -left_wake]
        ])
        self.ser.write(cmd)
        time.sleep(0.3)

        # Stop and settle
        self.stop()
        time.sleep(0.2)

        # Mark motors as active (warm)
        self.motors_active = False  # Reset to allow pre-activation on first real command
        print("Motors warmed up and ready!")

    def disconnect(self):
        """Close serial connection and stop motors"""
        if self.ser and self.ser.is_open:
            self.stop()
            self.ser.close()
            print("Motor controller disconnected")

    def _send_command(self, right_rps, left_rps):
        """
        Send motor command with pre-activation if needed

        Args:
            right_rps: Right wheel speed in RPS (positive = forward)
            left_rps: Left wheel speed in RPS (positive = forward, will be inverted)
        """
        if not self.ser or not self.ser.is_open:
            raise RuntimeError("Serial port not open")

        # Apply left motor inversion
        if LEFT_MOTOR_INVERTED:
            left_rps = -left_rps

        # Check if we need pre-activation
        # Pre-activate if motors were stopped and now need significant speed
        need_preactivate = False
        if not self.motors_active:
            if abs(right_rps) > PRE_ACTIVATE_THRESHOLD or abs(left_rps) > PRE_ACTIVATE_THRESHOLD:
                need_preactivate = True

        if need_preactivate:
            # Send tiny speed to wake up motors
            wake_right = PRE_ACTIVATE_SPEED if right_rps > 0 else (-PRE_ACTIVATE_SPEED if right_rps < 0 else 0)
            wake_left = PRE_ACTIVATE_SPEED if left_rps > 0 else (-PRE_ACTIVATE_SPEED if left_rps < 0 else 0)

            if wake_right != 0 or wake_left != 0:
                cmd = HiwonderProtocol.motor_command([
                    [RIGHT_MOTOR_ID, wake_right],
                    [LEFT_MOTOR_ID, wake_left]
                ])
                self.ser.write(cmd)
                time.sleep(PRE_ACTIVATE_DELAY)

        # Send actual command
        cmd = HiwonderProtocol.motor_command([
            [RIGHT_MOTOR_ID, right_rps],
            [LEFT_MOTOR_ID, left_rps]
        ])
        self.ser.write(cmd)

        # Update state
        self.last_speeds = [right_rps, left_rps]
        self.motors_active = (abs(right_rps) > 0.001 or abs(left_rps) > 0.001)

    def set_wheel_speeds(self, right_rps, left_rps):
        """
        Set wheel speeds in rotations per second

        Args:
            right_rps: Right wheel RPS (positive = forward)
            left_rps: Left wheel RPS (positive = forward)
        """
        self._send_command(right_rps, left_rps)

    def set_velocity(self, linear_mps, angular_radps, track_width=0.133, wheel_diameter=0.067):
        """
        Set robot velocity using differential drive kinematics

        Args:
            linear_mps: Linear velocity in m/s (positive = forward)
            angular_radps: Angular velocity in rad/s (positive = counter-clockwise)
            track_width: Distance between wheels in meters
            wheel_diameter: Wheel diameter in meters
        """
        import math

        # Differential drive kinematics
        v_left_mps = linear_mps - angular_radps * track_width / 2.0
        v_right_mps = linear_mps + angular_radps * track_width / 2.0

        # Convert m/s to RPS
        wheel_circumference = math.pi * wheel_diameter
        left_rps = v_left_mps / wheel_circumference
        right_rps = v_right_mps / wheel_circumference

        self.set_wheel_speeds(right_rps, left_rps)

    def stop(self):
        """Stop all motors"""
        cmd = HiwonderProtocol.motor_command([
            [RIGHT_MOTOR_ID, 0],
            [LEFT_MOTOR_ID, 0]
        ])
        if self.ser and self.ser.is_open:
            self.ser.write(cmd)
        self.motors_active = False
        self.last_speeds = [0.0, 0.0]

    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()


# Simple test
if __name__ == '__main__':
    print("Testing Motor Controller with Pre-activation")
    print("="*70)

    with MotorController() as mc:
        print("\nTest 1: Forward")
        mc.set_wheel_speeds(0.5, 0.5)
        print("  Both wheels should start simultaneously!")
        time.sleep(3)

        print("\nTest 2: Stop")
        mc.stop()
        time.sleep(2)

        print("\nTest 3: Reverse")
        mc.set_wheel_speeds(-0.5, -0.5)
        print("  Both wheels should start simultaneously!")
        time.sleep(3)

        print("\nTest 4: Stop")
        mc.stop()
        time.sleep(2)

        print("\nTest 5: Turn in place")
        mc.set_wheel_speeds(0.5, -0.5)
        print("  Both wheels should start simultaneously!")
        time.sleep(3)

        print("\nTest 6: Final stop")
        mc.stop()

    print("\n" + "="*70)
    print("Test complete!")
