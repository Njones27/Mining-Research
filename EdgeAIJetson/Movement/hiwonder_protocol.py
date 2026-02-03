#!/usr/bin/env python3
"""
Hiwonder RRC Protocol Implementation
Based on ros_robot_controller_sdk.py from MentorPi
"""

import struct

# CRC-8 lookup table for Hiwonder protocol
CRC8_TABLE = [
    0, 94, 188, 226, 97, 63, 221, 131, 194, 156, 126, 32, 163, 253, 31, 65,
    157, 195, 33, 127, 252, 162, 64, 30, 95, 1, 227, 189, 62, 96, 130, 220,
    35, 125, 159, 193, 66, 28, 254, 160, 225, 191, 93, 3, 128, 222, 60, 98,
    190, 224, 2, 92, 223, 129, 99, 61, 124, 34, 192, 158, 29, 67, 161, 255,
    70, 24, 250, 164, 39, 121, 155, 197, 132, 218, 56, 102, 229, 187, 89, 7,
    219, 133, 103, 57, 186, 228, 6, 88, 25, 71, 165, 251, 120, 38, 196, 154,
    101, 59, 217, 135, 4, 90, 184, 230, 167, 249, 27, 69, 198, 152, 122, 36,
    248, 166, 68, 26, 153, 199, 37, 123, 58, 100, 134, 216, 91, 5, 231, 185,
    140, 210, 48, 110, 237, 179, 81, 15, 78, 16, 242, 172, 47, 113, 147, 205,
    17, 79, 173, 243, 112, 46, 204, 146, 211, 141, 111, 49, 178, 236, 14, 80,
    175, 241, 19, 77, 206, 144, 114, 44, 109, 51, 209, 143, 12, 82, 176, 238,
    50, 108, 142, 208, 83, 13, 239, 177, 240, 174, 76, 18, 145, 207, 45, 115,
    202, 148, 118, 40, 171, 245, 23, 73, 8, 86, 180, 234, 105, 55, 213, 139,
    87, 9, 235, 181, 54, 104, 138, 212, 149, 203, 41, 119, 244, 170, 72, 22,
    233, 183, 85, 11, 136, 214, 52, 106, 43, 117, 151, 201, 74, 20, 246, 168,
    116, 42, 200, 150, 21, 75, 169, 247, 182, 232, 10, 84, 215, 137, 107, 53
]

def checksum_crc8(data):
    """Calculate CRC-8 checksum for Hiwonder protocol"""
    check = 0
    for b in data:
        check = CRC8_TABLE[check ^ b]
    return check & 0x00FF


class HiwonderProtocol:
    """Hiwonder RRC Communication Protocol"""

    # Protocol constants
    FRAME_HEADER_1 = 0xAA
    FRAME_HEADER_2 = 0x55

    # Function codes
    FUNC_SYS = 0
    FUNC_LED = 1
    FUNC_BUZZER = 2
    FUNC_MOTOR = 3
    FUNC_PWM_SERVO = 4
    FUNC_BUS_SERVO = 5
    FUNC_KEY = 6
    FUNC_IMU = 7
    FUNC_GAMEPAD = 8
    FUNC_SBUS = 9
    FUNC_OLED = 10
    FUNC_RGB = 11

    @staticmethod
    def build_frame(function, data):
        """
        Build a complete Hiwonder RRC protocol frame

        Args:
            function: Function code (0-11)
            data: Data payload as list of bytes or bytearray

        Returns:
            bytes: Complete frame with header and checksum
        """
        frame = [HiwonderProtocol.FRAME_HEADER_1,
                 HiwonderProtocol.FRAME_HEADER_2,
                 int(function)]
        frame.append(len(data))
        frame.extend(data)
        frame.append(checksum_crc8(bytes(frame[2:])))
        return bytes(frame)

    @staticmethod
    def motor_command(speeds):
        """
        Create motor control command

        Args:
            speeds: List of [motor_id, rps] pairs
                   motor_id: 1-4 (physical motor ports)
                   rps: rotations per second (float, positive=forward)

        Returns:
            bytes: Complete motor command frame

        Example:
            # Move motors 2 and 4 at 0.5 RPS
            cmd = HiwonderProtocol.motor_command([[2, 0.5], [4, 0.5]])
        """
        data = [0x01, len(speeds)]  # Sub-command 0x01, motor count
        for motor_id, rps in speeds:
            data.append(int(motor_id - 1))  # Convert to 0-indexed
            data.extend(struct.pack("<f", float(rps)))  # Speed as float

        return HiwonderProtocol.build_frame(HiwonderProtocol.FUNC_MOTOR, data)

    @staticmethod
    def led_command(led_id, on_time, off_time, repeat=1):
        """Create LED control command"""
        on_time = int(on_time * 1000)
        off_time = int(off_time * 1000)
        data = struct.pack("<BHHH", led_id, on_time, off_time, repeat)
        return HiwonderProtocol.build_frame(HiwonderProtocol.FUNC_LED, data)

    @staticmethod
    def buzzer_command(freq, on_time, off_time, repeat=1):
        """Create buzzer control command"""
        on_time = int(on_time * 1000)
        off_time = int(off_time * 1000)
        data = struct.pack("<HHHH", freq, on_time, off_time, repeat)
        return HiwonderProtocol.build_frame(HiwonderProtocol.FUNC_BUZZER, data)

    @staticmethod
    def pwm_servo_command(duration, positions):
        """
        Create PWM servo control command

        Args:
            duration: Movement duration in seconds
            positions: List of [servo_id, position] pairs
                      servo_id: 1-4
                      position: PWM value (typically 500-2500)
        """
        duration = int(duration * 1000)
        data = [0x01, duration & 0xFF, 0xFF & (duration >> 8), len(positions)]
        for servo_id, position in positions:
            data.extend(struct.pack("<BH", servo_id, position))
        return HiwonderProtocol.build_frame(HiwonderProtocol.FUNC_PWM_SERVO, data)


# Utility functions
def meters_per_sec_to_rps(speed_mps, wheel_diameter=0.067):
    """Convert m/s to rotations per second"""
    import math
    return speed_mps / (math.pi * wheel_diameter)

def rps_to_meters_per_sec(rps, wheel_diameter=0.067):
    """Convert rotations per second to m/s"""
    import math
    return rps * math.pi * wheel_diameter
