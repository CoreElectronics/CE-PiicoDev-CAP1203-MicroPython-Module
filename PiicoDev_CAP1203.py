# A simple class to read data from the Core Electronics PiicoDev CAP1203 Capacitive Touch Sensor
# Ported to MicroPython by Peter Johnston at Core Electronics JUN 2021
# Original repo by SparkFun https://github.com/sparkfun/SparkFun_CAP1203_Arduino_Library

from PiicoDev_Unified import *

compat_str = '\nUnified PiicoDev library out of date.  Get the latest module: https://piico.dev/unified \n'

# Declare I2C Address
_CAP1203Address = b'\x28'

# Registers as defined in Table 5-1 from datasheet (pg 20-21)
_MAIN_CONTROL = b'\x00'
_GENERAL_STATUS = b'\x02'
_SENSOR_INPUT_STATUS = b'\x03'
_SENSOR_INPUT_1_DELTA_COUNT = b'\x10'
_SENSOR_INPUT_2_DELTA_COUNT = b'\x11'
_SENSOR_INPUT_3_DELTA_COUNT = b'\x12'
_SENSITIVITY_CONTROL = b'\x1F'
_CONFIG = b'\x20'
_INTERRUPT_ENABLE = b'\x27'
_REPEAT_RATE_ENABLE = b'\x28'
_MULTIPLE_TOUCH_CONFIG = b'\x2A'
_MULTIPLE_TOUCH_PATTERN_CONFIG = b'\x2B'
_MULTIPLE_TOUCH_PATTERN = b'\x2D'
_PRODUCT_ID = b'\xFD'

# Product ID - always the same (pg. 22)
_PROD_ID_VALUE = b'\x6D'

class PiicoDev_CAP1203(object):
    
    def __init__(self, bus=None, freq=None, sda=None, scl=None, addr=int.from_bytes(_CAP1203Address,"big"), touchmode = "single", sensitivity = 6):
        try:
            if compat_ind >= 1:
                pass
            else:
                print(compat_str)
        except:
            print(compat_str)
        self.i2c = create_unified_i2c(bus=bus, freq=freq, sda=sda, scl=scl)
        self.addr = addr
        
        for i in range(0,1):
            sleep_ms(1000)
            try:
                product_ID_value = self.i2c.readfrom_mem(self.addr, int.from_bytes(_PRODUCT_ID,"big"), 1) 
                # to initialise the device
                if (product_ID_value == _PROD_ID_VALUE):
                    print("product ID match")
                    print("connected...")
            except:
                print("connection failed")
            if (touchmode == "single"):
                self.setBits(_MULTIPLE_TOUCH_CONFIG,b'\x80',b'\x80')
            if (touchmode == "multi"):
                self.setBits(_MULTIPLE_TOUCH_CONFIG,b'\x00',b'\x80')
            if (sensitivity >= 0 and sensitivity <= 7): # check for valid entry
                self.setBits(_SENSITIVITY_CONTROL,bytes([sensitivity*16]),b'\x70')
    
    def setBits(self, address, byte, mask):
        old_byte = int.from_bytes(self.i2c.readfrom_mem(self.addr, int.from_bytes(address,"big"), 1),"big")
        temp_byte = old_byte
        int_byte = int.from_bytes(byte,"big")
        int_mask = int.from_bytes(mask,"big")
        for n in range(8): # Cycle through each bit
            bit_mask = (int_mask >> n) & 1
            if bit_mask == 1:
                if ((int_byte >> n) & 1) == 1:
                    temp_byte = temp_byte | 1 << n
                else:
                    temp_byte = temp_byte & ~(1 << n)
        new_byte = temp_byte
        self.i2c.writeto_mem(self.addr, int.from_bytes(address,"big"), bytes([new_byte]))
    
    def getSensitivity(self):
        sensitivity_control = self.i2c.readfrom_mem(self.addr, int.from_bytes(_SENSITIVITY_CONTROL,"big"), 1)

    def setSensitivity(self):
        self.i2c.writeto_mem(self.addr, int.from_bytes(_SENSITIVITY_CONTROL,"big"), 0x6F)
        
    def clearInterrupt(self):
        self.i2c.writeto_mem(self.addr, int.from_bytes(_MAIN_CONTROL,"big"), bytes([0x00]))
        main_control_value = self.i2c.readfrom_mem(self.addr, int.from_bytes(_MAIN_CONTROL,"big"), 1)
    
    def read(self):
        CS1return = 0
        CS2return = 0
        CS3return = 0
        try:
            self.clearInterrupt()
            general_status_value = self.i2c.readfrom_mem(self.addr, int.from_bytes(_GENERAL_STATUS,"big"), 1)
        except:
            print(i2c_err_str.format(self.addr))
            return float('NaN'), float('NaN'), float('NaN')    
        mask =  0b00000001
        value = mask & int.from_bytes(general_status_value,'big')
        sensor_input_status = self.i2c.readfrom_mem(self.addr, int.from_bytes(_SENSOR_INPUT_STATUS,"big"), 1)
        CS1 = 0b00000001 & int.from_bytes(sensor_input_status,'big')
        CS2 = 0b00000010 & int.from_bytes(sensor_input_status,'big')
        CS3 = 0b00000100 & int.from_bytes(sensor_input_status,'big')
        if (CS1 > 0):
            CS1return = 1
        if (CS2 > 0):
            CS2return = 1
        if (CS3 > 0):
            CS3return = 1
        return CS1return, CS2return, CS3return
    
    def readDeltaCounts(self):
        DC1return = 0
        DC2return = 0
        DC3return = 0
        try:
            DC1 = self.i2c.readfrom_mem(self.addr, int.from_bytes(_SENSOR_INPUT_1_DELTA_COUNT,"big"), 1)
            DC2 = self.i2c.readfrom_mem(self.addr, int.from_bytes(_SENSOR_INPUT_2_DELTA_COUNT,"big"), 1)
            DC3 = self.i2c.readfrom_mem(self.addr, int.from_bytes(_SENSOR_INPUT_3_DELTA_COUNT,"big"), 1)
        except:
            print(i2c_err_str.format(self.addr))
            return float('NaN'), float('NaN'), float('NaN') 
        return DC1, DC2, DC3
        
