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
import adafruit_midi
import _bleio

from adafruit_bluefruit_connect.color_packet import ColorPacket

from adafruit_ble import BLERadio
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.nordic import UARTService

from adafruit_midi.midi_message     import note_parser

from adafruit_midi.note_on          import NoteOn
from adafruit_midi.note_off         import NoteOff

# brightness 1.0 saves memory by removing need for a second buffer
# 10 is number of NeoPixels on CPX
numpixels = 10  # was const(10)
pixels = neopixel.NeoPixel(board.NEOPIXEL, numpixels, brightness=1.0)
midi_note_C4 = note_parser("C4")
# Turn NeoPixel on to represent a note using RGB x 10
# to represent 30 notes - doesn't do anything with pitch bend
def noteLED(pix, pnote, pvel):
    note30 = (pnote - midi_note_C4) % (3 * numpixels)
    pos = note30 % numpixels
    r, g, b = pix[pos]
    if pvel == 0:
        brightness = 0
    else:
        # max brightness will be 32
        brightness = round(pvel / 127 * 30 + 2)
    # Pick R/G/B based on range within the 30 notes
    if note30 < 10:
        r = brightness
    elif note30 < 20:
        g = brightness
    else:
        b = brightness
    pix[pos] = (r, g, b)

ble = BLERadio()
uart_connection = None

if ble.connected:
    for connection in ble.connections:
        if UARTService in connection:
            uart_connection = connection
            break

midi_channel = 1

midi = adafruit_midi.MIDI(midi_in=usb_midi.ports[0],
                          in_channel=midi_channel-1)


# Read any incoming MIDI messages (events) over USB
# looking for note on, note off, pitch bend change
# or control change for control 1 (modulation wheel)
# Apply crude amplitude modulation using speaker enable

while True:
    if uart_connection is None:
        print("Scanning...")
        for adv in ble.start_scan(ProvideServicesAdvertisement, timeout=5):
            if UARTService in adv.services:
                print("found a UARTService advertisement")
                uart_connection = ble.connect(adv)
                break
        # Stop scanning whether or not we are connected.
        ble.stop_scan()

    while uart_connection and uart_connection.connected:
        msg = midi.receive()
        color = (0, 0, 0)

        if isinstance(msg, NoteOn) and msg.velocity != 0:
            noteLED(pixels, msg.note, msg.velocity)
            color = (255, 0, 0)

        elif (isinstance(msg, NoteOff) or
            isinstance(msg, NoteOn) and msg.velocity == 0):
            noteLED(pixels, msg.note, 0)
            color = (0, 0, 0)

        try:
            if msg is not None:
                color_packet = ColorPacket(color)
                uart_connection[UARTService].write(color_packet.to_bytes())
        except (OSError,):
            try:
                uart_connection.disconnect()
            except: # pylint: disable=bare-except
                pass
            uart_connection = None

        time.sleep(0.05)