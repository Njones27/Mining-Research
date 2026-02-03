#!/usr/bin/env python3
"""
Identify motor gear ratio by measuring actual RPM
Run with robot wheels OFF GROUND
"""
import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from motor_controller import MotorController

def identify_gear_ratio():
    print("="*70)
    print("MOTOR GEAR RATIO IDENTIFICATION TEST")
    print("="*70)
    print("\nThis test identifies which gear ratio motors you have:")
    print("  • 1:20 → 390 RPM (fast, low torque)")
    print("  • 1:30 → 280 RPM (moderate)")
    print("  • 1:60 → 146 RPM (good torque)")
    print("  • 1:90 → 85 RPM (high torque)")
    print("\n" + "="*70)
    print("PREPARATION:")
    print("="*70)
    print("1. ⚠️  LIFT ROBOT OFF GROUND (wheels must spin freely!)")
    print("2. Mark one wheel with tape/marker for visibility")
    print("3. Have stopwatch/timer ready")
    print("4. Position yourself to see marked wheel clearly")
    print("\nPress ENTER when ready...")
    input()

    with MotorController() as mc:
        mc.warm_up()

        print("\n" + "="*70)
        print("TEST STARTING IN 3 SECONDS!")
        print("="*70)
        print("\nGet ready to count rotations...")
        time.sleep(1)
        print("3...")
        time.sleep(1)
        print("2...")
        time.sleep(1)
        print("1...")
        time.sleep(1)
        print("\n" + "="*70)
        print("⚡ START COUNTING ROTATIONS NOW! ⚡")
        print("="*70)

        # Command maximum speed (1.0 RPS command)
        mc.set_wheel_speeds(right_rps=1.0, left_rps=1.0)

        # Run for exactly 10 seconds
        for i in range(10, 0, -1):
            print(f"  {i} seconds remaining...")
            time.sleep(1)

        mc.stop()
        print("\n" + "="*70)
        print("⛔ STOP COUNTING!")
        print("="*70)

    print("\nHow many complete rotations did you count?")
    print("(Estimate to nearest 0.5 rotation)")
    rotations = float(input("Enter number: "))

    rpm = rotations * 6  # Convert to rotations per minute
    print(f"\n{'='*70}")
    print(f"RESULTS")
    print(f"{'='*70}")
    print(f"Measured: {rotations} rotations in 10 seconds")
    print(f"Actual motor RPM: {rpm:.1f} RPM")
    print(f"\nComparison to specs:")
    print(f"  1:20 → 390 RPM rated (500 no-load)")
    print(f"  1:30 → 280 RPM rated (320 no-load)")
    print(f"  1:60 → 146 RPM rated (170 no-load)")
    print(f"  1:90 → 85 RPM rated (110 no-load)")
    print(f"\n{'='*70}")

    # Determine which ratio
    if rpm > 250:
        ratio = "1:20 or 1:30"
        torque = "LOW"
        recommendation = "❌ UPGRADE NEEDED"
        print(f"✓ You have {ratio} motors")
        print(f"  Speed: HIGH")
        print(f"  Torque: {torque} (~1.0-1.2 kg·cm rated)")
        print(f"\n{recommendation} for heavy robot!")
        print(f"\nPROBLEM: Not enough torque for 3kg+ robot")
        print(f"SOLUTION: Order JGB37-520R60 or R90 motors")
        print(f"  • R60: 1.9 kg·cm torque, 146 RPM")
        print(f"  • R90: 2.6 kg·cm torque, 85 RPM (BEST for heavy loads)")
        print(f"\nEstimated cost: $60-80 for 2 motors")
    elif rpm > 120:
        ratio = "1:60"
        torque = "GOOD"
        recommendation = "✓ SHOULD WORK"
        print(f"✓ You have {ratio} motors")
        print(f"  Speed: MODERATE")
        print(f"  Torque: {torque} (1.9 kg·cm rated)")
        print(f"\n{recommendation} for your robot!")
        print(f"\nIf robot still doesn't move, check:")
        print(f"  1. Battery voltage (should be >11.5V)")
        print(f"  2. Mechanical friction (wheel bearings)")
        print(f"  3. Command scaling (try 1.0 RPS command)")
    else:
        ratio = "1:90"
        torque = "HIGH"
        recommendation = "✅ PERFECT"
        print(f"✓ You have {ratio} motors")
        print(f"  Speed: SLOW but sufficient")
        print(f"  Torque: {torque} (2.6 kg·cm rated, 15 kg·cm stall)")
        print(f"\n{recommendation} for heavy robot!")
        print(f"\nIf robot doesn't move, problem is NOT motors:")
        print(f"  • Check battery voltage")
        print(f"  • Check mechanical friction")
        print(f"  • Check command scaling")

    # Calculate theoretical max speed
    wheel_diameter = 0.067  # meters
    wheel_circumference = 3.14159 * wheel_diameter
    max_speed_mps = (rpm / 60) * wheel_circumference

    print(f"\n{'='*70}")
    print(f"PERFORMANCE ESTIMATE")
    print(f"{'='*70}")
    print(f"With 67mm wheels:")
    print(f"  Max speed: {max_speed_mps:.2f} m/s ({max_speed_mps * 3.6:.1f} km/h)")
    print(f"  Suitable for: ", end='')
    if max_speed_mps > 1.0:
        print("Fast navigation (indoor racing)")
    elif max_speed_mps > 0.5:
        print("Normal navigation (person-following ✓)")
    else:
        print("Slow navigation (precision tasks)")

    print(f"\n{'='*70}")
    print(f"NEXT STEPS")
    print(f"{'='*70}")
    if "UPGRADE" in recommendation:
        print("1. Order higher gear ratio motors (1:60 or 1:90)")
        print("2. While waiting: Run test_minimum_speed.py")
        print("3. Check if current motors work at max command")
    else:
        print("1. Run: python3 test_minimum_speed.py")
        print("2. Run: python3 test_voltage_sag.py")
        print("3. Check mechanical friction (spin wheels by hand)")

if __name__ == '__main__':
    identify_gear_ratio()
