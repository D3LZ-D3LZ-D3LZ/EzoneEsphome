#!/usr/bin/env python3
"""Calculate CRC-8 for Advantage Air commands"""

def crc8(data):
    crc = 0
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x80:
                crc = (crc << 1) ^ 0x07
            else:
                crc <<= 1
            crc &= 0xFF
    return crc

commands = [
    # Zone settings
    ("setZoneData?zone=1&setting=1", "Zone 1 Open"),
    ("setZoneData?zone=1&setting=0", "Zone 1 Close"),
    ("setZoneData?zone=2&setting=1", "Zone 2 Open"),
    ("setZoneData?zone=2&setting=0", "Zone 2 Close"),
    ("setZoneData?zone=3&setting=1", "Zone 3 Open"),
    ("setZoneData?zone=3&setting=0", "Zone 3 Close"),
    ("setZoneData?zone=4&setting=1", "Zone 4 Open"),
    ("setZoneData?zone=4&setting=0", "Zone 4 Close"),
    ("setZoneData?zone=5&setting=1", "Zone 5 Open"),
    ("setZoneData?zone=5&setting=0", "Zone 5 Close"),
    ("setZoneData?zone=6&setting=1", "Zone 6 Open"),
    ("setZoneData?zone=6&setting=0", "Zone 6 Close"),
    ("setZoneData?zone=7&setting=1", "Zone 7 Open"),
    ("setZoneData?zone=7&setting=0", "Zone 7 Close"),
    
    # System
    ("setSystemData?airconOnOff=1", "AC ON"),
    ("setSystemData?airconOnOff=0", "AC OFF"),
    ("setSystemData?mode=1", "Mode Cool"),
    ("setSystemData?mode=2", "Mode Heat"),
    ("setSystemData?mode=3", "Mode Fan"),
    ("setSystemData?fanSpeed=1", "Fan Low"),
    ("setSystemData?fanSpeed=2", "Fan Medium"),
    ("setSystemData?fanSpeed=3", "Fan High"),
    ("setSystemData?centralDesiredTemp=21", "Temp 21"),
    ("setSystemData?centralDesiredTemp=22", "Temp 22"),
    ("setSystemData?centralDesiredTemp=23", "Temp 23"),
    
    # Zone temps
    ("setZoneData?zone=1&desiredTemp=21", "Zone 1 Temp 21"),
    ("setZoneData?zone=2&desiredTemp=21", "Zone 2 Temp 21"),
    ("setZoneData?zone=3&desiredTemp=21", "Zone 3 Temp 21"),
    ("setZoneData?zone=7&desiredTemp=21", "Zone 7 Temp 21"),
    
    # Percentages
    ("setZoneData?zone=4&userPercentSetting=50", "Zone 4 Percent 50"),
    ("setZoneData?zone=4&userPercentSetting=80", "Zone 4 Percent 80"),
    ("setZoneData?zone=4&userPercentSetting=100", "Zone 4 Percent 100"),
    ("setZoneData?zone=5&userPercentSetting=50", "Zone 5 Percent 50"),
    ("setZoneData?zone=5&userPercentSetting=80", "Zone 5 Percent 80"),
    ("setZoneData?zone=5&userPercentSetting=100", "Zone 5 Percent 100"),
    ("setZoneData?zone=6&userPercentSetting=50", "Zone 6 Percent 50"),
    ("setZoneData?zone=6&userPercentSetting=80", "Zone 6 Percent 80"),
    ("setZoneData?zone=6&userPercentSetting=100", "Zone 6 Percent 100"),
]

print("CRC-8 Values for Advantage Air Commands")
print("=" * 60)
for cmd, name in commands:
    crc = crc8(cmd.encode('ascii'))
    print(f"{name:25} | {cmd:40} | ={crc:02x}")
