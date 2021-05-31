# mb_47x16
Very simple MicroPython module/driver for Microchip 47x16 EERAM devices (47L/47C). Works with RP2040 (tested on Raspberry Pi Pico), should run on other microcontrollers that have hardware or software I2C and run MicroPython v1.15.

This module is intended to make using the 47x16 as simple as possible. It has the following functions:
- Write a value (range 0-255) to a SRAM address (range 0-2047)
- Read a value from an SRAM address (range 0-2047), values are returned as integers
- Store the contents of SRAM to EEPROM
- Recall the contents of EEPROM into SRAM

The Microchip 47x16 is a neat little device. EERAM was a new acronym for me - I initially thought it was a typo, but it turns out it's far cooler than a typo in a datasheet - it's a combination device that contains both SRAM and EEPROM. If it's properly connected (with the proper capacitor value) and configured, it will write the contents of the SRAM to the EEPROM in the event of a power failure or a hardware or software store request. On power-up (or on a software recall request), the contents of the EEPROM will be written back to SRAM.

This is particularly neat because it combines the essentially infinite write cycles and high speed of SRAM with the nonvolatility of EEPROM, while not requiring a battery.

Author: mark@marksbench.com

Version: 0.1, 2021-05-31

**NOTE(1): There is no guarantee that this software will work in the way you expect (or at all).
Use at your own risk.

**NOTE(2): This driver only seems to work reliably with an I2C bus speed of 400000.
It is not stable at 100000 with the MCUs and/or 47L16s that I have on hand.
I will be investigating this further.

**NOTE(3): The 47xxx EERAM will show up as TWO devices on the I2C bus. An i2c.scan() with
the default addresses (disconnected or tied to Vss) will give the result [24, 80]. This
is normal behaviour. The SRAM array is accessed via the high address, and the control
registers are accessed via the low address. No need to worry, this driver handles all that.

**NOTE(4): This driver sets the Auto-Store Enable (ASE) bit so the 47L16 will try to write
the contents of the SRAM to the EEPROM in the event of a power failure. You must have
a capacitor of at least 10uF (I am using 22uF) connected between Vcap (Pin 1) and GND
for the device to operate properly.

**NOTE(5): This driver can send commands to copy the SRAM contents to EEPROM (and vice
versa). It doesn't require a microcontroller pin connected to the HS pin to copy SRAM
to EEPROM, although you can still do that if you'd like.

**NOTE(6): Wait times are currently set to much higher than the datasheet specifies.
They can likely be set lower for an increase in speed (particularly writing to EEPROM).

**NOTE(7): The EEPROM write protection in the attached 47xxx device is disabled on startup.

**NOTE(8): Table for addresses vs A2 and A1 pin settings is:

* A2 | A1 |Addresses
*  0 | 0  | 0x24, 0x80
*  0 | 1  | 0x26, 0x82
*  1 | 0  | 0x28, 0x84
*  1 | 1  | 0x30, 0x86
* A2 and A1 are internally pulled-down, so not connecting them will set them to 0.


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
- See mb_47x16_example.py
  
For more information, consult the Raspberry Pi Pico MicroPython SDK documentation at:
  https://datasheets.raspberrypi.org/pico/raspberry-pi-pico-python-sdk.pdf
  
and the MicroPython I2C documentation at:
  https://docs.micropython.org/en/latest/library/machine.I2C.html

and the Microchip 47xxx datasheet at:
  https://ww1.microchip.com/downloads/en/DeviceDoc/47L04_47C04_47L16_47C16_DS20005371D.pdf
