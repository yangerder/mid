import smbus2
import time
import math

# BMP280 I2C address (could be 0x76 or 0x77 depending on module)
BMP280_ADDRESS = 0x77

# Initialize I2C (SMBus)
bus = smbus2.SMBus(1)

def read_bmp280_data():
    # Read temperature raw data
    msb = bus.read_byte_data(BMP280_ADDRESS, 0xFA)
    lsb = bus.read_byte_data(BMP280_ADDRESS, 0xFB)
    xlsb = bus.read_byte_data(BMP280_ADDRESS, 0xFC)
    adc_T = (msb << 16) | (lsb << 8) | xlsb
    adc_T >>= 4

    # Read pressure raw data
    msb = bus.read_byte_data(BMP280_ADDRESS, 0xF7)
    lsb = bus.read_byte_data(BMP280_ADDRESS, 0xF8)
    xlsb = bus.read_byte_data(BMP280_ADDRESS, 0xF9)
    adc_P = (msb << 16) | (lsb << 8) | xlsb
    adc_P >>= 4

    return adc_T, adc_P

def compensate_temperature(adc_T):
    global t_fine
    var1 = (((adc_T >> 3) - (dig_T1 << 1)) * dig_T2) >> 11
    var2 = (((((adc_T >> 4) - dig_T1) * ((adc_T >> 4) - dig_T1)) >> 12) * dig_T3) >> 14
    t_fine = var1 + var2
    temperature = (t_fine * 5 + 128) >> 8
    return temperature, t_fine

def compensate_pressure(adc_P, t_fine):
    var1 = t_fine - 128000
    var2 = var1 * var1 * dig_P6
    var2 = var2 + ((var1 * dig_P5) << 17)
    var2 = var2 + (dig_P4 << 35)
    var1 = ((var1 * var1 * dig_P3) >> 8) + ((var1 * dig_P2) << 12)
    var1 = (((1 << 47) + var1) * dig_P1) >> 33

    if var1 == 0:
        return 0  # avoid division by zero

    p = 1048576 - adc_P
    p = (((p << 31) - var2) * 3125) // var1
    var1 = (dig_P9 * (p >> 13) * (p >> 13)) >> 25
    var2 = (dig_P8 * p) >> 19
    pressure = ((p + var1 + var2) >> 8) + (dig_P7 << 4)
    return pressure

def load_calibration_params():
    calib = []
    for i in range(0x88, 0x88+24):
        calib.append(bus.read_byte_data(BMP280_ADDRESS, i))
    calib.append(bus.read_byte_data(BMP280_ADDRESS, 0xA1))
    return calib

def calculate_altitude(pressure_pa, sea_level_pressure=101325.0):
    return (1 - (pressure_pa / sea_level_pressure) ** (1 / 5.255)) * 44330

# Load and parse calibration parameters
calib = load_calibration_params()

dig_T1 = (calib[1] << 8) | calib[0]
dig_T2 = (calib[3] << 8) | calib[2]
dig_T3 = (calib[5] << 8) | calib[4]
dig_P1 = (calib[7] << 8) | calib[6]
dig_P2 = (calib[9] << 8) | calib[8]
dig_P3 = (calib[11] << 8) | calib[10]
dig_P4 = (calib[13] << 8) | calib[12]
dig_P5 = (calib[15] << 8) | calib[14]
dig_P6 = (calib[17] << 8) | calib[16]
dig_P7 = (calib[19] << 8) | calib[18]
dig_P8 = (calib[21] << 8) | calib[20]
dig_P9 = (calib[23] << 8) | calib[22]

# Main loop
try:
    while True:
        adc_T, adc_P = read_bmp280_data()
        temperature, t_fine = compensate_temperature(adc_T)
        pressure = compensate_pressure(adc_P, t_fine)
        pressure_pa = pressure / 256.0  # Convert to Pa
        altitude = calculate_altitude(pressure_pa)-2200

        print(f"Temperature: {temperature / 100.0:.2f} C")
        print(f"Pressure: {pressure_pa:.2f} Pa")
        print(f"Altitude: {altitude:.2f} m\n")

        time.sleep(1)

except KeyboardInterrupt:
    print("Program stopped.")
