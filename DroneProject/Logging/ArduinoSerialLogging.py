import csv
import time
from datetime import datetime
from pathlib import Path

import serial

# Configure serial connection
SERIAL_PORT = '/dev/cu.usbmodem101'  # Set this to the correct port on the target machine
BAUD_RATE = 115200
LOG_DIR = Path(__file__).resolve().parent / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
CSV_FILENAME = LOG_DIR / f'sensor_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'


def log_to_csv():
    ser = None
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        time.sleep(2)  # Give the device a moment after opening the port

        with open(CSV_FILENAME, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['timestamp_ms', 'hPos', 'vPos', 'xLidar', 'yLidar'])

            while True:
                raw_line = ser.readline().decode('utf-8', errors='replace').strip()
                if not raw_line or ',' not in raw_line or raw_line.startswith('timestamp_ms'):
                    continue

                data = [part.strip() for part in raw_line.split(',')]
                if len(data) != 5:
                    continue

                writer.writerow(data)
                csvfile.flush()
                print(f"Logged: {raw_line}")

    except KeyboardInterrupt:
        print(f"\nLogging stopped. Data saved to {CSV_FILENAME}")
    except serial.SerialException as exc:
        print(f"Serial error: {exc}")
    except Exception as exc:
        print(f"Error: {exc}")
    finally:
        if ser is not None and ser.is_open:
            ser.close()


if __name__ == "__main__":
    log_to_csv()
