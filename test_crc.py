#!/usr/bin/env python3
"""Find correct CRC algorithm for userPercentSetting"""

def crc_lsb(data, poly, init):
    crc = init
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x01:
                crc = (crc >> 1) ^ poly
            else:
                crc >>= 1
    return crc & 0xFF

def crc_msb(data, poly, init):
    crc = init
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x80:
                crc = (crc << 1) ^ poly
            else:
                crc <<= 1
            crc &= 0xFF
    return crc

def reverse_bits_byte(b):
    return int('{:08b}'.format(b)[::-1], 2)

def reverse_nibbles(b):
    return ((b & 0x0F) << 4) | ((b & 0xF0) >> 4)

def reverse_bits_2bit(b):
    return ((b & 0x55) << 1) | ((b & 0xAA) >> 1)

# Test cases from logs
test_cases = [
    ("setZoneData?zone=6&userPercentSetting=36", 0x3a),
    ("setZoneData?zone=6&userPercentSetting=22", 0x02),  # from our calc
]

print("Testing different CRC configurations:")
print("=" * 60)

# Test LSB-first with different init values
for init in [0x00, 0xBA, 0xFF, 0x9B]:
    for poly in [0x07, 0x31, 0xB2, 0x39]:
        cmd = "setZoneData?zone=6&userPercentSetting=36".encode()
        crc = crc_lsb(cmd, poly, init)
        if crc == 0x3a:
            print(f"FOUND! LSB-first poly=0x{poly:02x} init=0x{init:02x} for 36%")
            # Test with 22%
            cmd2 = "setZoneData?zone=6&userPercentSetting=22".encode()
            crc2 = crc_lsb(cmd2, poly, init)
            print(f"  -> 22% gives CRC=0x{crc2:02x}")
            # Test with 100
            cmd3 = "setZoneData?zone=6&userPercentSetting=100".encode()
            crc3 = crc_lsb(cmd3, poly, init)
            print(f"  -> 100% gives CRC=0x{crc3:02x}")

print()
print("Testing byte reversal on result:")

# Test what byte reversal does to 0x3b (our calc for 36%)
print(f"  reverse_bits_byte(0x3b) = 0x{reverse_bits_byte(0x3b):02x}")
print(f"  reverse_nibbles(0x3b) = 0x{reverse_nibbles(0x3b):02x}")

# Test the exact byte reversal from the C++ code
def byte_reverse_cpp_style(b):
    b = ((b & 0x0F) << 4) | ((b & 0xF0) >> 4)  # nibble swap
    b = ((b & 0x33) << 2) | ((b & 0xCC) >> 2)  # 2-bit swap
    b = ((b & 0x55) << 1) | ((b & 0xAA) >> 1)  # bit swap
    return b

print(f"  cpp_style_reversal(0x3b) = 0x{byte_reverse_cpp_style(0x3b):02x}")

# Test MSB-first
print()
print("Testing MSB-first:")
cmd = "setZoneData?zone=6&userPercentSetting=36".encode()
for poly in [0x07, 0x31]:
    for init in [0x00, 0xBA, 0xFF]:
        crc = crc_msb(cmd, poly, init)
        print(f"  MSB poly=0x{poly:02x} init=0x{init:02x}: CRC=0x{crc:02x}")
