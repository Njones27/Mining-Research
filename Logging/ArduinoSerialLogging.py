import serial
import csv
import time
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import threading
import os

# Configure serial connection
SERIAL_PORT = 'COM3' # TODO: Change this accordingly
BAUD_RATE = 115200
CSV_FILENAME = f'sensor_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'

# Create Graphs directory if it doesn't exist
GRAPHS_DIR = 'Graphs'
os.makedirs(GRAPHS_DIR, exist_ok=True)

def generate_chart():
    """Generate a real-time chart from CSV data"""
    try:
        df = pd.read_csv(CSV_FILENAME)
        if len(df) < 2:
            return

        plt.clf()

        # Create subplots
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 8))

        # Position trajectory (X-Y plot)
        ax1.plot(df['hPos'], df['vPos'], 'b-', alpha=0.7)
        ax1.scatter(df['hPos'].iloc[-1], df['vPos'].iloc[-1], color='red', s=50)
        ax1.set_xlabel('Horizontal Position')
        ax1.set_ylabel('Vertical Position')
        ax1.set_title('Movement Trajectory')
        ax1.grid(True)

        # Lidar distances over time
        time_sec = df['timestamp_ms'] / 1000
        ax2.plot(time_sec, df['xLidar'], 'r-', label='X Lidar', linewidth=2)
        ax2.plot(time_sec, df['yLidar'], 'g-', label='Y Lidar', linewidth=2)
        ax2.set_xlabel('Time (seconds)')
        ax2.set_ylabel('Distance (mm)')
        ax2.set_title('Lidar Readings')
        ax2.legend()
        ax2.grid(True)

        # Position vs Lidar correlation
        ax3.scatter(df['hPos'], df['xLidar'], alpha=0.6, c='red', label='H-Pos vs X-Lidar')
        ax3.set_xlabel('Horizontal Position')
        ax3.set_ylabel('X Lidar Distance')
        ax3.set_title('Position-Distance Correlation')
        ax3.grid(True)

        # 3D surface map (if enough data points)
        if len(df) > 10:
            scatter = ax4.scatter(df['hPos'], df['vPos'], c=df['xLidar'], cmap='viridis', alpha=0.7)
            ax4.set_xlabel('Horizontal Position')
            ax4.set_ylabel('Vertical Position')
            ax4.set_title('Distance Heatmap')
            plt.colorbar(scatter, ax=ax4, label='X Lidar Distance')

        plt.tight_layout()
        chart_path = os.path.join(GRAPHS_DIR, f'chart_{datetime.now().strftime("%H%M%S")}.png')
        plt.savefig(chart_path, dpi=150)
        plt.pause(0.1)

    except Exception as e:
        print(f"Chart error: {e}")


def log_to_csv():
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        time.sleep(2)

        with open(CSV_FILENAME, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['timestamp_ms', 'hPos', 'vPos', 'xLidar', 'yLidar'])

            chart_timer = 0
            while True:
                line = ser.readline().decode('utf-8').strip()
                if line and ',' in line and not line.startswith('timestamp_ms'):
                    data = line.split(',')
                    if len(data) == 5:
                        writer.writerow(data)
                        csvfile.flush()
                        print(f"Logged: {line}")

                        # Generate chart every 50 data points
                        chart_timer += 1
                        if chart_timer >= 50:
                            threading.Thread(target=generate_chart, daemon=True).start()
                            chart_timer = 0

    except KeyboardInterrupt:
        print(f"\nLogging stopped. Generating final chart...")
        generate_chart()
        plt.show()
        print(f"Data saved to {CSV_FILENAME}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'ser' in locals():
            ser.close()


if __name__ == "__main__":
    plt.ion()  # Enable interactive mode
    log_to_csv()
