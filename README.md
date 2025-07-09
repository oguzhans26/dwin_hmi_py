# dwin_hmi_py

A Python library for interfacing with DWIN DGUS HMI modules via serial communication.  
Supports reading and writing 16-bit registers and 32-bit floating-point values.

## Features

- Write single 16-bit registers
- Read single 16-bit registers
- Write 32-bit floats as two 16-bit registers
- Read 32-bit floats from two 16-bit registers
- Automatic packet framing and ACK handling

## Installation

```bash
pip install dwin_hmi

## Or install from source:
git clone https://github.com/oguzhans26/dwin_hmi_py.git
cd dwin_hmi
pip install -e .

## Usage

from dwin_hmi_py import DwinHMI

# Initialize with serial port, baud rate, and timeout
hmi = DwinHMI(port='/dev/ttyUSB0', baudrate=115200, timeout=0.2)

# Write a 16-bit value
hmi.write_register(0x07D0, 1234)

# Read it back
value = hmi.read_register(0x07D0)
print(f"Register 0x07D0 = {value}")

# Write and read a float
hmi.write_float(0x0800, 3.1415)
pi = hmi.read_float(0x0800)
print(f"Float at 0x0800 = {pi:.4f}")
