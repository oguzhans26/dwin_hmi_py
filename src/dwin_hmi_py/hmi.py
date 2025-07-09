"""
hmi.py

Core module defining the DwinHMI class for register and float access.
"""

import time
import struct
import serial


class DwinHMI:
    """
    DwinHMI provides methods to read/write 16-bit registers and 32-bit floats
    on DWIN DGUS HMI devices via a serial interface.
    """

    def __init__(self, port: str, baudrate: int = 115200, timeout: float = 0.1):
        """
        Initialize serial connection.

        :param port: Serial port identifier (e.g., '/dev/ttyUSB0' or 'COM3').
        :param baudrate: Communication speed in bits per second.
        :param timeout: Read timeout in seconds.
        """
        self.ser = serial.Serial(port=port, baudrate=baudrate, timeout=timeout)

    def send_packet(self, packet: bytes) -> None:
        """
        Transmit a raw packet to the HMI.

        :param packet: Byte sequence following DWIN packet frame.
        """
        self.ser.write(packet)

    def read_bytes(self, length: int, timeout: float = None) -> bytes:
        """
        Read a fixed number of bytes with an optional custom timeout.

        :param length: Number of bytes to read.
        :param timeout: Override the serial timeout if provided.
        :return: Bytes object of received data.
        """
        deadline = time.time() + (timeout if timeout is not None else self.ser.timeout)
        buffer = bytearray()
        while len(buffer) < length and time.time() < deadline:
            if self.ser.in_waiting:
                buffer.extend(self.ser.read(1))
        return bytes(buffer)

    def write_register(self, vp_addr: int, value: int) -> None:
        """
        Write a single 16-bit register.

        Packet structure:
          [0x5A, 0xA5] Header
          [0x05]      Length
          [0x82]      Command: write register
          [VP_H, VP_L] Address high/low byte
          [VAL_H, VAL_L] Value high/low byte

        :param vp_addr: Variable parameter address (0–0xFFFF).
        :param value:   16-bit value to write.
        """
        packet = bytearray([
            0x5A, 0xA5,
            0x05, 0x82,
            (vp_addr >> 8) & 0xFF, vp_addr & 0xFF,
            (value >> 8) & 0xFF, value & 0xFF
        ])
        self.send_packet(packet)
        # Discard 6-byte ACK response
        self.read_bytes(6)

    def read_register(self, vp_addr: int) -> int:
        """
        Read a single 16-bit register.

        Packet structure:
          [0x5A, 0xA5] Header
          [0x04]      Length
          [0x83]      Command: read register
          [VP_H, VP_L] Address
          [0x01]      Number of registers

        Response format:
          [0x5A, 0xA5, LEN, 0x83, VP_H, VP_L, 0x01, VAL_H, VAL_L]

        :param vp_addr: Variable parameter address.
        :return: 16-bit register value.
        :raises ValueError: on timeout or invalid response.
        """
        packet = bytearray([
            0x5A, 0xA5,
            0x04, 0x83,
            (vp_addr >> 8) & 0xFF, vp_addr & 0xFF,
            0x01
        ])
        self.send_packet(packet)
        resp = self.read_bytes(9)
        if len(resp) != 9 or resp[0:2] != b'\x5A\xA5' or resp[3] != 0x83:
            raise ValueError("Invalid response or timeout in read_register")
        return (resp[7] << 8) | resp[8]

    def write_float(self, vp_addr: int, value: float) -> None:
        """
        Write a 32-bit float to two consecutive 16-bit registers.

        Internally, packs as little-endian float, then sends high-word first.

        :param vp_addr: Starting VP address.
        :param value:    IEEE-754 float.
        """
        raw = struct.pack('<f', value)
        msw = (raw[3] << 8) | raw[2]  # Big-endian high word
        lsw = (raw[1] << 8) | raw[0]  # Big-endian low word
        self.write_register(vp_addr, msw)
        self.write_register(vp_addr + 1, lsw)

    def read_float(self, vp_addr: int) -> float:
        """
        Read two 16-bit registers and reconstruct a 32-bit float.

        :param vp_addr: Starting VP address.
        :return: IEEE-754 float.
        """
        msw = self.read_register(vp_addr)
        lsw = self.read_register(vp_addr + 1)
        raw = bytearray(4)
        raw[3], raw[2] = (msw >> 8) & 0xFF, msw & 0xFF
        raw[1], raw[0] = (lsw >> 8) & 0xFF, lsw & 0xFF
        return struct.unpack('<f', raw)[0]
