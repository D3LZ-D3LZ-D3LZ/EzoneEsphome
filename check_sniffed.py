#!/usr/bin/env python3
"""Verify all sniffed userPercentSetting values"""

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

# From sniffer
sniffed = [
    ("setZoneData?zone=6&userPercentSetting=10", 0x5b),
    ("setZoneData?zone=6&userPercentSetting=15", 0x9d),
]

print("Verifying sniffed values with LSB poly=0xB2 init=0xBA:")
for cmd, expected in sniffed:
    crc = crc_lsb(cmd.encode(), 0xB2, 0xBA)
    status = "✓" if crc == expected else f"✗ (got 0x{crc:02x})"
    print(f"  {cmd}")
    print(f"    Expected: 0x{expected:02x}, Got: 0x{crc:02x} {status}")

print()
print("Checking all possible 2-digit percentages:")

# Check what init values work for all percentages
for percent in [10, 15, 20, 22, 25, 30, 36, 40, 50]:
    cmd = f"setZoneData?zone=6&userPercentSetting={percent}".encode()
    crc = crc_lsb(cmd, 0xB2, 0xBA)
    print(f"  {percent}% -> 0x{crc:02x}")
