# tests/test_hmi_usage.py

import struct
import pytest
from dwin_hmi_py.hmi import DwinHMI  

class FakeSerial:
    """
    A fake serial port for testing DwinHMI.
    It captures written bytes and provides a read buffer.
    """
    def __init__(self, response_bytes: bytes = b"", timeout: float = 0.1):
        self._write_buffer = bytearray()
        self._read_buffer  = bytearray(response_bytes)
        self.timeout       = timeout

    @property
    def in_waiting(self) -> int:
        return len(self._read_buffer)

    def write(self, data: bytes) -> int:
        self._write_buffer.extend(data)
        return len(data)

    def read(self, size: int = 1) -> bytes:
        chunk = self._read_buffer[:size]
        self._read_buffer = self._read_buffer[size:]
        return bytes(chunk)


@pytest.fixture
def hmi(monkeypatch):
    """
    Replace serial.Serial inside our module with FakeSerial.
    """
    fake = FakeSerial()
    monkeypatch.setattr("dwin_hmi_py.hmi.serial.Serial",
                        lambda *args, **kwargs: fake)
    return DwinHMI(port="COM_FAKE", baudrate=115200, timeout=0.1)


def _make_ack() -> bytes:
    # 6-byte ACK for write_register
    return b"\x5A\xA5\x02\x82\x00\x00"


def _make_read_response(addr: int, value: int) -> bytes:
    # 9-byte response for read_register
    return bytes([
        0x5A, 0xA5,      # Header
        0x04,            # Length
        0x83,            # Read cmd echo
        (addr >> 8) & 0xFF,
        addr & 0xFF,
        0x01,            # Count = 1
        (value >> 8) & 0xFF,
        value & 0xFF
    ])


def test_register_read_write_flow(hmi):
    # Simulate ACK for write_register
    hmi.ser._read_buffer = _make_ack()

    # Write register 0x07D0 = 1234
    hmi.write_register(0x07D0, 1234)
    expected = bytes([0x5A, 0xA5, 0x05, 0x82, 0x07, 0xD0, 0x04, 0xD2])
    assert hmi.ser._write_buffer[:8] == expected

    # Simulate read response
    hmi.ser._read_buffer = _make_read_response(0x07D0, 1234)
    val = hmi.read_register(0x07D0)
    assert val == 1234


def test_float_read_write_flow(hmi):
    # Two ACKs for two write_register calls
    ack = _make_ack()
    hmi.ser._read_buffer = ack + ack

    # Write a float at 0x0800
    pi = 3.1415
    hmi.write_float(0x0800, pi)

    # Check that two write packets went out
    writ = hmi.ser._write_buffer
    assert writ[0:4] == b"\x5A\xA5\x05\x82"
    assert writ[8:12] == b"\x5A\xA5\x05\x82"

    # Now simulate two read responses
    packed = struct.pack("<f", pi)
    msw = (packed[3] << 8) | packed[2]
    lsw = (packed[1] << 8) | packed[0]
    resp1 = _make_read_response(0x0800, msw)
    resp2 = _make_read_response(0x0801, lsw)
    hmi.ser._read_buffer = resp1 + resp2

    result = hmi.read_float(0x0800)
    assert pytest.approx(result, rel=1e-6) == pi
