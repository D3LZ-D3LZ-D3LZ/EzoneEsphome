# ESPHome Advantage Air Component

Custom ESPHome component for Advantage Air e-zone AC systems.

## Setup

### 1. Add to your ESPHome configuration

```yaml
external_components:
  - source: github://D3LZ-D3LZ-D3LZ/EzoneEsphome
    refresh: 0d

advantage_air:
  id: aa_controller
  uart_id: rs485_bus

uart:
  id: rs485_bus
  tx_pin: GPIO19
  rx_pin: GPIO22
  baud_rate: 57600
```

### 2. Hardware Connection

| Pin | Function |
|-----|----------|
| GPIO19 | RS485 TX |
| GPIO22 | RS485 RX |
| GND | RS485 GND |

## Commands

### Status
```
<U>getSystemData</U=15>
<U>getZoneData?zone=1</U=74>
```

### Control
```
<U>setSystemData?airconOnOff=1&mode=1&fanSpeed=1&centralDesiredTemp=22</U=XX>
<U>setZoneData?zone=1&setting=1</U=XX>
```

## Protocol

- Baud rate: 57600
- Format: XML over serial with CRC checksum
- CRC: CRC-8 with polynomial 0x07
