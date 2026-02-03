#!/usr/bin/env python3
"""
JetAcker Motor Control Test with Pre-Activation
Now using MotorController class for synchronized wheel movements
"""

import sys
import time
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from motor_controller import MotorController


def test_motors():
    """Test motor control with pre-activation (eliminates wheel delay)"""

    print("="*70)
    print("JETACKER MOTOR CONTROL TEST")
    print("="*70)
    print("\nConfiguration:")
    print("  Protocol: Hiwonder RRC (0xAA 0x55)")
    print("  Pre-activation: ENABLED ⭐")
    print("  Baud Rate: 1,000,000")
    print("\nPhysical Setup:")
    print("  LEFT wheel: M4 (inverted)")
    print("  RIGHT wheel: M2")
    print("\nFeatures:")
    print("  ✓ Automatic pre-activation (eliminates delay)")
    print("  ✓ Both wheels start simultaneously")
    print("  ✓ Motor inversion handled automatically")
    print("\nStarting in 3 seconds...")
    time.sleep(3)

    # Use MotorController with context manager
    with MotorController() as mc:
        try:
            # Initialization: Warm up motors to eliminate cold start
            print("\n" + "="*70)
            print("INITIALIZING MOTORS (Warm-up Phase)")
            print("="*70)
            print("Sending synchronized pulses to both motors...")
            print("This eliminates cold-start delay and ensures smooth operation.\n")

            # Warm up both motors simultaneously
            mc.warm_up()

            time.sleep(1)

            print("\n" + "="*70)
            print("STARTING MOTOR TESTS")
            print("="*70)

            # Test 1: Stop
            print("\n1. STOP (baseline)")
            mc.stop()
            time.sleep(2)

            # Test 2: Forward slow
            print("\n2. FORWARD SLOW (0.5 RPS)")
            print("   Both wheels should start SIMULTANEOUSLY!")
            mc.set_wheel_speeds(right_rps=0.5, left_rps=0.5)
            time.sleep(3)

            # Test 3: Stop
            print("\n3. STOP")
            mc.stop()
            time.sleep(2)

            # Test 4: Forward faster
            print("\n4. FORWARD FASTER (1.0 RPS)")
            print("   Both wheels should start SIMULTANEOUSLY!")
            mc.set_wheel_speeds(right_rps=1.0, left_rps=1.0)
            time.sleep(3)

            # Test 5: Stop
            print("\n5. STOP")
            mc.stop()
            time.sleep(2)

            # Test 6: Reverse
            print("\n6. REVERSE (-0.5 RPS)")
            print("   Both wheels should start SIMULTANEOUSLY!")
            mc.set_wheel_speeds(right_rps=-0.5, left_rps=-0.5)
            time.sleep(3)

            # Test 7: Stop
            print("\n7. STOP")
            mc.stop()
            time.sleep(2)

            # Test 8: Turn left (right forward, left backward)
            print("\n8. TURN LEFT")
            print("   Right: +0.5 RPS (forward)")
            print("   Left:  -0.5 RPS (backward)")
            print("   Both wheels should start SIMULTANEOUSLY!")
            mc.set_wheel_speeds(right_rps=0.5, left_rps=-0.5)
            time.sleep(3)

            # Test 9: Stop
            print("\n9. STOP")
            mc.stop()
            time.sleep(2)

            # Test 10: Turn right (left forward, right backward)
            print("\n10. TURN RIGHT")
            print("   Right: -0.5 RPS (backward)")
            print("   Left:  +0.5 RPS (forward)")
            print("   Both wheels should start SIMULTANEOUSLY!")
            mc.set_wheel_speeds(right_rps=-0.5, left_rps=0.5)
            time.sleep(3)

            # Test 11: Stop
            print("\n11. STOP")
            mc.stop()
            time.sleep(2)

            # Test 12: Using velocity API (m/s and rad/s)
            print("\n12. VELOCITY API TEST")
            print("   Linear: 0.2 m/s forward")
            print("   Angular: 0.0 rad/s (straight)")
            mc.set_velocity(linear_mps=0.2, angular_radps=0.0)
            time.sleep(3)

            # Test 13: Turn using velocity
            print("\n13. VELOCITY TURN TEST")
            print("   Linear: 0.1 m/s")
            print("   Angular: 0.5 rad/s (turning)")
            mc.set_velocity(linear_mps=0.1, angular_radps=0.5)
            time.sleep(3)

            # Final stop
            print("\n14. FINAL STOP")
            mc.stop()

            print("\n" + "="*70)
            print("TEST COMPLETE!")
            print("="*70)
            print("\n✅ Key Observations:")
            print("  • Did both wheels start at the same time?")
            print("  • Was there any 1-2 second delay?")
            print("  • Did pre-activation eliminate the delay?")
            print("\nPre-activation parameters:")
            print("  • Wake-up speed: 0.01 RPS")
            print("  • Delay: 0.1 seconds")
            print("  • Threshold: 0.1 RPS")

        except KeyboardInterrupt:
            print("\n\n🛑 EMERGENCY STOP")
            mc.stop()

    # MotorController automatically disconnects when exiting 'with' block
    print("\nMotor controller disconnected")


if __name__ == '__main__':
    test_motors()
