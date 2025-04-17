import time
from smbus2 import SMBus
from struct import unpack

I2C_ADDR = 0x68
ICM20948_ACCEL_XOUT_H = 0x2D
ICM20948_GYRO_XOUT_H = 0x33
ICM20948_PWR_MGMT_1 = 0x06
CHIP_ID = 0xEA

bus = SMBus(1)

def read_bytes(addr, reg, length):
    return bus.read_i2c_block_data(addr, reg, length)

def write_byte(addr, reg, value):
    bus.write_byte_data(addr, reg, value)

def initialize_imu():
    write_byte(I2C_ADDR, ICM20948_PWR_MGMT_1, 0x80)
    time.sleep(0.01)
    write_byte(I2C_ADDR, ICM20948_PWR_MGMT_1, 0x01)

def read_accel_gyro():
    data = read_bytes(I2C_ADDR, ICM20948_ACCEL_XOUT_H, 12)
    ax, ay, az, gx, gy, gz = unpack(">hhhhhh", bytearray(data))
    ax, ay, az = ax / 16384.0, ay / 16384.0, az / 16384.0
    gx, gy, gz = gx / 131.0, gy / 131.0, gz / 131.0
    return ax, ay, az, gx, gy, gz

initialize_imu()

try:
    while True:
        ax, ay, az, gx, gy, gz = read_accel_gyro()
        print(f"Accel: {ax:.2f} {ay:.2f} {az:.2f} | Gyro: {gx:.2f} {gy:.2f} {gz:.2f}")
        time.sleep(0.5)
except KeyboardInterrupt:
    bus.close()
    print("end")
