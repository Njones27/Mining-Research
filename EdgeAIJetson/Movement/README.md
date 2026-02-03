# Hiwonder Motor Controller - JetAcker Robot

Complete motor control implementation for Hiwonder STM32 motor controller using RRC protocol.

## Overview

This implementation provides motor control for the Hiwonder JetAcker robot using the custom RRC (Remote Robot Control) protocol over serial communication. The code includes pre-activation to eliminate wheel startup delays and supports differential drive kinematics.

## Hardware Configuration

### Components
- **Motor Controller**: Hiwonder STM32-based controller board
- **Motors**: JGB37-520 DC geared motors with Hall encoders
  - Motor IDs: M2 (right wheel), M4 (left wheel, inverted)
  - Gear ratios available: 1:20, 1:30, 1:60, 1:90
  - Voltage: 12V nominal (6-14V range)
- **Battery**: 3S LiPo (11.1V - 12.6V)
  - Minimum: 2200mAh, 30C rating
  - **CRITICAL**: Motors MUST be powered by battery, not USB!
- **Communication**: USB serial (/dev/ttyACM0)
  - Baud rate: 1,000,000 (1 Mbaud)

### Physical Setup

```
Battery (12V) ──┬──> STM32 Motor Controller
                │      ├──> M2 (Right wheel)
                │      └──> M4 (Left wheel, inverted)
                │
                └──> Jetson (optional, or use wall power)

Jetson ──USB──> STM32 (serial communication only)
```

**IMPORTANT**:
- Battery powers the motors (provides 12V and high current)
- USB provides serial communication only (NOT motor power)
- Running motors on USB power (5V) will result in ~85% torque loss!

## Software Requirements

### Dependencies

```bash
# Python 3.x required
sudo apt-get install python3 python3-pip

# Install pyserial
pip3 install pyserial
```

### Permissions

```bash
# Add user to dialout group for serial access
sudo usermod -a -G dialout $USER

# Log out and log back in, then verify
groups | grep dialout

# Or use temporary permission
sudo chmod 666 /dev/ttyACM0
```

## File Descriptions

### Core Files (Required)

**hiwonder_protocol.py** - RRC Protocol Implementation
- Builds RRC frames with 0xAA 0x55 header
- Implements CRC-8 checksum
- Function codes:
  - `0x03`: Motor control
  - `0x05`: Bus servo control (not functional via serial)
  - `0x07`: IMU/telemetry streaming (STM32 sends continuously)

**motor_controller.py** - Motor Controller Class
- `MotorController` class with context manager support
- Key methods:
  - `set_wheel_speeds(right_rps, left_rps)` - Set wheel speeds in RPS
  - `set_velocity(linear_mps, angular_radps)` - Differential drive kinematics
  - `warm_up()` - Pre-activate motors to eliminate delays
  - `stop()` - Emergency stop
- Features:
  - Pre-activation (0.01 RPS pulse before actual command)
  - Automatic motor inversion (M4 left wheel)
  - Synchronized wheel startup (no 1-2 second delay)

### Test Files

**test_max_power.py** ⭐ **RECOMMENDED**
- Quick test at maximum effective power (1.0 RPS)
- Tests: Forward, Reverse, Spin Left, Spin Right
- Duration: ~20 seconds
- Use for: Quick verification that motors work

**test_motor_control.py**
- Comprehensive test of all motor functions
- Tests at 0.5 and 1.0 RPS
- Includes velocity API demonstration
- Duration: ~2 minutes
- Use for: First-time setup, debugging synchronization

### Diagnostic Files

**identify_motor_ratio.py**
- Identifies which gear ratio motors you have
- Measures actual RPM to determine: 1:20, 1:30, 1:60, or 1:90
- Requires: Robot wheels OFF GROUND
- Duration: ~1 minute

**test_minimum_speed.py**
- Finds minimum RPS command needed to move robot
- Tests speeds from 0.1 to 1.0 RPS incrementally
- Requires: Robot ON GROUND
- Duration: ~5 minutes

## Quick Start Guide

### 1. Hardware Setup

```bash
# Connect hardware:
1. Connect battery to STM32 power input (RED = +, BLACK = GND)
2. Connect motors to M2 (right) and M4 (left)
3. Connect STM32 to Jetson/computer via USB
4. Verify device appears: ls /dev/ttyACM*
```

### 2. Test Motor Control

```bash
# Navigate to directory with motor files
cd /path/to/jetacker_motor_tests

# Run maximum power test (recommended first test)
python3 test_max_power.py

# Or run comprehensive test
python3 test_motor_control.py
```

### 3. Expected Results

**✅ GOOD:**
- Both wheels start simultaneously (no delay)
- Robot moves forward/backward smoothly
- Strong, fast movements at 1.0 RPS

**⚠️ MARGINAL:**
- Wheels move but robot struggles
- Slow acceleration
- Check: Battery voltage, gear ratio, mechanical friction

**❌ POOR:**
- Wheels spin but robot doesn't move
- One wheel starts before the other (1-2 sec delay)
- Very weak/slow movement

### 4. Troubleshooting

**Problem: Wheels don't move at all**
```bash
# Check battery connection and voltage
# Battery should be 11.5V - 12.6V
# Verify motors are connected to M2 and M4
```

**Problem: One wheel starts 1-2 seconds before the other**
```bash
# Verify using motor_controller.py (has pre-activation)
# Old scripts without pre-activation will have delay
# Solution: Always use MotorController class
```

**Problem: Weak movement, can't push robot weight**
```bash
# Most likely causes:
1. Motors powered by USB instead of battery (check power connections!)
2. Battery voltage too low (charge to 12.6V)
3. Wrong gear ratio motors (run identify_motor_ratio.py)
```

**Problem: Serial permission denied**
```bash
sudo chmod 666 /dev/ttyACM0
# Or add user to dialout group (permanent fix)
```

## Motor Speed Specifications

### Command Range Discovery

Through testing, we discovered:
- **Effective range**: 0.0 - 1.0 RPS command
- **Motor response**: ~960 RPM at motor shaft (1.0 RPS command)
- **Commands above 1.0 RPS**: No additional speed increase (motors already maxed)

### Speed Conversions

For 67mm diameter wheels:

| RPS Command | Motor RPM | Linear Speed | Notes |
|-------------|-----------|--------------|-------|
| 0.1 | ~96 RPM | 0.02 m/s | Very slow |
| 0.3 | ~288 RPM | 0.06 m/s | Slow, controlled |
| 0.5 | ~480 RPM | 0.11 m/s | Moderate |
| 0.7 | ~672 RPM | 0.15 m/s | Fast |
| 1.0 | ~960 RPM | 0.21 m/s | Maximum effective |
| 2.0+ | ~960 RPM | 0.21 m/s | Same as 1.0 (no increase) |

### Gear Ratio Specifications

JGB37-520 motor variants (verify yours with identify_motor_ratio.py):

| Model | Ratio | Rated RPM | Torque (Rated) | Torque (Stall) | Best For |
|-------|-------|-----------|----------------|----------------|----------|
| R20 | 1:20 | 390 RPM | 1.0 kg·cm | 3.7 kg·cm | Light robots (<1kg) |
| R30 | 1:30 | 280 RPM | 1.2 kg·cm | 5.8 kg·cm | Light robots (1-2kg) |
| R60 | 1:60 | 146 RPM | 1.9 kg·cm | 9.2 kg·cm | Medium robots (2-3kg) ✓ |
| R90 | 1:90 | 85 RPM | 2.6 kg·cm | 15 kg·cm | Heavy robots (3-5kg) ✓✓ |

**For 3.1kg JetAcker robot**: Requires ~4.6 kg·cm torque per wheel
- ❌ 1:20 or 1:30 motors: INSUFFICIENT torque
- ✅ 1:60 motors: ADEQUATE (marginal)
- ✅✅ 1:90 motors: IDEAL (plenty of headroom)

## Configuration Details

### Motor Parameters

Edit in `motor_controller.py` if needed:

```python
# Motor IDs (don't change unless wiring is different)
RIGHT_MOTOR_ID = 2          # M2 port
LEFT_MOTOR_ID = 4           # M4 port
LEFT_MOTOR_INVERTED = True  # M4 is inverted

# Pre-activation settings (tuned, usually don't need to change)
PRE_ACTIVATE_THRESHOLD = 0.1  # RPS - activate below this speed
PRE_ACTIVATE_SPEED = 0.01     # RPS - tiny pulse to wake motors
PRE_ACTIVATE_DELAY = 0.1      # seconds - delay after activation

# Serial settings
DEFAULT_SERIAL_PORT = '/dev/ttyACM0'
DEFAULT_BAUD_RATE = 1000000   # 1 Mbaud
```

### Differential Drive Parameters

For ROS2 integration or custom velocity control:

```python
# Robot physical dimensions (adjust if different)
TRACK_WIDTH = 0.133    # meters - distance between wheels
WHEEL_DIAMETER = 0.067 # meters - wheel diameter

# Velocity limits (based on 1.0 RPS max)
MAX_LINEAR_VELOCITY = 0.21   # m/s
MAX_ANGULAR_VELOCITY = 3.16  # rad/s (1.0 RPS on both wheels, opposite directions)
```

## Usage Examples

### Basic Motor Control

```python
from motor_controller import MotorController

# Context manager (recommended - auto cleanup)
with MotorController() as mc:
    mc.warm_up()  # Pre-activate motors

    # Forward at max speed
    mc.set_wheel_speeds(1.0, 1.0)
    time.sleep(2)

    # Stop
    mc.stop()

# Manual control
mc = MotorController()
mc.connect()
mc.set_wheel_speeds(0.5, 0.5)
mc.disconnect()
```

### Differential Drive Control

```python
from motor_controller import MotorController

with MotorController() as mc:
    mc.warm_up()

    # Forward at 0.2 m/s
    mc.set_velocity(linear_mps=0.2, angular_radps=0.0)
    time.sleep(2)

    # Turn while moving forward (0.1 m/s, 0.5 rad/s)
    mc.set_velocity(linear_mps=0.1, angular_radps=0.5)
    time.sleep(2)

    # Spin in place (0 linear, max angular)
    mc.set_velocity(linear_mps=0.0, angular_radps=2.0)
    time.sleep(2)

    mc.stop()
```

### Direct RRC Protocol

```python
from hiwonder_protocol import HiwonderProtocol
import serial

ser = serial.Serial('/dev/ttyACM0', 1000000, timeout=0.1)

# Build motor command for M2 at 1.0 RPS
# Format: [motor_id, direction, speed_low, speed_high]
# Speed value: RPS * 1000 (e.g., 1.0 RPS = 1000)
speed_value = int(1.0 * 1000)
data = [
    2,  # Motor ID (M2)
    0,  # Direction: 0=forward, 1=reverse
    speed_value & 0xFF,        # Speed low byte
    (speed_value >> 8) & 0xFF  # Speed high byte
]

frame = HiwonderProtocol.build_frame(0x03, data)  # 0x03 = motor control
ser.write(frame)
ser.close()
```

## ROS2 Integration

For ROS2 cmd_vel integration, see `jetacker_driver_node_v2.py`:

```bash
# Run ROS2 driver node
ros2 run jetacker_motor_tests jetacker_driver_node_v2

# Publish velocity commands
ros2 topic pub /cmd_vel geometry_msgs/msg/Twist \
  "{linear: {x: 0.2, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}"
```

## Known Limitations

1. **Servo control doesn't work** - STM32 firmware doesn't support servo commands via serial
   - Workaround: Use PWM servos with different controller (e.g., Yahboom board)

2. **Speed limited to 1.0 RPS** - Commands above 1.0 RPS don't increase speed
   - Motor firmware limits or hardware governor
   - Maximum linear speed: ~0.21 m/s (0.76 km/h)

3. **Telemetry interference** - STM32 continuously streams IMU data (function 0x07)
   - Can cause serial buffer overflow and board "buzzing"
   - Solution: Use jetacker_driver_node_v2.py with background telemetry reader

4. **No odometry feedback** - Motors have Hall encoders but STM32 doesn't report encoder values
   - Current implementation: Open-loop control only
   - Future: May need to reverse-engineer encoder protocol

## Performance Optimization

### Pre-activation (Already Implemented)

Eliminates 1-2 second wheel startup delay:
- Sends 0.01 RPS "wake up" pulse before actual command
- Both wheels activate simultaneously
- No user action needed (built into MotorController class)

### Battery Health

For optimal performance:
- Voltage: 12.6V fully charged, >11.5V minimum
- C-rating: 30C or higher for adequate current delivery
- Capacity: 2200mAh minimum for 3kg robot
- Check voltage sag: Should be <10% under full load (use test_voltage_sag.py)

### Motor Selection

For heavy robots (3+ kg):
- Use 1:60 or 1:90 gear ratio motors
- Higher gear ratio = more torque, less speed
- 1:90 recommended for 3kg+ robots with good torque margin

## Testing Checklist

Before deployment, verify:

- [ ] Battery fully charged (12.6V)
- [ ] Battery connected to STM32 (not relying on USB power)
- [ ] Motors connected to M2 (right) and M4 (left)
- [ ] USB serial connection working (/dev/ttyACM0 exists)
- [ ] test_max_power.py runs successfully
- [ ] Both wheels start simultaneously (no delay)
- [ ] Robot can move on ground at 1.0 RPS
- [ ] Identified motor gear ratio (run identify_motor_ratio.py)
- [ ] Found minimum working speed (run test_minimum_speed.py)

## Support and Troubleshooting

### Common Issues

| Symptom | Likely Cause | Solution |
|---------|--------------|----------|
| No wheel movement | USB power only | Connect battery to STM32 |
| Weak movement | Low battery voltage | Charge battery to 12.6V |
| One wheel delays | Not using pre-activation | Use MotorController class |
| Robot can't move weight | Wrong gear ratio (1:20/1:30) | Upgrade to 1:60 or 1:90 motors |
| Serial permission error | User not in dialout group | `sudo usermod -a -G dialout $USER` |
| STM32 buzzing | Buffer overflow | Use jetacker_driver_node_v2.py |

### Diagnostic Procedure

1. **Test power**: Run test_max_power.py - Do wheels spin fast?
2. **Identify motors**: Run identify_motor_ratio.py - Which gear ratio?
3. **Test movement**: Run test_minimum_speed.py - Can robot move?
4. **Check battery**: Run test_voltage_sag.py - Voltage dropping too much?

## Hardware Migration Path

If current hardware limitations are blocking (no servo control, speed limits):

**Option A: Upgrade to Yahboom G1 Expansion Board**
- Cost: ~$60
- Features: 4-ch encoder motors, 4-ch PWM servos, MPU9250 IMU
- Benefits: Better ROS2 support, PWM servo control, more documentation
- Connection: USB serial (Jetson AGX Orin has no 40-pin GPIO)
- Timeline: 1-2 weeks setup

**Option B: Add PCA9685 for Servo Control**
- Cost: ~$10-15
- Keep current motor controller
- Add I2C PWM servo driver for steering
- Hybrid approach

See `nextStepsPlan.md` for detailed migration plan.

## Credits

Developed for Hiwonder JetAcker robot on Jetson AGX Orin
RRC Protocol reverse-engineered from Hiwonder documentation
Pre-activation technique developed through iterative testing

## License

Use freely for robotics projects. Attribution appreciated.

---

**Last Updated**: 2026-02-03
**Tested On**: Jetson AGX Orin, Hiwonder JetAcker, JGB37-520 motors
**Status**: Production ready for differential drive applications
