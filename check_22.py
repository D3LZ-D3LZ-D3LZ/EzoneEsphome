#!/usr/bin/env python3
"""Check CRC for userPercentSetting=22"""

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

cmd = "setZoneData?zone=6&userPercentSetting=22".encode()
crc = crc_lsb(cmd, 0xB2, 0xBA)
print(f"userPercentSetting=22: CRC = 0x{crc:02x}")

# Check what gives CRC 0x02
print()
print("Searching for correct algorithm that gives CRC=0x02 for 22%:")
for init in range(256):
    crc = crc_lsb(cmd, 0xB2, init)
    if crc == 0x02:
        print(f"  init=0x{init:02x}")
