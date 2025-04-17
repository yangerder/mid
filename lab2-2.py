# -*- coding: utf-8 -*-
import smbus2
import time
import struct

ICM20948_ADDR = 0x68
bus = smbus2.SMBus(1)

# Register banks
REG_BANK_SEL = 0x7F

def select_bank(bank):
    bus.write_byte_data(ICM20948_ADDR, REG_BANK_SEL, bank << 4)

# Register map for Bank 0
ACCEL_XOUT_H = 0x2D
GYRO_XOUT_H = 0x33
WHO_AM_I = 0x00

def read_i2c_word(reg):
    high = bus.read_byte_data(ICM20948_ADDR, reg)
    low = bus.read_byte_data(ICM20948_ADDR, reg + 1)
    value = struct.unpack('>h', bytes([high, low]))[0]  # signed short
    return value

def initialize_icm20948():
    select_bank(0)
    whoami = bus.read_byte_data(ICM20948_ADDR, WHO_AM_I)
    if whoami != 0xEA:
        print(f"Unexpected WHO_AM_I value: {hex(whoami)}")
    else:
        print("ICM20948 detected")
    bus.write_byte_data(ICM20948_ADDR, 0x06, 0x01)  # Wake up (PWR_MGMT_1)

initialize_icm20948()

# === Quiz 2 settings ===
acc_offset_x = 0.02    # G
gyro_offset_z = 0.8    # deg/s
dt = 1.0               # 1 second per loop

velocity = 0.0         # m/s
distance = 0.0         # m
angle = 0.0            # degrees

try:
    while True:
        select_bank(0)

        # Read raw values
        acc_x_raw = read_i2c_word(ACCEL_XOUT_H)
        gyro_z_raw = read_i2c_word(GYRO_XOUT_H + 4)

        # Convert to physical units
        acc_x_g = acc_x_raw / 16384.0
        acc_x_ms2 = (acc_x_g - acc_offset_x) * 9.81

        gyro_z_dps = gyro_z_raw / 131.0
        gyro_z_calibrated = gyro_z_dps - gyro_offset_z

        # Quiz 2-1: Velocity and Distance
        velocity += acc_x_ms2 * dt
        distance += velocity * dt + 0.5 * acc_x_ms2 * dt * dt

        # Quiz 2-2: Rotation Angle
        angle += gyro_z_calibrated * dt

        # Output
        print(f"AccX: {acc_x_g:.3f} g | {acc_x_ms2:.2f} m/s^2 | v = {velocity:.2f} m/s | s = {distance:.2f} m")
        print(f"GyroZ: {gyro_z_dps:.2f} deg/s | angle = {angle:.2f} deg")
        print("-" * 60)

        time.sleep(dt)

except KeyboardInterrupt:
    print("Stopped.")
