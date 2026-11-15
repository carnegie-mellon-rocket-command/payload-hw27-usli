# Flamingo schematic build plan

Updated: 2026-11-15. Checked against the saved active KiCad hierarchy. Checked boxes mean drawn or named, not electrically validated. See [COMPONENTS.md](COMPONENTS.md) for component choices and the current connection record.

## Current sheet inventory

| Page | Saved state | Remaining work |
|---|---|---|
| System overview | Nine functional sheet boxes; USB power and laser links drawn | Connect SD and USB data at the parent; camera, FC and expansion interfaces |
| Power distribution | Circuit and component verification complete per user | Final electrical check and layout |
| Battery input protection | Circuit verified per user; C8 existing 47uF part for hand soldering | Included in final power check and layout |
| 4S to 5 V buck | Circuit verified per user; C3 replacement resolved | Included in final power check and layout |
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

Power drawing, component selection and verification are complete per the user's review. C3 has been corrected. The earlier detailed power checklist is consolidated here; this records the user's completed review rather than a new independent validation.

- [x] Complete power circuitry and component verification: 4S input protection, TPS54302 buck, TPS2116 source selection and TPS62162 3.3V stage, including capacitor selections.
- [ ] Perform the final electrical check against the latest saved schematic/BOM, including net connections, ratings and ERC findings relevant to power.
- [ ] Complete PCB layout and final footprint/placement checks; retain existing net names.

Capacitor assembly: only C8 (47uF input bulk) is hand-soldered, using the user's existing part rated at least 35V. No exact purchase MPN is required. Exclude C8 from the JLC assembly BOM/CPL/selection, but keep its full BOM entry and PCB pads. C11 is now the user-selected 100uF non-polarized capacitor and remains in factory assembly selection. C8 is radial; select its Capacitor_THT:CP_Radial footprint from the measured body diameter and lead spacing. Match both actual packages during layout. C9/C10 remain the drawn 4.7uF input bypass capacitors.

## Core and USB

- [x] U1 ESP32-S3-WROOM-1-N16R8 is placed; global `3V3` and GND drawn.
- [x] Core labels: SD_CLK GPIO40, SD_MOSI GPIO41, SD_MISO GPIO42, SD_CS GPIO47; USB_D_N GPIO19, USB_D_P GPIO20; LASER_TX GPIO38, LASER_RX GPIO39.
- [x] J3: VBUS copies joined, ground contacts grounded, D+ copies joined and D- copies joined.
- [x] R6/R7: independent 5.1k pull-downs on CC2/CC1; 0402 / C25905.
- [ ] Ground J3 shell pads 1-4; explicitly mark unused SBU contacts.
- [ ] Add USB ESD protection; proposed USBLC6-2SC6 remains unplaced.
- [ ] Wire USB_D_P/N between USB and core at the parent. Route the PCB pair over continuous ground with 90-ohm differential impedance and minimal stubs/vias.
- [ ] Add core decoupling, EN reset network, BOOT and RESET controls; preserve antenna keepout and N16R8 memory-pin restrictions.

## Camera - `schematics/camera.kicad_sch`

**Decided:** Arducam Mega 5MP autofocus SPI camera (B0401 / Amazon B0BW7MDVHK), JPEG still capture, dedicated SPI bus and 3.3V module power/logic. The module handles internal sensor rails, timing and frame buffering. External DVP, SCCB, XCLK and sensor-level translators are not part of this interface.

**Drawn:** no components or ports yet; the active camera sheet remains a placeholder.

| Camera connection | Proposed ESP32 GPIO | Camera-sheet port direction |
|---|---|---|
| SCK | GPIO8 | Input |
| MOSI | GPIO9 | Input |
| MISO | GPIO10 | Output |
| CS, active low | GPIO6 | Input |
| VCC | Existing regulated 3.3V net | Power connection |
| GND | GND | Power connection |

- [ ] Choose/place a six-contact connector and assign a free J reference; J2 is already microSD. The simple prototype option is a 1x6 2.54mm vertical male THT header, `Connector_Generic:Conn_01x06` with `Connector_PinHeader_2.54mm:PinHeader_1x06_P2.54mm_Vertical`.
- [ ] If choosing the locking option discussed, use Molex Micro-Fit 3.0 43045-0600 board header with 43025-0600 cable housing and suitable crimp contacts. It is 2x3 / 3mm pitch and needs its own symbol/footprint and adapter harness. It does not mate directly with the camera connector.
- [ ] Verify the actual camera harness. The module-side connector is listed as XH2.54-6P; board-side female jumper sockets suit the simple pin-header option. Do not infer signal order from wire color.
- [ ] For the proposed 1x6 header, use pads 1 VCC, 2 GND, 3 SCK, 4 MISO, 5 MOSI, 6 CS, after confirming the harness. If selecting Micro-Fit, define its numbered pad map separately; do not assume the linear header order carries over.
- [ ] Wire the connector to the four core GPIOs above and the existing 3.3V/GND nets. Preserve existing net names; new camera port names must match between child labels, core and parent sheet pins.
- [ ] Add a 10k CS pull-up to 3.3V so the camera is deselected during reset.
- [ ] Add local 100nF + 10uF supply bypass. Prefer matching 0805 parts where appropriate; record exact value/voltage/MPN/footprint.
- [ ] Draw matching camera and core ports, then connect them at the parent. Retitle the obsolete OV5640 box only when intentionally updating that sheet name.

**Bring-up after the schematic:** use Arducam Mega SDK/protocol, not the parallel esp32-camera driver. Start at a low SPI clock and small image, then test JPEG capture/readout up to the documented 8MHz SPI limit, full-resolution decode memory, autofocus and image sharpness. Measure capture latency and verify cable retention separately during layout/hardware work.

## microSD

- [x] J2 TF-115-BCP9 / C720505, with existing imported footprint.
- [x] R1 DAT2, R2 CS, R3 MOSI, R4 MISO, R5 DAT1: 10k pull-ups to global `3V3`; 0805 / C17414. No CLK pull-up.
- [x] Pin 4 global `3V3`; pin 6 and shell pins 10-13 GND; mechanical CD pin 9 no-connect.
- [x] Child ports: SD_CLK/MOSI/CS inputs; SD_MISO output. DAT1/DAT2 use local labels and have no MCU connection.
- [x] Separate pull-up bank and socket with nonoverlapping fields/labels and explanatory notes.
- [ ] Add local supply capacitors near the socket.
- [x] Connect SD parent pins to core parent pins. Top-level sheet boxes/pins/wires snapped to the 50mil (1.27mm) grid; exported netlist verifies all four SD signals connect separately to the intended core pads.
- [ ] If adding expansion to this bus, use separate EXT_CS on GPIO48 and initialize SD into SPI mode first.

## Laser - `schematics/laser.kicad_sch`

**Drawn:** J1 five-contact connector, supply/ground and preliminary LASER_TX/LASER_RX connections. Core labels use GPIO38 TX and GPIO39 RX.

| Module contact per supplied manual | Intended connection |
|---|---|
| 1 GND | GND |
| 2 Vin | Selected regulated 5V rail |
| 3 TXD, output from module | ESP32 GPIO39 RX / LASER_RX |
| 4 RXD, input to module | ESP32 GPIO38 TX / LASER_TX |
| 5 ENO | Leave unused pending manufacturer clarification |

- [ ] Review/correct preliminary J1 TX/RX assignments against the table. Earlier saved wiring reached pin 3 from LASER_TX and pin 4 from LASER_RX; verify the latest saved version before editing.
- [ ] Confirm received module label, connector contact order and factory 3.3V UART setting. Supply voltage and logic voltage are different specifications.
- [ ] Settle the actual connector/harness; the existing five-pin JST GH footprint is a candidate, not proof of a mechanical match. If using a six-contact carrier connector, explicitly mark the spare contact unused.
- [ ] Give ENO an intentional no-connect until its function is confirmed, add local supply bypass and match core/laser/parent port directions.

Bring-up: begin with the manual's 19200-baud defaults and confirmed framing/address; validate checksums, result validity, units and stale-data handling. See COMPONENTS.md for protocol examples and the manual's inconsistent model naming.

## Flight-controller telemetry - `schematics/fc_telemetry.kicad_sch`

**Decided:** external MicoAir743v2-AIO-45A supplies navigation/attitude; Flamingo uses its own power branch. GPS/compass remains connected to the AIO, not Flamingo.

**Drawn:** placeholder/note only; no connector or electrical ports yet.

| Telemetry connection | Flamingo GPIO | Telemetry-sheet direction |
|---|---|---|
| FC_UART_TX: Flamingo -> AIO UART4 RX | GPIO1 TX | Input |
| FC_UART_RX: AIO UART4 TX -> Flamingo | GPIO2 RX | Output |
| Common ground | GND | Ground connection |

Directions are relative to the telemetry sheet; the corresponding core ports have the opposite directions.

- [ ] Select/place a three-contact connector for TX, RX and GND; choose its footprint and mating harness. A locking cable connector is a candidate for flight installation.
- [ ] Wire GPIO1 TX -> AIO UART4 RX, AIO UART4 TX -> GPIO2 RX, plus GND. Do not carry the FC's 5V supply on this link.
- [ ] Add matching child labels, core ports and parent sheet pins/wires. State TX/RX direction from Flamingo's perspective in the connector note.
- [ ] Correct any placeholder note still referring to MicoAir405v2; the selected FC is MicoAir743v2-AIO-45A.
- [ ] Check actual FC UART4 pad/contact names and non-inverted 3.3V logic against the received board before assigning a harness pinout.

Bring-up: initially MAVLink 2, 115200 baud, 8N1. ArduPilot uses SERIAL4; PX4 names this UART TELEM2. Keep GPS on UART3/GPS1 plus compass I2C. Request timestamped position, attitude, GPS quality and health at measured rates; reject stale/invalid navigation and test link loss while capturing images and writing SD.

## GPIO / I2C / SPI expansion - `schematics/GPIO.kicad_sch`

**Decided:** optional short-cable 3.3V expansion; share the SD SPI bus with separate chip selects. GPIO4/5 are available for I2C because the Mega camera does not use SCCB.

**Drawn:** empty placeholder; connector sizes, pin order and electrical ports remain to draw.

| Function | Planned connection | Expansion-sheet direction |
|---|---|---|
| Shared SPI clock | GPIO40 / existing SD_CLK signal | Input |
| Shared SPI MOSI | GPIO41 / existing SD_MOSI signal | Input |
| Shared SPI MISO | GPIO42 / existing SD_MISO signal | Output |
| External-device CS | GPIO48, independent of SD_CS GPIO47 | Input |
| I2C SDA / SCL | GPIO4 / GPIO5 | Bidirectional |
| Power / ground | Existing 3.3V rail / GND | Power connections |

- [ ] Choose/place headers or locking connectors and document numbered contacts, signal directions and 3.3V logic/power limits. Keep raw battery and motor power off this breakout.
- [ ] Add shared SCK/MOSI/MISO connections and separate EXT_CS control; preserve existing shared-bus net names rather than renaming SD nets.
- [ ] Add a 10k pull-up on the external CS to keep the peripheral deselected during startup; SD keeps its own independent CS pull-up.
- [ ] If fitting I2C, add/coordinate one effective pull-up per SDA/SCL line to 3.3V. Pick values for the actual devices, cable/bus capacitance and clock rate; 4.7k is a candidate, not an additional mandatory set if devices already provide suitable pull-ups.
- [ ] Add core/child/parent sheet ports and wires, and record the final pin allocation. Keep GPIO35/36/37 reserved for N16R8 memory and boot-strapping pins out of casual expansion use.
- [ ] Document available spares (GPIO7, 11-18 and 21) only after checking the complete allocation; GPIO8/9/10/6 are reserved for the planned camera.

Later layout/bring-up: aim for a short SPI cable (initial plan below 5cm), provide nearby ground returns, initialize SD into SPI mode before other shared devices, and verify unselected devices release MISO. Check the 3.3V load allocation before powering external modules.

## Optional UART debug - `schematics/uart_debug.kicad_sch`

**Decided:** optional 3.3V UART0 access for an external USB-UART adapter. Native USB remains the main programming/console/JTAG port.

**Drawn:** explanatory placeholder note only; no connector or ports yet.

| Header signal | Connection | Debug-sheet direction |
|---|---|---|
| TX from Flamingo | GPIO43 / UART0 TX | Input |
| RX into Flamingo | GPIO44 / UART0 RX | Output |
| GND | Common ground | Ground connection |

- [ ] Decide to fit or explicitly omit the optional header. If fitted, choose a simple 1x3 2.54mm THT header or a suitable locking connector and assign an unused reference.
- [ ] Define/label the numbered pin order, then wire GPIO43 TX -> adapter RX, adapter TX -> GPIO44 RX and GND -> GND.
- [ ] Label the header `3.3V TTL UART` and show TX/RX from Flamingo's perspective.
- [ ] Add core, debug-child and parent sheet ports/wires. This header does not add another native USB interface.
- [ ] Omit an adapter power contact for the basic TX/RX/GND connection; do not connect the adapter's 5V output to the ESP32 3.3V rail.

Bring-up: use an adapter with verified 3.3V logic; check firmware UART0 pin/console settings. Manual download recovery still depends on correct EN/BOOT support on the core sheet.

## Parent-sheet integration still to draw

- [ ] Connect USB data between the existing USB/core sheet pins; retain USB_D_P and USB_D_N names and finish their bidirectional port definitions.
- [x] Connect SD_CLK, SD_MOSI, SD_MISO and SD_CS between existing SD/core parent pins; verified by netlist after the grid correction. Review direction metadata in the final ERC pass.
- [ ] Add the planned camera, FC telemetry, expansion and optional debug ports to their child and core sheets, then add matching parent pins and wires.
- [ ] Check that each connector's TX/RX labels use the documented viewpoint; port direction is relative to its child sheet, not the external device.
- [ ] Reconcile obsolete architecture notes with the selected Mega camera and MicoAir743v2-AIO-45A as those pages are completed. Drawn arrows/notes alone do not connect electrical nets.

## Before PCB release

- [ ] Resolve remaining ERC findings; a clean export is not proof of an electrically complete schematic.
- [ ] Verify each MPN, value, footprint/pad mapping and assembly selection, especially inductors and connectors.
- [ ] Update PCB from schematic and review reference changes, then finish placement/routing and DRC.
- [ ] Confirm 50x80mm target / 50x100mm maximum, connector access, mounting and antenna clearance.
- [ ] Test rails, source selection, SD writes and timestamped camera/laser/FC operation on hardware.

References: [SD pull-ups](https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-reference/peripherals/sd_pullup_requirements.html), [SD SPI sharing](https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-reference/peripherals/sdspi_share.html), [TPS54302](https://www.ti.com/lit/ds/symlink/tps54302.pdf), [TPS2116](https://www.ti.com/lit/ds/symlink/tps2116.pdf), [TPS6216x](https://www.ti.com/lit/ds/symlink/tps62160.pdf), [C25905 package](https://jlcpcb.com/partdetail/C25905).

Assembly decision: only C8 (47uF) is hand-soldered among the capacitors. C11 is the selected 100uF non-polarized capacitor for factory assembly; remove its former hand-solder exclusion.

Top-level grid correction: all nine sheet boxes, sheet pins and electrical wire/junction coordinates are on the 50mil (1.27mm) grid. Four zero-length stubs created by snapping were removed. Net names were preserved. SD CLK/CS/MISO/MOSI connections to U1 were verified independently by netlist.
