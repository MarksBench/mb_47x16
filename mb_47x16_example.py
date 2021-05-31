"""
mb_47x16_example.py

Example MicroPython script for Microchip 47x16 EERAM with RP2040 (Raspberry Pi Pico)
(Should work with other MicroPython-capable devices with hardware of software I2C)

Author: mark@marksbench.com

Version: 0.1, 2021-05-31

**NOTE: There is no guarantee that this software will work in the way you expect (or at all).
**Use at your own risk.

To use:
- Upload the mb_47x16.py file to your board (the same location where your MicroPython scripts
  run from, or the /lib folder if applicable).
- Connect the 47L16 (the "C" version is 5V!) to the Pi Pico (RP2040).
- For testing (and to use this example script without modification) I suggest the following:
  
        47L16    |    Pi Pico
        1(Vcap) - not connected to Pico. Connect instead to +ve of >10uF capacitor and -ve of cap to GND
        2(A1)    |    NC (internally pulled-down)
        3(A2)    |    NC (internally pulled-down)
        4(Vss)   |    GND, (Pin 38)
        5(SDA)   |    GP0(Pin 1)
        6(SCL)   |    GP1(Pin 2)
        7(HS)    |    NC (internally pulled-down)
        8(Vcc)   |    3V3 OUT, (Pin 36)
        
- To write a value: memory.write_byte(address, value)
- To read a value: value = memory.read_byte(address)
- You should get an error if the address or value is out of range.
- To store contents of SRAM to EEPROM: memory.store_to_EEPROM()
- To recall contents of EEPROM to SRAM: memory.recall_from_EEPROM()
"""


from machine import Pin, I2C
import utime
import mb_47x16

# Set up I2C
i2c = I2C(0, scl=Pin(1), sda=Pin(0), freq=400000) # Unstable at 100000???

# Now scan the bus for the addresses. The 47xxx series devices will have TWO I2C addresses.
# Table for addresses vs A2 and A1 pin settings is:
# A2 | A1 |Addresses
#  0 | 0  | 24, 80
#  0 | 1  | 26, 82
#  1 | 0  | 28, 84
#  1 | 1  | 30, 86
# A2 and A1 are internally pulled-down, so not connecting them will set them to 0.

i2c_found = i2c.scan()
print(i2c_found)

# The I2C addresses are always offset by the same amount, so only need to send one address. If the
# 47xxx is the only device on the bus, you can let it use the highest address it scanned.
# Otherwise, comment out the following line and uncomment the line after that and put the
# higher of the two addresses the 47xxx is at (80, 82, 84, or 86)
i2c_address = (i2c_found[1])
#i2c_address = put high address here


memory = mb_47x16.mb_47x16(i2c, i2c_address)

# A1, A2, and HS are internally tied to GND via pull-downs
# 47L16 shows two addresses: The SRAM array (high value) and the Control registers (low)
# With A1 A2 tied to GND or NC, addresses shown are 24 (Control) and 80 (SRAM)

value1 = 5 # Put anything from 0-255 in here
value2 = 131 # Put anything from 0-255 in here

print("value1 = ", value1)
print("value2 = ", value2)

memory.write_byte(0, value1) # Write value1 to SRAM at address 0x0000, should be value1

print(memory.read_byte(0)) # Read the contents of SRAM location 0x0000, should be value1

memory.store_to_EEPROM() # Store the contents of SRAM to EEPROM, overwriting the EEPROM

memory.write_byte(0, value2) # Write value2 to SRAM at address 0x0000, should be value2

print(memory.read_byte(0)) # Read the contents of SRAM location 0x0000, should be value2

memory.recall_from_EEPROM() # Recall the contents of the EEPROM, overwriting the SRAM

print(memory.read_byte(0)) # Read the contents of SRAM location 0x0000, should be back to value1

# That's all there is to it.

print("Done")
