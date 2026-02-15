# Advantage Air ESPHome Controller

ESPHome configuration for controlling Advantage Air AC systems using M5Stack ATOM with RS485.

## Related Resources

- [Advantage Air Ezone Tablet DIY Repair](https://blog.hopefullyuseful.com/blog/advantage-air-ezone-tablet-diy-repair/)
- [Discussion on Hacker News](https://news.ycombinator.com/item?id=41387108)

## Hardware

- **Controller**: M5Stack ATOM (ESP32)
- **RS485 Module**: [ATOM RS485 Base](https://shop.m5stack.com/products/atomic-rs485-base)

## Wiring

### RS485 to AC Controller

| Pin | Function |
|-----|----------|
| 1 | RS422 +/B |
| 2 | RS422 -/A |
| 4 | GND |
| 5 | ~14.2V DC (unloaded) |

> **Note**: Pinout may vary depending on the AC controller model. Check your controller's specifications.

### M5Stack ATOM Pinout

- **GPIO19**: RS485 TX
- **GPIO22**: RS485 RX

## CRC Calculations

The Advantage Air protocol uses custom CRC algorithms. All CRCs use LSB-first bit ordering.

### CRC Parameters by Command Type

| Command Type | Init Value | Poly | Algorithm |
|--------------|------------|------|-----------|
| zoneSetting (on/off) | 0x9B | 0xB2 | LSB-first |
| userPercentSetting (damper %) | 0xBA | 0xB2 | LSB-first |
| desiredTemp (zone target) | 0x62 | 0xB2 | LSB-first |
| setSystemData?mode (Cool/Heat/Fan/Dry) | 0x40 | 0xB2 | LSB-first |
| setSystemData?fanSpeed (Low/Med/High/Auto) | 0x79 | 0xB2 | LSB-first |
| setSystemData?airconOnOff | 0x00 | 0x07 | MSB-first |
| centralDesiredTemp | 0x00 | 0x07 | MSB-first |

### CRC Implementation (C++)

```cpp
// LSB-first CRC (zoneSetting, userPercentSetting, desiredTemp, mode, fanSpeed)
uint8_t crc = INIT_VALUE;  // See table above
for (char c : cmd) {
  crc ^= (uint8_t)c;
  for (int i = 0; i < 8; i++) {
    if (crc & 0x01) crc = (crc >> 1) ^ 0xB2;
    else crc >>= 1;
  }
}

// MSB-first CRC (airconOnOff, centralDesiredTemp)
uint8_t crc = 0;
for (char c : cmd) {
  crc ^= (uint8_t)c;
  for (int i = 0; i < 8; i++) {
    if (crc & 0x80) crc = (crc << 1) ^ 0x07;
    else crc <<= 1;
    crc &= 0xFF;
  }
}
```

## AC Modes

| mode Value | Description |
|------------|-------------|
| 1 | Cool |
| 2 | Heat |
| 3 | Fan |
| 5 | Dry |

## Fan Speeds

| fanSpeed Value | Description |
|----------------|-------------|
| 1 | Low |
| 2 | Medium |
| 3 | High |
| 4 | Auto |

## Zone Configuration

The config supports 7 zones. Each zone can be configured as:
- **Climate Zone**: Temperature sensor, target temp control, on/off switch (zones 1, 2, 3, 7)
- **Damper Zone**: Cover/percentage control only (zones 4, 5, 6)

Customize zone names in the `substitutions` section:

```yaml
substitutions:
  zone1_name: "Kitchen"
  zone2_name: "Master"
  zone3_name: "Guest"
  zone4_name: "Store"
  zone5_name: "Workroom"
  zone6_name: "Study"
  zone7_name: "Theatre"
```

## Features

- Zone temperature monitoring
- Zone on/off control
- Damper percentage control
- Central target temperature
- AC mode control (Cool/Heat/Fan/Dry)
- Fan speed control (Low/Medium/High/Auto)
- MyZone selection
- Real-time status updates from AC

## Home Assistant Integration

After uploading the firmware, the following entities will be available:

### Sensors
- Zone temperatures
- Zone signal strength
- Zone damper percentages
- AC Mode
- Fan Speed
- MyZone

### Switches
- AC Power
- Zone on/off (7 zones)

### Covers
- Zone dampers (7 zones)

### Numbers
- Central target temperature
- Zone target temperatures (zones with climate control)

### Selects
- AC Mode
- Fan Speed
- MyZone
