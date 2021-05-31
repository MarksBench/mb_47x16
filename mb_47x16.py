"""
mb_47x16.py

Very Simple MicroPython module/driver for Microchip 47L16/47C16 I2C EERAM

Author: mark@marksbench.com

Version: 0.1, 2021-05-31

**NOTE(1): There is no guarantee that this software will work in the way you expect (or at all).
**Use at your own risk.

**NOTE(2): This driver only seems to work reliably with an I2C bus speed of 400000.
**It is not stable at 100000 with the MCUs and/or 47L16s that I have on hand.
**I will be investigating this further.

**NOTE(3): The 47xxx EERAM will show up as TWO devices on the I2C bus. An i2c.scan() with
**the default addresses (disconnected or tied to Vss) will give the result [24, 80]. This
**is normal behaviour. The SRAM array is accessed via the high address, and the control
**registers are accessed via the low address. No need to worry, this driver handles all that.

**NOTE(4): This driver sets the Auto-Store Enable (ASE) bit so the 47L16 will try to write
**the contents of the SRAM to the EEPROM in the event of a power failure. You must have
**a capacitor of at least 10uF (I am using 22uF) connected between Vcap (Pin 1) and GND
**for the device to operate properly.

**NOTE(5): This driver can send commands to copy the SRAM contents to EEPROM (and vice
**versa). It doesn't require a microcontroller pin to drive the HS pin, although you still
**can if you'd like.

**NOTE(6): Wait times are currently set to much higher than the datasheet specifies.
**They can likely be set lower for an increase in speed (particularly writing to EEPROM).

**NOTE(7): The EEPROM write protection in the attached 47xxx device is disabled on startup.

**NOTE(8): Table for addresses vs A2 and A1 pin settings is:
# A2 | A1 |Addresses
#  0 | 0  | 0x24, 0x80
#  0 | 1  | 0x26, 0x82
#  1 | 0  | 0x28, 0x84
#  1 | 1  | 0x30, 0x86
# A2 and A1 are internally pulled-down, so not connecting them will set them to 0.


Prerequisites:
- RP2040 silicon (tested with Raspberry Pi Pico RP2040), should work with other MCUs.
- MicroPython v1.15.
- EERAM device connected to functioning HW or SW I2C bus.


Usage:
- from machine import Pin, I2C
- import utime
- set up I2C (preferably hardware), using a speed of 400000 (100000 seems buggy at this point)
- Create constructor:
  thisMemoryChipDeviceName = mb_47L16.py(i2c)
- To write a single byte to an address:
  thisMemoryChipDeviceName.write_byte(address, value)
- To read a single byte from an address:
  thisMemoryChipDeviceName.read_byte(address)
- To store contents of SRAM to EEPROM:
  store_to_EEPROM()
- To recall contents of EEPROM to SRAM:
  recall_from_EEPROM()
  
For more information, consult the Raspberry Pi Pico MicroPython SDK documentation at:
  https://datasheets.raspberrypi.org/pico/raspberry-pi-pico-python-sdk.pdf

and the Microchip 47xxx datasheet at:
  https://ww1.microchip.com/downloads/en/DeviceDoc/47L04_47C04_47L16_47C16_DS20005371D.pdf

"""

from machine import Pin, I2C
import utime



# A1, A2, and HS are internally tied to GND via pull-downs
# 47L16 shows two addresses: The SRAM array (high value) and the Control registers (low)
# With A1 A2 tied to GND or NC, addresses shown are 24 (Control) and 80 (SRAM)

_SRAM_READ = 0b10100001
_SRAM_WRITE = 0b10100000
_CTRL_READ = 0b00110001
_CTRL_WRITE = 0b00110000


_MAX_ADDRESS = 2047 # 47L16 is a 16Kbit device (2048x8)


class mb_47x16:
    """Driver for Microchip 47x16 series of EERAM modules"""
    
    def __init__(self, i2c, i2c_address):
        # Init with I2C settings
        self.i2c = i2c
        self.i2c_address_high = i2c_address # SRAM - this is the higher of the 2 I2C addresses from the 47xxx
        self.i2c_address_low = (i2c_address - 56) # CONTROL - lower of the 2 I2C addresses
        
        # STATUS control register is at offset 0x00
        # COMMAND control register is at offset 0x55
        # Set ASE (automatic store enable) bit (bit1) in STATUS control status register to 1 for ASE
        i2c.writeto_mem(self.i2c_address_low, 0, bytearray([0b11100011]), addrsize=8) ##MIGHT WANT TO READ AND CHECK IF IT NEEDS TO BE SET INSTEAD OF JUST SETTING IT
        # Optionally, can write-protect part or all of the array by setting b4, b3, and b2 in
        # the STATUS control register to 1
        utime.sleep_ms(25)
        
        # Done init, ready to go

    def read_byte(self, address):
        if(address > _MAX_ADDRESS):
            raise ValueError("Address is outside of device address range (0 to 2047)")
            return()
    
        value_read = self.i2c.readfrom_mem(self.i2c_address_high, address, 1, addrsize=16)
        return(int.from_bytes(value_read, "big"))


    def write_byte(self, address, data):
        if(address > _MAX_ADDRESS):
            raise ValueError("Address is outside of device address range (0 to 2047)")
            return()
        if((data > 255) or (data < 0)):
            raise ValueError("You can only pass an 8-bit data value (0-255) to this function")
            return()
        
        self.i2c.writeto_mem(self.i2c_address_high, address, bytearray([data]), addrsize=16)
        return()


    def store_to_EEPROM(self):
        self.i2c.writeto_mem(self.i2c_address_low, 0x55, bytearray([0b00110011]), addrsize=8) #offset 0x55 for COMMAND status register
        utime.sleep_ms(50)
        return()

    def recall_from_EEPROM(self):
        self.i2c.writeto_mem(self.i2c_address_low, 0x55, bytearray([0b11011101]), addrsize=8) #offset 0x55 for COMMAND status register
        utime.sleep_ms(50)
        return()


