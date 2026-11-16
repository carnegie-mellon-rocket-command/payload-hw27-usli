# Flamingo schematic build plan

Updated: 2026-11-15. Checked against the saved active KiCad hierarchy. Checked boxes mean drawn or named, not electrically validated. See [COMPONENTS.md](COMPONENTS.md) for component choices and the current connection record.

## Camera detachable interface

Selected: Arducam Mega 5MP autofocus, Amazon B0BW7MDVHK ($35 per user). Camera sheet now contains only J5 1x6 header, R20 CS pull-up. Core SPI allocation: GPIO7 CS,8 SCK,9 MISO,10 MOSI. Prior DVP labels and wire stubs removed. Camera signals and supply/ground now use hierarchical ports with parent wiring; extra host decoupling capacitors removed. See [Camera interface](COMPONENTS.md#camera-and-image-processing) for wiring, GPIO availability and validation. PCB and hardware testing pending.

## Current sheet inventory

| Page | Saved state | Remaining work |
|---|---|---|
| System overview | Eight functional sheet boxes; USB power and laser links drawn | Connect SD and USB data at the parent; camera, FC and expansion interfaces |
| Power distribution | Circuit and component verification complete per user | Final electrical check and layout |
| Battery input protection | Circuit verified per user; C8 existing 47uF part for hand soldering | Included in final power check and layout |
| 4S to 5 V buck | Circuit verified per user; C3 replacement resolved | Included in final power check and layout |
| ESP32-S3 core | U1 N16R8, power/ground and USB/SD/laser labels | EN/reset, BOOT, decoupling, camera/FC/expansion and remaining parent wiring |
| USB programming / JTAG | J3 DEALON USB-TYPE-C-017, R6/R7 CC pull-downs, joined D+/D- copies | Shell grounding, ESD, input protection and parent USB data wiring |
| Arducam Mega SPI camera | Six-pin interface drawn | Cable and hardware validation |
| microSD | J2 TF-115-BCP9, R1-R5 pull-ups, grounded shell, CD no-connect; layout cleaned | Local decoupling and parent SPI wiring |
| STA-M020X laser | J1 five-contact connector, supply/ground and UART labels | Resolve TX/RX pin assignment against module manual, verify harness and ENO |
| Flight-controller telemetry | Empty placeholder | Connector, GPIO1/2 UART and ground interfaces |
| GPIO / I2C / SPI expansion | Empty placeholder | Headers, I2C pull-ups as needed, SPI sharing and EXT_CS bias |

Inactive camera_tarpfinder, power_tarpfinder, usb_tarpfinder, GPS and usb_debug files are not in the active hierarchy; they have not been treated as implemented circuits or renamed.

## Naming completed

- [x] Give components unique R/C/L/D/F/J/U references; enter passive magnitudes in Value fields rather than reference names.
- [x] Preserve component UUIDs so schematic-to-PCB association can survive reference updates.
- [x] Preserve all original net names, hierarchy port names/directions and sheet names. Current CAD uses global `5V` and `3V3`, local `Buck_5V`, and the original battery/buck port names.
- [ ] Review existing battery/buck port directions separately; they were not changed in this component-naming pass.
- [ ] Change USB_D_P/N to bidirectional on both child labels and matching parent pins when finishing USB; original definitions retained for now.
- [ ] Core parent SD_MOSI still needs output direction to match its child label; original definition retained.
- [x] Top-level camera box and connections now match restored OV5640 DVP architecture.
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

Selected: Arducam Mega 5MP autofocus, Amazon B0BW7MDVHK ($35 per user). Camera sheet now contains only J5 1x6 header, R20 CS pull-up. Core SPI allocation: GPIO7 CS,8 SCK,9 MISO,10 MOSI. Prior DVP labels and wire stubs removed. Camera signals and supply/ground now use hierarchical ports with parent wiring; extra host decoupling capacitors removed. See [Camera interface](COMPONENTS.md#camera-and-image-processing) for wiring, GPIO availability and validation. PCB and hardware testing pending.

## microSD

- [x] J2 TF-115-BCP9 / C720505, with existing imported footprint.
- [x] R1 DAT2, R2 CS, R3 MOSI, R4 MISO, R5 DAT1: 10k pull-ups to global `3V3`; 0805 / C17414. No CLK pull-up.
- [x] Pin 4 global `3V3`; pin 6 and shell pins 10-13 GND; mechanical CD pin 9 no-connect.
- [x] Child ports: SD_CLK/MOSI/CS inputs; SD_MISO output. DAT1/DAT2 use local labels and have no MCU connection.
- [x] Separate pull-up bank and socket with nonoverlapping fields/labels and explanatory notes.
- [ ] Add local supply capacitors near the socket.
- [x] Connect SD parent pins to core parent pins. Top-level sheet boxes/pins/wires snapped to the 50mil (1.27mm) grid; exported netlist verifies all four SD signals connect separately to the intended core pads.


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

**Decided:** use the MicoAir743v2-AIO-45A UART4 connection; Flamingo has independent power from the shared battery. Four-contact connector desired, with TX/RX/GND used and FC 5V unused. The earlier three-contact Micro-Fit selection is superseded.

**Drawn:** placeholder/note only; no connector or electrical ports yet.

### Four-contact UART4 connector and cable selection

This supersedes the earlier three-contact Micro-Fit proposal. Use the confirmed four-contact JST-SH 1.0mm-pitch connection, with only TX, RX and GND electrically used. The 5V position is deliberately unconnected on Flamingo.

| Item | Selection |
|---|---|
| Flamingo PCB socket | JST **SM04B-SRSS-TB(LF)(SN)**, four contacts, 1.0mm pitch, right-angle SMT; [JLC C160404](https://jlcpcb.com/partdetail/JST-SM04B_SRSS_TB_LF_SN/C160404), Extended, Economic/Standard SMT assembly |
| KiCad symbol | `Connector_Generic:Conn_01x04`; assign a free reference |
| KiCad footprint | `Connector_JST:JST_SH_SM04B-SRSS-TB_1x04-1MP_P1.00mm_Horizontal` (available in the installed library) |
| Cable | Included **SH1.0-4P cable, 15cm**, identified in the user-supplied FC packing-list image. Reuse this cable; no separate cable purchase planned. Inspect whether its Flamingo end is already terminated or needs an SH four-contact housing/contacts |
| Plug housing if making a harness | JST SHR-04V-S family, with matching SH crimp contacts sized for the chosen wire; a finished cable avoids hand-crimping tiny contacts |

**Connector family confirmed:** the user-supplied packing-list image explicitly identifies the included lead as **SH1.0-4P Cable 15cm (For FC) x1**. This confirms the SH 1.0mm / four-contact family for the included cable and supports the selected JST SM04B-SRSS-TB socket. Use the supplied lead. Its end-to-end contact numbering and termination at the Flamingo end still need inspection; the packing-list text alone does not prove both ends are preterminated or give a pin map.

| FC UART4 signal | Flamingo connection |
|---|---|
| RX4 | GPIO1 TX / FC_UART_TX |
| TX4 | GPIO2 RX / FC_UART_RX |
| 5V | Corresponding Flamingo pad no-connect; never tie to Flamingo's power rails |
| GND | GND |

Do not assign numbered Flamingo pads from the screenshot's vertical order alone. Use a continuity test on the actual cable to map the FC contacts to the selected PCB connector's pad numbers. Preserve TX-to-RX crossing electrically. Qwiic/STEMMA QT is the cable's usual application, not the UART wiring standard: do not use its usual power/I2C color convention as the FC pinout. With this socket/cable used for UART, clearly label it UART so it is not mistaken for an I2C expansion port.

JST-SH uses friction retention rather than the positive latch of Micro-Fit. Use suitable cable restraint during layout/mechanical work. The SH board socket is 1mm SMT and is best factory-assembled; it is not the earlier easy-through-hole-solder option. JLC assembly stock was not exposed by the readable listing; the cable stock observation is not JLC inventory confirmation. A separate Adafruit cable is no longer required; use the included 150mm lead.

Sources: [JST SH family](https://www.jst-mfg.com/product/index.php?lang=en&series=231), [FC manual](https://micoair.com/en/docs/flight-controller/micoair743-aio-series/micoair743v2-aio-45a-manual), [JLC socket](https://jlcpcb.com/partdetail/JST-SM04B_SRSS_TB_LF_SN/C160404), [finished cable](https://www.adafruit.com/product/5384).

- [x] Confirm included cable family from the packing-list image: SH1.0-4P, 15cm, for FC.
- [ ] Inspect its Flamingo-end termination and verify contact continuity before assigning numbered PCB pads.
- [ ] Place the four-contact socket and record the pad-number map from cable continuity. Keep FC 5V's corresponding pad no-connect.
- [ ] Add FC_UART_TX (input on telemetry sheet), FC_UART_RX (output on telemetry sheet), and GND; connect GPIO1 TX -> FC RX4 and FC TX4 -> GPIO2 RX. Core directions are opposite.
- [ ] Add matching core/child/parent ports and wires, preserving existing net names.
- [ ] Correct the outdated MicoAir405v2 placeholder note to the selected MicoAir743v2-AIO-45A.

Bring-up: MAVLink 2, initially 115200 baud / 8N1, non-inverted 3.3V logic. ArduPilot uses SERIAL4; PX4 uses TELEM2. Keep GPS on FC UART3/GPS1 and compass I2C. Request timestamped position/attitude/health and test stale-data/link-loss behavior while capturing images and writing SD.

## GPIO / I2C / SPI expansion - `schematics/GPIO.kicad_sch`

**Decided:** optional short-cable 3.3V expansion; share the SD SPI bus with separate chip selects. GPIO4/5 are available following the SPI camera change. Any shared expansion requires a voltage-compatible bus and coordinated pull-ups.

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
- [ ] Use the SPI-camera allocation: GPIO7-10 occupied; GPIO4/5/6,11-18,21,43/44/48 available before diagnostics allocation.

Later layout/bring-up: aim for a short SPI cable (initial plan below 5cm), provide nearby ground returns, initialize SD into SPI mode before other shared devices, and verify unselected devices release MISO. Check the 3.3V load allocation before powering external modules.


## Parent-sheet integration still to draw

- [ ] Connect USB data between the existing USB/core sheet pins; retain USB_D_P and USB_D_N names and finish their bidirectional port definitions.
- [x] Connect SD_CLK, SD_MOSI, SD_MISO and SD_CS between existing SD/core parent pins; verified by netlist after the grid correction. Review direction metadata in the final ERC pass.
- [ ] Add the planned camera, FC telemetry, expansion ports to their child and core sheets, then add matching parent pins and wires.
- [ ] Check that each connector's TX/RX labels use the documented viewpoint; port direction is relative to its child sheet, not the external device.
- [ ] Reconcile obsolete architecture notes with the restored DVP camera and MicoAir743v2-AIO-45A as those pages are completed. Drawn arrows/notes alone do not connect electrical nets.

## Before PCB release

- [ ] Resolve remaining ERC findings; a clean export is not proof of an electrically complete schematic.
- [ ] Verify each MPN, value, footprint/pad mapping and assembly selection, especially inductors and connectors.
- [ ] Update PCB from schematic and review reference changes, then finish placement/routing and DRC.
- [ ] Confirm 50x80mm target / 50x100mm maximum, connector access, mounting and antenna clearance.
- [ ] Test rails, source selection, SD writes and timestamped camera/laser/FC operation on hardware.

References: [SD pull-ups](https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-reference/peripherals/sd_pullup_requirements.html), [SD SPI sharing](https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-reference/peripherals/sdspi_share.html), [TPS54302](https://www.ti.com/lit/ds/symlink/tps54302.pdf), [TPS2116](https://www.ti.com/lit/ds/symlink/tps2116.pdf), [TPS6216x](https://www.ti.com/lit/ds/symlink/tps62160.pdf), [C25905 package](https://jlcpcb.com/partdetail/C25905).

Assembly decision: only C8 (47uF) is hand-soldered among the capacitors. C11 is the selected 100uF non-polarized capacitor for factory assembly; remove its former hand-solder exclusion.

Top-level grid correction: all nine sheet boxes, sheet pins and electrical wire/junction coordinates are on the 50mil (1.27mm) grid. Four zero-length stubs created by snapping were removed. Net names were preserved. SD CLK/CS/MISO/MOSI connections to U1 were verified independently by netlist.

## Native USB programming and debugging

One USB-C port provides board power, flashing, serial console and built-in USB JTAG. The optional UART debug sheet/header has been removed; GPIO43/44 remain free.

Saved netlist review: J3 A6/B6 join USB_D_P and reach U1 pad14 (GPIO20); A7/B7 join USB_D_N and reach U1 pad13 (GPIO19). R7 is CC1-to-GND and R6 is CC2-to-GND, each5.1k. USB VBUS reaches the power selector. No additional USB/UART bridge or external JTAG connector is required.

Remaining manual work:
- Connect J3 shell pads1-4 to the chosen shield/ground network (currently unconnected); for this board, use short GND connections unless a deliberate chassis scheme is designed.
- Add low-capacitance USB data ESD protection next to J3; finish VBUS protection/current budget review.
- Reserve22/33-ohm series resistor footprints on D+/D- near the ESP32 per Espressif guidance; tune/populate based on the reference design and signal validation.
- Preserve GPIO19/20 for USB and ensure BOOT(GPIO0)/EN reset access for recovery.
- Route D+/D- as a short90-ohm differential pair over continuous ground.
- In firmware, use the USB Serial/JTAG console; use Espressif OpenOCD for breakpoint debugging. Avoid reassigning USB pins or disabling USB JTAG through eFuses. Install the Espressif USB JTAG driver on Windows.

References: [USB JTAG setup](https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-guides/jtag-debugging/configure-builtin-jtag.html), [hardware checklist](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32s3/schematic-checklist.html).

## Planned diagnostics / recovery sheet

Requested 2026-11-16. This replaces the former UART-only debug-sheet concept. Native USB remains the single programming/console/JTAG port. The following is a design plan, not drawn or verified hardware; choose exact parts and references during implementation.

| Function | Proposed circuit | Meaning / constraint |
|---|---|---|
| Gated 3.3V power LED | 3V3 -> resistor -> LED -> shared LED_RETURN | Indicates rail presence only while diagnostics are enabled; not proof of valid regulation or firmware health. Calculate resistance for about1mA with the selected LED. |
| Core heartbeat LED | GPIO21 -> resistor -> LED -> shared LED_RETURN | Reserve GPIO21; flash from the main application health loop. A stuck task must stop the heartbeat; an independent timer alone does not prove application health. |
| Optional fault LED | GPIO18 -> resistor -> LED -> shared LED_RETURN, DNP initially | Reserve18 only if fitted; use fault codes for camera/SD/link errors. |
| RESET button | Normally-open switch EN to GND | Reuse the existing EN pull-up/RC; do not duplicate its timing network on this sheet. |
| BOOT button | Normally-open switch GPIO0 to GND | Boot strap/recovery control; review strap pull-up and GPIO46 state against Espressif guidance. Hold BOOT, pulse RESET, then release BOOT for download recovery. |
| Recovery header | 1x6:1 GND,2 3V3 reference,3 UART0 TX(GPIO43),4 UART0 RX(GPIO44),5 EN,6 GPIO0 | 3.3V logic only. Adapter RX connects to TX and adapter TX to RX. Pin2 is voltage reference, not an authorized power input. No adapter5V connection. Firmware download uses UART0 plus BOOT/RESET control. |

- [ ] Create diagnostics child sheet and connect matching hierarchical core/parent ports for HEARTBEAT, optional FAULT, EN, BOOT, UART0_TX/RX and power/ground.
- [ ] Keep EN and boot traces short; avoid long button leads and unintended startup loads. No external pin-JTAG header planned: GPIO39-42 are already assigned to laser/SD; use USB JTAG.
- [ ] Select LED colors/brightness and resistor values; account for continuous power-LED load and GPIO drive limits.
- [ ] Add power and signal test pads if space permits. Keep recovery connector accessible without removing the camera or battery.
- [ ] Verify LED meaning in firmware, manual USB/UART recovery and boot-strapping on hardware.

GPIO21 is proposed for heartbeat; GPIO18 is optional fault. GPIO43/44 become reserved for recovery access. GPIO17 is reserved for DIAG_LED_EN. These are reservations in the plan, not changes to the core schematic.

## Proposed south-edge expansion connectors

South refers to a proposed physical PCB edge; placement, antenna keepout and final connector orientation remain to be checked. Prefer keyed connectors for field wiring. Define mating-side orientation and printed pin1 before release.

| Connector | Proposed contact order | Use |
|---|---|---|
| I2C,1x4 | GND,3V3,SDA(GPIO4),SCL(GPIO5) | Low-speed sensor expansion; coordinate one effective set of bus pull-ups. This is a custom pinout, not a claim of Qwiic compatibility. |
| SPI,1x6 | GND,3V3,SCK(GPIO40),MOSI(GPIO41),MISO(GPIO42),CS(GPIO48) | Shared with SD; independent CS and device-specific SPI settings. Not the camera bus. |
| General GPIO,2x5 | Row pairs:1 GND/2 3V3;3 IO6/4 IO11;5 IO12/6 IO13;7 IO14/8 IO15;9 IO16/10 GND | Seven flexible3.3V GPIOs; firmware can assign PWM, interrupts, UART or other routed peripheral functions. Analog capability/noise must be checked for the selected pin and use. |

GPIO18 can remain spare if the fault LED is omitted. GPIO21 is reserved for heartbeat. GPIO43/44 stay on the recovery header. Exclude strapping GPIO0/3/45/46 and PSRAM GPIO35-37 from casual expansion. Do not expose raw battery or5V on these3.3V headers. Check available3.3V current before supplying accessories; these are short internal-cable interfaces, not external long-wire buses. Shared SPI devices must release MISO when deselected; initialize SD appropriately and serialize bus access.

### Firmware-controlled diagnostic LED enable

All diagnostic LEDs must remain off during normal operation when firmware disables them, including the power indicator. Reserve GPIO17 as DIAG_LED_EN. Use one logic-level N-channel MOSFET as a shared low-side switch: drain to LED_RETURN, source to GND, gate driven from GPIO17 with an approximately100k gate-to-source pull-down. Select a MOSFET specified at2.5/3.3V gate drive. A series gate resistor may be added if needed; exact device and footprints remain to select.

All three LED cathodes return to LED_RETURN rather than directly to GND. Each LED retains its own current-limiting resistor. Power-LED anode is fed from3.3V; heartbeat/fault anodes are driven by GPIO21/GPIO18 through their resistors. GPIO17 LOW disables every LED; HIGH enables the power indicator and permits firmware to control heartbeat/fault independently. The gate pull-down defaults the switch off during reset/unprogrammed boot; avoid bootloader/peripheral use of GPIO17 that could defeat this policy.

Firmware defaults DIAG_LED_EN LOW, initializes status outputs LOW, and enables diagnostics only when explicitly requested. On disable, drive status outputs LOW and then deassert DIAG_LED_EN. Do not implement an always-on rail indicator elsewhere. With diagnostics disabled there is intentionally no visible power indication; use test pads/meter during bring-up. Verify off-state leakage/ghosting and LED behavior through reset, boot and firmware update. This gate controls only LEDs, not ESP32 reset, camera power or programmer signals.

GPIO17 is removed from general expansion: the proposed2x5 GPIO header now exposes6,11-16 (seven GPIOs), with pin10 reassigned to GND. Diagnostics reservations:17 enable,21 heartbeat, optional18 fault,43/44 recovery UART. Planned only; schematic implementation pending.
