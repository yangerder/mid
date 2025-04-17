# -*- coding: utf-8 -*-
import smbus2
import time
import struct
import math
import RPi.GPIO as GPIO

# === GPIO setup ===
LED_PIN = 12  # Ensure this matches your wiring
GPIO.setmode(GPIO.BOARD)  # Changed from GPIO.BCM to GPIO.BOARD
GPIO.setup(LED_PIN, GPIO.OUT)
GPIO.output(LED_PIN, GPIO.LOW)

# === ICM20948 setup ===
ICM20948_ADDR = 0x68
bus = smbus2.SMBus(1)
REG_BANK_SEL = 0x7F

def select_bank(bank):
    bus.write_byte_data(ICM20948_ADDR, REG_BANK_SEL, bank << 4)

ACCEL_XOUT_H = 0x2D
GYRO_XOUT_H = 0x33
WHO_AM_I = 0x00

def read_i2c_word(reg):
    high = bus.read_byte_data(ICM20948_ADDR, reg)
    low = bus.read_byte_data(ICM20948_ADDR, reg + 1)
    return struct.unpack('>h', bytes([high, low]))[0]

def initialize_icm20948():
    select_bank(0)
    whoami = bus.read_byte_data(ICM20948_ADDR, WHO_AM_I)
    if whoami != 0xEA:
        print(f"Unexpected WHO_AM_I: {hex(whoami)}")
    else:
        print("ICM20948 detected")
    bus.write_byte_data(ICM20948_ADDR, 0x06, 0x01)

initialize_icm20948()

# === Settings ===
acc_offset_x = 0.02
gyro_offset_z = 0.8
dt = 1.0
FALL_THRESHOLD_G = 1.5
REQUIRED_FALL_COUNT = 1

velocity = 0.0
distance = 0.0
angle = 0.0
fall_count = 0  # Consecutive fall detection counter

try:
    while True:
        select_bank(0)

        # Read raw sensor data
        acc_x_raw = read_i2c_word(ACCEL_XOUT_H)
        acc_y_raw = read_i2c_word(ACCEL_XOUT_H + 2)
        acc_z_raw = read_i2c_word(ACCEL_XOUT_H + 4)
        gyro_z_raw = read_i2c_word(GYRO_XOUT_H + 4)

        # Convert acceleration
        acc_x_g = acc_x_raw / 16384.0
        acc_y_g = acc_y_raw / 16384.0
        acc_z_g = acc_z_raw / 16384.0
        acc_x_ms2 = (acc_x_g - acc_offset_x) * 9.81

        # Convert gyro
        gyro_z_dps = gyro_z_raw / 131.0
        gyro_z_calibrated = gyro_z_dps - gyro_offset_z

        # Calculate distance and angle
        velocity += acc_x_ms2 * dt
        distance += velocity * dt + 0.5 * acc_x_ms2 * dt * dt
        angle += gyro_z_calibrated * dt

        # Total acceleration
        total_acc = math.sqrt(acc_x_g**2 + acc_y_g**2 + acc_z_g**2)

        # Fall detection with duration check
        if total_acc > FALL_THRESHOLD_G:
            fall_count += 1
        else:
            fall_count = 0

        if fall_count >= REQUIRED_FALL_COUNT:
            print("Fallen occurred")  # Print message when fall is detected
            GPIO.output(LED_PIN, GPIO.HIGH)  # Turn LED on
            time.sleep(2)  # Keep LED on for 2 seconds
            GPIO.output(LED_PIN, GPIO.LOW)  # Turn LED off after 2 seconds

        # Output sensor readings
        print(f"Acc: ({acc_x_g:.3f}, {acc_y_g:.3f}, {acc_z_g:.3f}) G | Total: {total_acc:.2f} G")
        print(f"Velocity: {velocity:.2f} m/s | Distance: {distance:.2f} m")
        print(f"Gyro Z: {gyro_z_dps:.2f} deg/s | Angle: {angle:.2f} deg")
        print("-" * 60)

        time.sleep(dt)

except KeyboardInterrupt:
    print("Stopped.")
finally:
    GPIO.output(LED_PIN, GPIO.LOW)  # Ensure LED turns off on exit
    GPIO.cleanup()
