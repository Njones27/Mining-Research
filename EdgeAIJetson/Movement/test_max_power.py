#!/usr/bin/env python3
"""
Test motors at MAXIMUM POWER (1.0 RPS)
Simple test to verify motors can move robot at full command
"""

import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from motor_controller import MotorController


def test_max_power():
    """Test motors at maximum effective power (1.0 RPS)"""

    print("="*70)
    print("MAXIMUM POWER TEST")
    print("="*70)
    print("\nThis test runs motors at 1.0 RPS (maximum effective command)")
    print("\nREQUIREMENTS:")
    print("  ✓ Battery connected and charged (11.1V - 12.6V)")
    print("  ✓ Robot on GROUND (wheels touching surface)")
    print("  ✓ Clear area around robot")
    print("\nConfiguration:")
    print("  • Command: 1.0 RPS per wheel")
    print("  • Actual speed: ~960 RPM (16 RPS at motor shaft)")
    print("  • Left motor: M4 (inverted)")
    print("  • Right motor: M2")
    print("\nStarting in 3 seconds...")
    time.sleep(3)

    with MotorController() as mc:
        # Warm up
        print("\nWarming up motors...")
        mc.warm_up()
        time.sleep(1)

        print("\n" + "="*70)
        print("RUNNING MAXIMUM POWER TESTS")
        print("="*70)

        # Test 1: Forward max
        print("\n1. FORWARD at MAX (1.0 RPS)")
        print("   Both wheels should move FAST and SIMULTANEOUSLY")
        mc.set_wheel_speeds(1.0, 1.0)
        time.sleep(3)
        mc.stop()
        time.sleep(2)

        # Test 2: Reverse max
        print("\n2. REVERSE at MAX (-1.0 RPS)")
        mc.set_wheel_speeds(-1.0, -1.0)
        time.sleep(3)
        mc.stop()
        time.sleep(2)

        # Test 3: Spin right
        print("\n3. SPIN RIGHT at MAX")
        print("   Right: -1.0 RPS (backward)")
        print("   Left:  +1.0 RPS (forward)")
        mc.set_wheel_speeds(-1.0, 1.0)
        time.sleep(3)
        mc.stop()
        time.sleep(2)

        # Test 4: Spin left
        print("\n4. SPIN LEFT at MAX")
        print("   Right: +1.0 RPS (forward)")
        print("   Left:  -1.0 RPS (backward)")
        mc.set_wheel_speeds(1.0, -1.0)
        time.sleep(3)
        mc.stop()

        print("\n" + "="*70)
        print("TEST COMPLETE")
        print("="*70)
        print("\n✅ RESULTS TO CHECK:")
        print("  • Did robot move forward/backward?")
        print("  • Were movements strong and fast?")
        print("  • Did wheels start simultaneously (no delay)?")
        print("  • Any motor strain/noise?")
        print("\n📊 PERFORMANCE INDICATORS:")
        print("  ✓ GOOD: Robot moves smoothly, wheels synchronized")
        print("  ⚠ MARGINAL: Moves but struggles/slow acceleration")
        print("  ❌ POOR: Wheels spin but robot doesn't move")
        print("\nIf performance is POOR:")
        print("  → Check battery voltage (should be >11.5V)")
        print("  → Run identify_motor_ratio.py to check gear ratio")
        print("  → Check for mechanical friction (spin wheels by hand)")


if __name__ == '__main__':
    try:
        test_max_power()
    except KeyboardInterrupt:
        print("\n\n🛑 Emergency stop!")
