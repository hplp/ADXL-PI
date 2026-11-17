# ADXL362 Accelerometer Logging (Raspberry Pi)

Python tools for reading an Analog Devices **ADXL362** 3-axis MEMS accelerometer over SPI from a Raspberry Pi, logging acceleration and temperature, and plotting the results.

This code is the sensor-side groundwork for a **sensor-enabled UHF RFID tag**, where the ADXL362 will eventually be read over the air through an **EM4325** RFID chip acting as an SPI master (see [Roadmap](#roadmap-rfid-integration)).

---

## Repository layout

```
.
├── ADXL_Read_V1/          # Original version: raw sensor counts, ~100 Hz polling
│   ├── ADXL362.py         # SPI driver
│   └── <logging script>   # 10 s capture, plots x/y/z
│
└── ADXL_Read_Adjusted/    # Revised version: unit conversion, CSV export, ~10 Hz polling
    ├── ADXL362.py         # SPI driver with scaling + temperature conversion
    └── <logging script>   # 10 s capture, prints registers, saves vibration.csv, plots x/y/z
```

### Version differences

| | `ADXL_Read_V1` | `ADXL_Read_Adjusted` |
|---|---|---|
| Acceleration output | Raw counts | Counts ÷ 1000 (≈ g) |
| Z-axis | Raw | Hand-tuned ±500 count offset |
| Temperature output | Raw counts | Empirical formula |
| Nominal sample rate | 100 Hz | 10 Hz |
| Prints register dump | No | Yes (`0x20`–`0x2E`) |
| Saves CSV | No | Yes (`vibration.csv`) |

**Recommendation:** `ADXL_Read_V1/ADXL362.py` is the cleaner driver (no hard-coded offsets). Do unit conversion in the script instead of the driver.

---

## Hardware

### Parts
- Raspberry Pi with SPI enabled (`sudo raspi-config` → Interface Options → SPI)
- ADXL362 breakout board

### Wiring (default: `/dev/spidev0.1`, i.e. SPI0 / CE1)

| ADXL362 | Raspberry Pi pin | GPIO |
|---|---|---|
| VS / VDDIO | Pin 1 (3.3 V) | — |
| GND | Pin 6 | — |
| MOSI (SDI) | Pin 19 | GPIO 10 |
| MISO (SDO) | Pin 21 | GPIO 9 |
| SCLK | Pin 23 | GPIO 11 |
| CS | Pin 26 | GPIO 7 (CE1) |

To use CE0 instead, construct the driver with `ADXL362.ADXL362(device=0, ce_pin=0)` and wire CS to pin 24 (GPIO 8).

---

## Installation

```bash
pip install spidev pandas matplotlib
```

---

## Usage

From inside either version folder:

```bash
python <logging script>.py
```

The script will:
1. Soft-reset the ADXL362 and enable measurement mode
2. Sample x, y, z and temperature for ~10 seconds
3. Show scatter plots of each axis vs. time
4. *(Adjusted only)* write the samples to `vibration.csv`

### Driver API (`ADXL362.py`)

| Method | Description |
|---|---|
| `ADXL362(device=0, ce_pin=1)` | Open SPI device and soft-reset the sensor (writes `0x52` to `0x1F`) |
| `begin_measure()` | Set measurement mode in `POWER_CTL` (`0x2D`) |
| `read_x()`, `read_y()`, `read_z()` | Read one axis (registers `0x0E`, `0x10`, `0x12`) |
| `read_temp()` | Read temperature register (`0x14`) |
| `read_xyz()` | Read x, y, z, temperature (see known issues — not a true burst read) |
| `check_all_regs()` | Burst-read 15 configuration registers from `0x20` |
| `spi_read_reg()` / `spi_write_reg()` | Single-register access (`0x0B` read / `0x0A` write) |

### Units

In the default ±2 g range, **1 count ≈ 1 mg**. At rest and flat, expect roughly `x ≈ 0`, `y ≈ 0`, `z ≈ +1000` counts (1 g from gravity).

---

## Known issues

1. **Chip-select polarity bug (both versions).** `begin_measure()` and `read_xyz()` set `spi.cshigh = True`, making CS active-high. The ADXL362's CS is active-low, so reads after `begin_measure()` may return garbage. Remove those lines.
2. **`read_xyz()` is not a burst read.** It performs separate transactions per axis, so x, y and z come from different samples. A single `[0x0B, 0x0E] + 6 dummy bytes` transfer fixes this.
3. **Double temperature conversion (Adjusted).** `read_xyz()` applies the temperature formula to a value `read_temp()` already converted.
4. **Uncalibrated conversions (Adjusted).** The z-axis ±500 offset and the temperature formula are empirical, not from the datasheet.
5. **Timestamps are nominal.** `prog_time` is incremented by the sleep interval and never reads the clock, so it drifts from real time. Use `time.perf_counter()` instead.
6. **Sample rate is limited.** The sensor's default output data rate is 100 Hz, and Python polling adds overhead. For real vibration measurements, raise the ODR in `FILTER_CTL` (`0x2C`) and read from the on-chip FIFO.
7. **Stale comments.** The commented-out scale factor `2.048 * 2 / 2**20` belongs to a 20-bit sensor (ADXL355), not the 12-bit ADXL362.

---


The register commands in this repo map directly to SendSPI payloads:

| Operation | SendSPI payload | Response bytes |
|---|---|---|
| Soft reset | `0A 1F 52` | 0 |
| Enable measurement | `0A 2D 02` | 0 |
| Burst-read x, y, z | `0B 0E` | 6 |
| Read temperature | `0B 14` | 2 |

| EM4325 pin | ADXL362 |
|---|---|
| 3 P0_MOSI | MOSI |
| 4 P1_MISO | MISO |
| 5 P2_SCLK | SCLK |
| 6 P3_CS (active low) | CS |
| 7 VBAT | VS / VDDIO |
| 8 VSS | GND |

The tag antenna is being designed separately in Ansys HFSS and must be impedance-matched to the EM4325 with the battery and sensor PCB included in the model.
