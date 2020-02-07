# Write your code here :-)
### cpx-basic-synth v1.4
### CircuitPython (on CPX) synth module using internal speaker
### Velocity sensitive monophonic synth
### with crude amplitude modulation (cc1) and choppy pitch bend

### Tested with CPX and CircuitPython and 4.0.0-beta.7

### Needs recent adafruit_midi module

### copy this file to CPX as code.py

### MIT License.

### Copyright (c) 2019 Kevin J. Walters

### Permission is hereby granted, free of charge, to any person obtaining a copy
### of this software and associated documentation files (the "Software"), to deal
### in the Software without restriction, including without limitation the rights
### to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
### copies of the Software, and to permit persons to whom the Software is
### furnished to do so, subject to the following conditions:

### The above copyright notice and this permission notice shall be included in all
### copies or substantial portions of the Software.

### THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
### IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
### FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
### AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
### LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
### OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
### SOFTWARE.

import array
import time
import math

import digitalio
import board
import usb_midi
import neopixel

from adafruit_ble import BLERadio
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.nordic import UARTService

from adafruit_bluefruit_connect.packet import Packet
from adafruit_bluefruit_connect.color_packet import ColorPacket

# brightness 1.0 saves memory by removing need for a second buffer
# 10 is number of NeoPixels on CPX
numpixels = 10  # was const(10)
pixels = neopixel.NeoPixel(board.A3, numpixels, brightness=0.1)

# Turn NeoPixel on to represent a note using RGB x 10
# to represent 30 notes - doesn't do anything with pitch bend

ble = BLERadio()
uart = UARTService()
advertisement = ProvideServicesAdvertisement(uart)

# Read any incoming MIDI messages (events) over USB
# looking for note on, note off, pitch bend change
# or control change for control 1 (modulation wheel)
# Apply crude amplitude modulation using speaker enable
pixels.fill(0x110000)
time.sleep(1)
pixels.fill(0x000000)

while True:
    ble.start_advertising(advertisement)
    while not ble.connected:
        pass

    while ble.connected:
        packet = Packet.from_stream(uart)
        if isinstance(packet, ColorPacket):
            pixels.fill(packet.color)