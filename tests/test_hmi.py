import os
import pytest
from dwin_hmi_py import DwinHMI

#------------------------------------------------------------------------------
# Configuration: pick up serial port from env var or default.
#------------------------------------------------------------------------------
PORT      = os.getenv("HMI_PORT", "/dev/ttyUSB0")
BAUDRATE  = int(os.getenv("HMI_BAUD", 115200))
TIMEOUT   = float(os.getenv("HMI_TIMEOUT", 0.5))

#------------------------------------------------------------------------------
# Fixture that returns a live DwinHMI instance
#------------------------------------------------------------------------------
@pytest.fixture(scope="module")
def hmi():
    """
    Returns a DwinHMI object connected to a real serial port.
    Make sure your DGUS HMI is powered and wired before running these tests.
    """
    h = DwinHMI(port=PORT, baudrate=BAUDRATE, timeout=TIMEOUT)
    yield h
    # Optionally, you can clean up/reset here.

#------------------------------------------------------------------------------
# Marker for integration tests
#------------------------------------------------------------------------------
def pytest_configure(config):
    config.addinivalue_line(
        "markers", "integration: mark test as requiring real HMI hardware"
    )

#------------------------------------------------------------------------------
# Test writing and reading a 16-bit register
#------------------------------------------------------------------------------
@pytest.mark.integration
def test_write_read_register(hmi):
    vp_addr = 0x07D0
    test_val = 0x1234

    # write
    hmi.write_register(vp_addr, test_val)

    # read back
    result = hmi.read_register(vp_addr)
    assert result == test_val, f"expected 0x{test_val:04X}, got 0x{result:04X}"

#------------------------------------------------------------------------------
# Test writing and reading a 32-bit float
#------------------------------------------------------------------------------
@pytest.mark.integration
def test_write_read_float(hmi):
    vp_addr = 0x0800
    test_f  = 3.1415926

    # write
    hmi.write_float(vp_addr, test_f)

    # read back
    result = hmi.read_float(vp_addr)
    assert pytest.approx(result, rel=1e-6) == test_f
