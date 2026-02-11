#!/usr/bin/env python3
"""Find correct CRC for zoneSetting commands"""

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

# Sniffed zoneSetting values
zone_tests = [
    ("setZoneData?zone=6&zoneSetting=1", 0x8d),
    ("setZoneData?zone=6&zoneSetting=0", 0xb3),
]

print("Finding zoneSetting CRC:")
print("=" * 60)

# Test LSB-first with different init values
for init in [0x00, 0x9B, 0xFF, 0xBA, 0x7F]:
    for poly in [0x07, 0x31, 0xB2, 0x39, 0x8C]:
        cmd, expected = zone_tests[0]
        crc = crc_lsb(cmd.encode(), poly, init)
        if crc == expected:
            # Verify with second test
            cmd2, expected2 = zone_tests[1]
            crc2 = crc_lsb(cmd2.encode(), poly, init)
            if crc2 == expected2:
                print(f"FOUND! LSB poly=0x{poly:02x} init=0x{init:02x}")
                print(f"  {cmd} -> 0x{crc:02x} (expected 0x{expected:02x}) ✓")
                print(f"  {cmd2} -> 0x{crc2:02x} (expected 0x{expected2:02x}) ✓")

print()
print("Trying MSB-first:")
for init in [0x00, 0xFF, 0x7F]:
    for poly in [0x07, 0x31]:
        cmd, expected = zone_tests[0]
        crc = crc_msb(cmd.encode(), poly, init)
        if crc == expected:
            cmd2, expected2 = zone_tests[1]
            crc2 = crc_msb(cmd2.encode(), poly, init)
            if crc2 == expected2:
                print(f"FOUND! MSB poly=0x{poly:02x} init=0x{init:02x}")
                print(f"  {cmd} -> 0x{crc:02x} (expected 0x{expected:02x}) ✓")
                print(f"  {cmd2} -> 0x{crc2:02x} (expected 0x{expected2:02x}) ✓")

# Test zone 1 and zone 2 from earlier sniffs
print()
print("Testing zone 1 and 2 from earlier:")
zone1_tests = [
    ("setZoneData?zone=1&zoneSetting=1", 0x2a),
    ("setZoneData?zone=1&zoneSetting=0", 0x14),
]
zone2_tests = [
    ("setZoneData?zone=2&zoneSetting=1", 0x1e),
    ("setZoneData?zone=2&zoneSetting=0", 0x20),
]

for name, tests in [("Zone 1", zone1_tests), ("Zone 2", zone2_tests)]:
    for init in [0x00, 0x9B, 0xFF]:
        for poly in [0x07, 0x31, 0xB2]:
            cmd1, exp1 = tests[0]
            crc1 = crc_lsb(cmd1.encode(), poly, init)
            cmd2, exp2 = tests[1]
            crc2 = crc_lsb(cmd2.encode(), poly, init)
            if crc1 == exp1 and crc2 == exp2:
                print(f"{name}: LSB poly=0x{poly:02x} init=0x{init:02x} ✓")
