#!/usr/bin/env python3
"""Verify CRC against sniffed values"""

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

# Sniffed values
sniffed = [
    ("setZoneData?zone=6&userPercentSetting=10", 0x5b),
    ("setZoneData?zone=6&userPercentSetting=15", 0x9d),
    ("setZoneData?zone=6&zoneSetting=0", 0xb3),
    ("setZoneData?zone=6&zoneSetting=1", 0x8d),
]

print("Verifying LSB-first poly=0xB2 init=0xBA:")
print("=" * 60)
for cmd, expected in sniffed:
    crc = crc_lsb(cmd.encode(), 0xB2, 0xBA)
    status = "✓" if crc == expected else f"✗ (got 0x{crc:02x})"
    print(f"  {cmd}")
    print(f"    Expected: 0x{expected:02x}, Got: 0x{crc:02x} {status}")
    print()
