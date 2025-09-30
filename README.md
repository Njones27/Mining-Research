# Mining Research Motion Platform

This repository contains firmware and logging utilities for a lab-scale mining research platform that sweeps a lidar sensor array across a two-axis gantry. The code drives paired stepper motors with [AccelStepper](https://www.airspayce.com/mikem/arduino/AccelStepper/) motion control profiles and records positional and range data for later analysis.

## Repository structure

```
Mining_Research/
├── Classes/              # Reusable motion helper class shared by sketches
├── Logging/              # Python-based serial logger and CSV output
├── Reset/                # Tools for manually jogging the gantry to a start pose
└── runtest/              # Automated raster sweep sketch for endurance testing
```

## Firmware sketches

All Arduino sketches target an Uno-style board that drives X and Y stepper motors as well as dual TFmini-style lidar sensors over software serial. Both sketches expose a serial interface so you can issue emergency stop or jogging commands from a host PC.

### `runtest/runtest.ino`

* Configures the stepper drivers (DIR/STEP pins 6–9) and lidar serial connections (pins 2–5).【F:Mining_Research/runtest/runtest.ino†L1-L25】
* Automatically begins a continuous raster movement pattern across the test bed after a three-second start-up delay, using the `Movement` helper to queue coordinated moves.【F:Mining_Research/runtest/runtest.ino†L40-L109】
* Includes an emergency-stop command (`stop`) and optional lidar logging hooks that can be re-enabled for data collection.【F:Mining_Research/runtest/runtest.ino†L51-L88】

### `Reset/startPosition/startPosition.ino`

* Shares the same hardware pinout as the automated test sketch but keeps motion manual by listening for `up`, `down`, `left`, and `right` serial commands before queuing a move.【F:Mining_Research/Reset/startPosition/startPosition.ino†L1-L68】
* Useful for homing the gantry or recovering from an emergency stop without running the full raster pattern.

Both sketches rely on the `Movement` class (defined in `Classes/Movement.h` and implemented in `Classes/movement.cpp`) to apply a fast motion profile and emit human-readable serial messages whenever a move is commanded.【F:Mining_Research/Classes/movement.cpp†L1-L39】

## Data logging utility

The `Logging/ArduinoSerialLogging.py` script captures telemetry streamed over USB and appends it to timestamped CSV files under `Logging/logs/`. It expects the Arduino sketch to emit comma-separated records in the order `timestamp_ms,hPos,vPos,xLidar,yLidar` and prints each line as it is saved for easy monitoring.【F:Mining_Research/Logging/ArduinoSerialLogging.py†L1-L40】

Update the `SERIAL_PORT` constant to match the port name on your machine before running the logger with:

```bash
python -m pip install -r requirements.txt  # Ensure pyserial is available
python Logging/ArduinoSerialLogging.py
```

(If a requirements file is not present, install `pyserial` manually.)

## Getting started

1. **Install dependencies**
   * Arduino IDE with the AccelStepper and SoftwareSerial libraries available.
   * Python 3.9+ with `pyserial` for optional logging.
2. **Wire the hardware** according to the pin definitions in each sketch (stepper drivers on pins 6–9, lidar sensors on pins 2–5).【F:Mining_Research/runtest/runtest.ino†L5-L24】
3. **Upload a sketch**
   * Use `runtest/runtest.ino` for automated raster sweeps.
   * Use `Reset/startPosition/startPosition.ino` when you need manual jogging control before a test.
4. **Monitor serial output** using the Arduino Serial Monitor or the provided Python logger. Issue `stop` to halt motion immediately if needed.
5. **Collect data** by re-enabling the commented lidar logging block in `runtest.ino` and running the Python logger to save CSV files for analysis.【F:Mining_Research/runtest/runtest.ino†L70-L89】【F:Mining_Research/Logging/ArduinoSerialLogging.py†L18-L39】

## Contributing

Pull requests that improve documentation, add calibration routines, or integrate additional sensors are welcome. Please follow the existing folder layout and keep hardware pin definitions centralized so downstream users can swap in their own motion profiles easily.

