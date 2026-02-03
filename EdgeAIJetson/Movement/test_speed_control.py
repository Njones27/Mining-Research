#!/usr/bin/env python3
"""
Simple test: Does speed control work at all?
Tests extreme differences: 0.1 vs 1.0 vs 10.0 RPS
"""

import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from motor_controller import MotorController


def test_speed_control():
    """Test if speed values actually change motor speed"""

    print("="*70)
    print("SPEED CONTROL VERIFICATION TEST")
    print("="*70)
    print("\nThis tests 3 VERY different speeds:")
    print("  • 0.1 RPS  (super slow)")
    print("  • 1.0 RPS  (10x faster)")
    print("  • 10.0 RPS (100x faster than first!)")
    print("\nEach runs for 6 seconds - plenty of time to see difference")
    print("\nIf all 3 feel the SAME, motor speed control isn't working")
    print("If they feel DIFFERENT, speed control works!")
    print("\nStarting in 5 seconds...")
    time.sleep(5)

    with MotorController() as mc:
        mc.warm_up()
        time.sleep(2)

        # Test 1: Super slow
        print("\n" + "="*70)
        print("TEST 1: 0.1 RPS (SUPER SLOW)")
        print("="*70)
        print("Robot should barely crawl...")
        print("Watch how far it moves in 6 seconds!")
        time.sleep(2)
        mc.set_wheel_speeds(right_rps=0.1, left_rps=0.1)
        print("RUNNING... (mark starting position)")
        time.sleep(6)
        mc.stop()
        print("STOPPED - Note distance traveled!")
        time.sleep(4)

        # Test 2: Medium
        print("\n" + "="*70)
        print("TEST 2: 1.0 RPS (10x FASTER)")
        print("="*70)
        print("Should travel 10x farther than test 1!")
        print("If it travels the SAME distance, speed control broken!")
        time.sleep(2)
        mc.set_wheel_speeds(right_rps=1.0, left_rps=1.0)
        print("RUNNING... (should be obviously faster)")
        time.sleep(6)
        mc.stop()
        print("STOPPED - Compare to test 1 distance")
        time.sleep(4)

        # Test 3: Fast
        print("\n" + "="*70)
        print("TEST 3: 10.0 RPS (100x FASTER than test 1!)")
        print("="*70)
        print("Should travel 10x farther than test 2!")
        print("This should be VERY obviously faster!")
        time.sleep(2)
        mc.set_wheel_speeds(right_rps=10.0, left_rps=10.0)
        print("RUNNING... (should zoom!)")
        time.sleep(6)
        mc.stop()
        print("STOPPED - Much farther than tests 1 and 2?")

        print("\n" + "="*70)
        print("TEST COMPLETE - RESULTS")
        print("="*70)
        print("\nApproximate distances if working correctly:")
        print("  Test 1 (0.1 RPS): ~0.13 meters (5 inches)")
        print("  Test 2 (1.0 RPS): ~1.3 meters (4.3 feet)")
        print("  Test 3 (10.0 RPS): ~13 meters (43 feet!)")
        print("\nDid you see these HUGE differences?")
        print("  YES → Speed control works! (motors just have max speed)")
        print("  NO → Speed control broken (all same distance)")


if __name__ == '__main__':
    test_speed_control()
