# Flamingo schematic build plan

Updated: 2026-11-15. Checked against the saved active KiCad hierarchy. Checked boxes mean drawn or named, not electrically validated. See [COMPONENTS.md](COMPONENTS.md) for component choices and the current connection record.

## Current sheet inventory

| Page | Saved state | Remaining work |
|---|---|---|
| System overview | Nine functional sheet boxes; USB power and laser links drawn | Connect SD and USB data at the parent; camera, FC and expansion interfaces |
| Power distribution | J4 XT30 input; protection/buck child sheets; U2 TPS2116 and U3 TPS62162 support | Local mux capacitors, USB protection and complete power review |
| Battery input protection | F1 MF-R160, D2 SS34, D1 P6KE20A and C8 EEEFK1V470P | Confirm bulk-capacitor selection/assembly plan, fault/transient and thermal ratings |
| 4S to 5 V buck | U4 TPS54302; L2, C3-C7 and R11-R12 | Inductor MPN/value conflict, compensation/feedback and capacitor ratings |
| ESP32-S3 core | U1 N16R8, power/ground and USB/SD/laser labels | EN/reset, BOOT, decoupling, camera/FC/expansion and remaining parent wiring |
| USB programming / JTAG | J3 DEALON USB-TYPE-C-017, R6/R7 CC pull-downs, joined D+/D- copies | Shell grounding, ESD, input protection and parent USB data wiring |
| Arducam Mega SPI camera | Empty placeholder; parent still named OV5640 | Entire camera connector/SPI/decoupling circuit |
| microSD | J2 TF-115-BCP9, R1-R5 pull-ups, grounded shell, CD no-connect; layout cleaned | Local decoupling and parent SPI wiring |
| STA-M020X laser | J1 five-contact connector, supply/ground and UART labels | Resolve TX/RX pin assignment against module manual, verify harness and ENO |
| Flight-controller telemetry | Empty placeholder | Connector, GPIO1/2 UART and ground interfaces |
| GPIO / I2C / SPI expansion | Empty placeholder | Headers, I2C pull-ups as needed, SPI sharing and EXT_CS bias |
| Optional UART debug | Empty placeholder | Optional GPIO43/44 and GND header |

Inactive camera_tarpfinder, power_tarpfinder, usb_tarpfinder, GPS and usb_debug files are not in the active hierarchy; they have not been treated as implemented circuits or renamed.

## Naming completed

- [x] Give components unique R/C/L/D/F/J/U references; enter passive magnitudes in Value fields rather than reference names.
- [x] Preserve component UUIDs so schematic-to-PCB association can survive reference updates.
- [x] Preserve all original net names, hierarchy port names/directions and sheet names. Current CAD uses global `5V` and `3V3`, local `Buck_5V`, and the original battery/buck port names.
- [ ] Review existing battery/buck port directions separately; they were not changed in this component-naming pass.
- [ ] Change USB_D_P/N to bidirectional on both child labels and matching parent pins when finishing USB; original definitions retained for now.
- [ ] Core parent SD_MOSI still needs output direction to match its child label; original definition retained.
- [ ] Top-level camera box still says OV5640 although the selected module is Arducam Mega; original sheet name retained.
- [x] Correct R6/R7 footprints to `R_0402_1005Metric` for the existing C25905 selection (JLC lists 0402 / 5.1k).

These edits do not add the missing top-level wires or complete unfinished circuits. Update the PCB from the schematic after reviewing reference/footprint changes; the PCB has not been modified in this pass.

## Power distribution and protection

- [x] J4: XT30PW-M30.G.Y; child battery input `Unprotected In`.
- [x] F1, D2, D1 and C8 input protection is drawn; child output `Protected in`.
- [x] U4 TPS54302 support circuit is drawn; output `5Vout` / parent local `Buck_5V`.
- [x] U2: USB_5V -> VIN1 and MODE; Buck_5V -> VIN2; R9 33k / R8 10k PR1 divider; VOUT pins joined as global `5V`. ST remains unused.
- [x] U3: global `5V` -> VIN/EN; L1 2.2uH; C1 10uF, C2 22uF; R10 100k PG pull-up. VOS -> global `3V3`; EP/AGND/PGND/FB -> GND.
- [ ] Resolve L1/L2: both currently cite C1046 despite intended values 2.2uH and 10uH. Select separate rated power inductors with adequate saturation/RMS current and verify footprints; this BOM cannot be ordered as-is.
- [ ] Validate R11/R12 feedback and all capacitor/inductor ratings against the exact regulator designs.
- [ ] Add local TPS2116 input/output capacitors and USB input current/inrush protection.
- [ ] Resolve C8: current CAD uses EEEFK1V470P / C178565; earlier existing-parts hand-soldered capacitor plan is not the same selection.
- [ ] Validate USB current capability, combined +3V3 peaks, startup, source switching, thermal performance, battery fault protection and undervoltage behavior.

## Core and USB

- [x] U1 ESP32-S3-WROOM-1-N16R8 is placed; global `3V3` and GND drawn.
- [x] Core labels: SD_CLK GPIO40, SD_MOSI GPIO41, SD_MISO GPIO42, SD_CS GPIO47; USB_D_N GPIO19, USB_D_P GPIO20; LASER_TX GPIO38, LASER_RX GPIO39.
- [x] J3: VBUS copies joined, ground contacts grounded, D+ copies joined and D- copies joined.
- [x] R6/R7: independent 5.1k pull-downs on CC2/CC1; 0402 / C25905.
- [ ] Ground J3 shell pads 1-4; explicitly mark unused SBU contacts.
- [ ] Add USB ESD protection; proposed USBLC6-2SC6 remains unplaced.
- [ ] Wire USB_D_P/N between USB and core at the parent. Route the PCB pair over continuous ground with 90-ohm differential impedance and minimal stubs/vias.
- [ ] Add core decoupling, EN reset network, BOOT and RESET controls; preserve antenna keepout and N16R8 memory-pin restrictions.

## Camera

- [ ] Draw Arducam Mega 5 MP AF SPI camera interface. No camera circuitry currently exists in the active child sheet.
- [ ] Confirm connector/harness; 1x6 header was proposed and Micro-Fit locking alternative discussed, neither is placed. Assign a free reference; J2 is microSD.
- [ ] Planned GPIO8 SCK, GPIO9 MOSI, GPIO10 MISO, GPIO6 CS on a dedicated bus; add matching parent interfaces/wiring.
- [ ] Add 10k CS pull-up and local 100nF + 10uF; include camera in +3V3 current budget.
- [ ] Validate SDK JPEG capture/readout, autofocus and cable retention.

## microSD

- [x] J2 TF-115-BCP9 / C720505, with existing imported footprint.
- [x] R1 DAT2, R2 CS, R3 MOSI, R4 MISO, R5 DAT1: 10k pull-ups to global `3V3`; 0805 / C17414. No CLK pull-up.
- [x] Pin 4 global `3V3`; pin 6 and shell pins 10-13 GND; mechanical CD pin 9 no-connect.
- [x] Child ports: SD_CLK/MOSI/CS inputs; SD_MISO output. DAT1/DAT2 use local labels and have no MCU connection.
- [x] Separate pull-up bank and socket with nonoverlapping fields/labels and explanatory notes.
- [ ] Add local supply capacitors near the socket.
- [ ] Connect existing SD parent pins to core parent pins; these remain disconnected at the top level.
- [ ] If adding expansion to this bus, use separate EXT_CS on GPIO48 and initialize SD into SPI mode first.

## Laser, telemetry and expansion

- [x] J1 STA-M020X connector and preliminary UART/power wiring are drawn.
- [ ] Fix/review laser TX/RX assignment: saved LASER_TX/GPIO38 reaches J1 pin 3 and LASER_RX/GPIO39 reaches pin 4; the supplied manual identifies pin 3 as module TXD and pin 4 as module RXD. These need crossing relative to the saved core-perspective names. No pin swap was made during this naming pass.
- [ ] Confirm laser module connector pin order, UART logic voltage, ENO treatment and local decoupling.
- [ ] Draw AIO UART4 telemetry: GPIO1 TX -> FC RX, GPIO2 RX <- FC TX, GND only; no FC power on cable.
- [ ] Draw expansion +3V3/GND, shared SPI and independent EXT_CS; GPIO4/5 may serve I2C after pull-up/load review.
- [ ] Draw optional debug header GPIO43 TX, GPIO44 RX and GND, or explicitly omit it.

## Before PCB release

- [ ] Resolve remaining ERC findings; a clean export is not proof of an electrically complete schematic.
- [ ] Verify each MPN, value, footprint/pad mapping and assembly selection, especially inductors and connectors.
- [ ] Update PCB from schematic and review reference changes, then finish placement/routing and DRC.
- [ ] Confirm 50x80mm target / 50x100mm maximum, connector access, mounting and antenna clearance.
- [ ] Test rails, source selection, SD writes and timestamped camera/laser/FC operation on hardware.

References: [SD pull-ups](https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-reference/peripherals/sd_pullup_requirements.html), [SD SPI sharing](https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-reference/peripherals/sdspi_share.html), [TPS54302](https://www.ti.com/lit/ds/symlink/tps54302.pdf), [TPS2116](https://www.ti.com/lit/ds/symlink/tps2116.pdf), [TPS6216x](https://www.ti.com/lit/ds/symlink/tps62160.pdf), [C25905 package](https://jlcpcb.com/partdetail/C25905).
