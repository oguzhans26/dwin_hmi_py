# example.py

from dwin_hmi_py import DwinHMI

def main():
    # Configure the serial connection to your HMI (adjust the port as needed)
    hmi = DwinHMI(port='COM11', baudrate=115200, timeout=0.2)

    # Write the value 0x0005 to register 0x5000
    hmi.write_register(0x5000, 0x0005)

    # Read back and print the value at register 0x07D0
    val = hmi.read_register(0x07D0)
    print(f"Register 0x07D0 = 0x{val:04X}")

    # Write a float (3.1415) to address 0x0800 and read it back
    hmi.write_float(0x0800, 3.1415)
    f = hmi.read_float(0x0800)
    print(f"Float at 0x0800 = {f:.4f}")

if __name__ == "__main__":
    main()
