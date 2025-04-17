import time
import math
import RPi.GPIO as GPIO
from smbus2 import SMBus
from struct import unpack


I2C_ADDR = 0x68
ICM20948_ACCEL_XOUT_H = 0x2D
ICM20948_PWR_MGMT_1 = 0x06
CHIP_ID = 0xEA


LED_PIN = 18
GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN, GPIO.OUT)


bus = SMBus(1)

def read_accelerometer():

    data = bus.read_i2c_block_data(I2C_ADDR, ICM20948_ACCEL_XOUT_H, 6)
    ax, ay, az = unpack(">hhh", bytearray(data))


    ax /= 16384.0
    ay /= 16384.0
    az /= 16384.0

    return ax, ay, az

def calculate_angles(ax, ay, az):

    roll = math.degrees(math.atan2(ay, az))
    pitch = math.degrees(math.atan2(-ax, math.sqrt(ay**2 + az**2)))
    return roll, pitch

try:
    while True:
        ax, ay, az = read_accelerometer()
        roll, pitch = calculate_angles(ax, ay, az)
        print(f"Roll: {roll:.2f}, Pitch: {pitch:.2f}")


        if abs(roll) < 10 and abs(pitch) < 10:
            GPIO.output(LED_PIN, True)
        else:
            GPIO.output(LED_PIN, False)

        time.sleep(0.2)

except KeyboardInterrupt:
    GPIO.cleanup()
    print("end")
