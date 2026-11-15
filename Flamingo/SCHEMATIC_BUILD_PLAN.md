# Flamingo schematic build plan

Updated: 2026-11-15. This is the work list for drawing the schematic. Detailed electrical checks come afterward.

Use [COMPONENTS.md](COMPONENTS.md) for architecture, proposed pin assignments and external modules; use [POWER_PARTS.md](POWER_PARTS.md) for the power parts. Tick items as they are drawn, not just because a library exists.

## What we are building

- ESP32-S3-WROOM-1-N16R8: 8 MB PSRAM, 16 MB flash.
- Arducam Mega 5 MP AF SPI camera, microSD logging and STA-M020X UART laser.
- MicoAir743v2-AIO-45A flight controller with four ESCs; external M10G-5883 GPS/compass connects to the flight controller.
- One 4S battery, split externally with an XT30 parallel Y harness. One branch feeds the AIO/motors; the other feeds Flamingo.
- Flamingo converts 4S to 5 V onboard. USB takes priority when connected and powers all Flamingo loads through SYS_5V. No onboard charging or physical camera/laser power switch.
- Maximum PCB outline: 50 x 100 mm; aim around 50 x 80 mm. PCB work starts after the schematic.

```text
4S battery -> XT30 Y harness -> AIO -> motors and GPS
                           -> Flamingo protection -> 5 V buck --+
USB-C -> USB input protection --------------------------------+-> selector -> SYS_5V
                                                                         |-> laser
                                                                         |-> 3.3 V -> ESP32 + microSD + camera
AIO UART + GND <---------------------------------------------------------> ESP32
```

## Current saved state

| Sheet | Already present | Work remaining |
|---|---|---|
| Power | XT30/input protection, TPS54302 support circuit, TPS2116 priority network, TPS62162 support circuit | Validate passive values/ratings, add mux decoupling and USB protection |
| USB programming / JTAG | DEALON USB-TYPE-C-017, paired D+/D- contacts, CC pull-downs | Shell grounding, ESD/input protection, package/value checks and top-level data wiring |
| ESP32-S3 core | Module and preliminary camera/laser wiring | Power, reset, boot and remaining interfaces |
| Arducam Mega camera | Empty placeholder; top-level title still OV5640 | Entire SPI interface; camera header reference to assign (J2 is microSD) |
| microSD | J2 TF-115-BCP9, five 10k pull-ups R1-R5, grounded shell, unused CD marked | Local decoupling and top-level SPI connections |
| STA-M020X laser | Five-pin connector and preliminary wiring | Final cable/connector choice and supply naming |
| Flight-controller telemetry | Sheet placeholder | Connector and UART wiring |
| GPIO / I2C / SPI | Sheet placeholder | Headers and wiring |
| Optional UART debug | Sheet placeholder | Header and wiring |
| Top level | All nine sheet boxes and laser/USB-power wiring | Add SD and USB-data parent interfaces/wires; camera and remaining interfaces |

XT30 CAD is placed on the Power sheet as `EasyEDA:XT30PW-M`. Existing wires and assigned footprints are starting points, not completed validation.

## Build order

1. Power main path and USB input.
2. Core power/reset/boot and USB data.
3. Camera SPI interface, connector and decoupling.
4. microSD, laser and flight-controller telemetry.
5. Expansion and optional debug headers.
6. Finish top-level connections, then review the complete schematic.

## 1. Power — `schematics/power.kicad_sch`

### Battery input and 5 V conversion

- [x] Place `EasyEDA:XT30PW-M`, value `XT30PW-M30.G.Y`, LCSC `C431092`. This is the original through-hole, right-angle PCB connector.
- [ ] Label the input `VBAT_4S` and `GND`; map the contacts to the actual harness polarity.
- [ ] Add Flamingo branch protection and reverse-polarity protection; call the protected battery net `VBAT_PROT`. Exact protection parts remain to select.
- [ ] Keep the already placed TPS54302DDCR / C311983. Give it a normal `U` reference during annotation.
- [ ] Add its inductor, input/output capacitors, bootstrap capacitor, feedback network and EN network. Output net: `BUCK_5V`.
- [ ] Use the [TI 5 V reference circuit](https://www.ti.com/lit/ds/symlink/tps54302.pdf), Figure 7-1, as the starting circuit. Its example uses 10 uH, 10 uF input, two 22 uF outputs, 100 nF bootstrap, and a feedback/filter network. Final passive parts and battery cutoff settings remain to select; the example's EN thresholds are not a 4S battery cutoff design.

### USB/battery source selection

- [x] Place TPS2116DRLR / C3235557 using `Power_Management:TPS2116DRL`, or the existing imported TPS2116 symbol. Use one version.
- [ ] Connect protected `USB_5V` to VIN1 and `BUCK_5V` to VIN2. Tie both VOUT pins to `SYS_5V`.
- [ ] Configure USB priority: MODE to VIN1, PR1 to a divider sensing VIN1, plus the input/output capacitors. ST can stay unused.
- [ ] Feed the laser, main 3.3 V regulator and camera load through the main 3.3 V regulator from `SYS_5V`.
- [ ] Use the [TPS2116 datasheet](https://www.ti.com/lit/ds/symlink/tps2116.pdf) for the divider and capacitor circuit. USB current/inrush protection belongs ahead of VIN1; the mux does not provide a USB current budget.

### Low-voltage supplies

- [ ] Add the main `+3V3` supply. Current candidate: TPS62162DSGR / C40256, subject to the combined load budget.
- [ ] Add its inductor and capacitors following the fixed-3.3 V circuit in the [TPS6216x datasheet](https://www.ti.com/lit/ds/symlink/tps62160.pdf).
- [ ] Include the complete Mega camera module in the +3V3 current budget; no separate sensor supplies are required.
- [ ] Add convenient test points for GND, protected battery, BUCK_5V, SYS_5V and +3V3.

Do not copy Pelican's charger, single-cell battery gating or laser boost into this design. Motor current stays off Flamingo.

## 2. USB programming / JTAG — `schematics/usb_power_program.kicad_sch`

- [x] Place DEALON USB-TYPE-C-017 / C2927037, right-angle SMT. Verify imported footprint against the exact connector drawing.
- [x] Join the connector's duplicated USB 2.0 D+ contacts and duplicated D- contacts into one D+/D- pair.
- [x] Draw separate CC pull-downs to GND. Before release, enter 5.1k in Value fields and check C25905 against the assigned 01005 footprint.
- [ ] Add USB ESD protection; current candidate USBLC6-2SC6 / C7519. Follow its actual pinout.
- [ ] Add the selected USB current/inrush protection between VBUS and the `USB_5V` output to Power. This part remains to select.
- [ ] Expose `USB_D_P`, `USB_D_N` and `USB_5V` as sheet interfaces. Connect D+ to core GPIO20 and D- to GPIO19 at the top level.
- [ ] Ground connector shell pads 1-4; USB ground contacts are already grounded. Handle unused contacts deliberately. No separate USB-to-UART chip is needed for native USB Serial/JTAG.

Reference: [Espressif USB Serial/JTAG](https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-guides/usb-serial-jtag-console.html).

## 3. ESP32-S3 core — `schematics/core.kicad_sch`

- [ ] Keep U1 as `ESP32-S3-WROOM-1-N16R8`. Its flash, PSRAM, crystal and antenna are inside the module; do not add bare-chip memory circuitry.
- [ ] Connect its 3.3 V supply and all ground pads; add local supply capacitors.
- [ ] Add EN pull-up/reset timing and a RESET button. Add GPIO0 pull-up and BOOT button for manual download recovery. Use the module reference circuit for values.
- [ ] Finish the interfaces using the GPIO plan below. GPIO numbers are not module pad numbers—wire by pin name.
- [ ] Correct any preliminary camera/laser wires that disagree with the plan.
- [ ] Keep GPIO35/36/37 unavailable for N16R8 PSRAM. Avoid casually using strapping pins GPIO0/3/45/46 for peripherals.
- [ ] Add sheet interfaces for USB, telemetry, SD, expansion and optional debug. Record unused/control pins explicitly.

| Function | Proposed ESP32 GPIOs |
|---|---|
| Camera SPI | 8 SCK, 9 MOSI, 10 MISO, 6 CS |
| Available I2C | 4 SDA, 5 SCL |
| Native USB | 19 D-, 20 D+ |
| FC telemetry | 1 TX, 2 RX |
| Laser | 38 TX, 39 RX |
| Shared SPI | 40 SCLK, 41 MOSI, 42 MISO |
| SD / expansion chip select | 47 SD_CS, 48 EXT_CS |
| Optional UART0 debug | 43 TX, 44 RX |
| Available | 7, 11-18, 21; review before assigning |

Reference: [S3 module datasheet](https://documentation.espressif.com/esp32-s3-wroom-1_wroom-1u_datasheet_en.pdf) and [hardware guidelines](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32s3/index.html).

## 4. Arducam Mega SPI camera - `schematics/camera.kicad_sch`

Current saved sheet is empty. The top-level box still says OV5640; rename when drawing the selected Mega interface.

- [ ] Draw a six-wire SPI connector for the Mega; assign an unused reference (J2 is the SD socket).
- [ ] Use the proposed connector/pin plan in COMPONENTS.md after verifying the harness. A Micro-Fit locking alternative has been discussed but is not implemented.
- [ ] Draw core SPI: GPIO8 SCK, GPIO9 MOSI, GPIO10 MISO, GPIO6 CS, and parent connections.
- [ ] Add 10k CS pull-up and local 100 nF + 10 uF; review the 3V3 load budget.
- [ ] Validate JPEG capture/readout and harness retention on hardware.

## 5. microSD - `schematics/SD_card.kicad_sch`

- [x] Place J2 TF-115-BCP9 / C720505 with `EasyEDA:TF-SMD_TF-115-BCP9`.
- [x] Connect VDD to global `3V3`, VSS and shell pins 10-13 to GND.
- [x] Draw `SD_CLK`, `SD_MOSI`, `SD_CS` inputs and `SD_MISO` output.
- [x] Add five 10k pull-ups: R1 DAT2, R2 CS, R3 MOSI, R4 MISO, R5 DAT1; existing 0805 / C17414 selection retained. CLK has no pull-up.
- [x] Mark mechanical CD pin 9 intentionally unconnected. DAT1/DAT2 are biased high without core GPIOs.
- [x] Separate pull-up bank, socket, labels and notes; enter 10k Value fields and unique references.
- [ ] Add local supply decoupling close to the socket in the eventual PCB layout.
- [ ] Add parent sheet pins and wire core to SD: CLK GPIO40, MOSI GPIO41, MISO GPIO42, CS GPIO47. These core labels exist but do not yet connect to the SD sheet through the parent.
- [ ] Draw expansion SPI sharing only with independent CS; initialize SD into SPI mode before other devices use the bus.

References: [SD pull-ups](https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-reference/peripherals/sd_pullup_requirements.html), [sharing SD SPI](https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-reference/peripherals/sdspi_share.html).

## 6. STA-M020X laser — `schematics/laser.kicad_sch`

- [ ] Keep the existing five-contact module mapping: 1 GND, 2 Vin, 3 laser TXD, 4 laser RXD, 5 ENO.
- [ ] Connect Vin to `SYS_5V` through the sheet interface; replace the ambiguous existing `5V` interface name consistently at both levels.
- [ ] Connect laser TXD -> ESP32 GPIO39 RX; laser RXD <- ESP32 GPIO38 TX. Define `LASER_TX` as ESP32 output and `LASER_RX` as ESP32 input consistently.
- [ ] Keep ENO unconnected pending clarification; do not infer its function from the name.
- [ ] Confirm the laser's physical connector and choose the carrier connector/cable. The existing five-pin JST GH footprint is a candidate, not a confirmed laser mating connector.
- [ ] Decide whether to retain a five-pin carrier connector or use the originally requested six-way carrier with one spare contact. Record the harness mapping either way.
- [ ] Add local supply decoupling and a note that UART logic must be the confirmed 3.3 V setting.

Source: supplied SAT-M020X manual, which calls the module STA-M020X; summary and protocol notes are in [COMPONENTS.md](COMPONENTS.md#laser-interface).

## 7. Flight-controller telemetry — `schematics/fc_telemetry.kicad_sch`

- [ ] Select and place a locking connector for TX, RX and GND. Do not carry an FC 5 V supply on this link; Flamingo has its own power branch.
- [ ] Wire ESP32 GPIO1 TX -> AIO UART4 RX, and AIO UART4 TX -> ESP32 GPIO2 RX, plus common GND.
- [ ] Label signal direction from Flamingo's perspective: `FC_UART_TX` and `FC_UART_RX`.
- [ ] Add a connector pinout note and sheet interfaces matching the core.
- [ ] Note the firmware starting configuration: MAVLink 2, 115200 baud; AIO UART4 is ArduPilot SERIAL4 / PX4 TELEM2.

GPS stays on the AIO's UART3/GPS1 plus I2C for its compass. Do not add a GPS module or GPS regulator to Flamingo.

## 8. GPIO / I2C / SPI — `schematics/GPIO.kicad_sch`

- [ ] Choose connector sizes and physical orientation for the GPIO/I2C breakout and short SPI cable, planned below 5 cm.
- [ ] Break out +3V3, GND and available GPIO. Add a voltage/current label so this header is not mistaken for a motor-power output.
- [ ] Expose shared SPI SCLK/MOSI/MISO and separate GPIO48 `EXT_CS`.
- [ ] Add a default-high pull-up on EXT_CS so an external device stays deselected during startup.
- [ ] If exposing I2C on GPIO4/5, share only the correct ESP32-side voltage domain. Use 3.3 V pull-ups; the Mega camera has no external SCCB connection.
- [ ] GPIO7 is available after removing the parallel camera interface. Keep boot straps and PSRAM pins off general expansion.
- [ ] Put ground contacts beside the cable's signals where practical and document the final contact order.

## 9. Optional UART debug — `schematics/uart_debug.kicad_sch`

- [ ] Place a simple header with GND, ESP32 GPIO43 TX and GPIO44 RX.
- [ ] Label it `3.3 V TTL UART` and show TX/RX direction from Flamingo.
- [ ] Do not connect a USB-UART adapter's 5 V supply to the ESP32 rail. A power contact is unnecessary for the basic debug link.
- [ ] Expose the matching core interfaces. Native USB remains the main programming/JTAG connection.

## 10. Top level — `flamingo.kicad_sch`

- [ ] Synchronize each sheet's hierarchical labels and parent sheet pins after finishing that sheet.
- [ ] Connect Power to USB, core, SD, camera and laser. Use unambiguous rail names: VBAT_4S, VBAT_PROT, BUCK_5V, USB_5V, SYS_5V and +3V3.
- [ ] Connect core to USB data, SD SPI, camera, laser, FC UART, expansion and optional UART debug.
- [ ] Use hierarchical labels for module interfaces and local labels inside a sheet. GND and deliberately shared power symbols can be global; avoid also creating disconnected hierarchical nets with slightly different names.
- [ ] Use only CAM_SCK, CAM_MOSI, CAM_MISO and CAM_CS for the camera signal interfaces; power is +3V3/GND.
- [ ] Keep the architecture drawing readable and add short connector/voltage notes. Remove obsolete copied notes and annotate references normally.
- [ ] Update COMPONENTS.md with final connectors, camera revision and regulator/support parts as choices are settled.

## Libraries and parts workflow

See [libraries/EasyEDA/README.md](libraries/EasyEDA/README.md) for importing C-numbers into the relocated library. Prefer KiCad's stock symbols for generic resistors/capacitors and supported ICs; import exact parts when their CAD is missing.

Every fitted part eventually needs a value, correct footprint and purchase reference. Recheck JLCPCB stock/assembly eligibility when selecting new parts and before ordering; earlier stock checks are not reservations. The camera, laser, flight controller, GPS, motors and cable harness are external purchased items.

## After the drawing is complete

- [ ] Review power budgets and USB behavior, camera voltage/pin mapping, GPIO conflicts and connector polarity.
- [ ] Check symbols against package pads, run ERC and resolve findings.
- [ ] Complete the BOM, then start PCB outline, mounting and connector placement.

Open decisions carried forward: camera harness verification/retention and SPI support parts; 4S protection/cutoff; complete regulator support BOM and current budget; USB input protection/current capability; laser harness; FC/expansion/debug connectors; battery capacity, propellers and mechanical layout.

## Saved-diagram reconciliation - 2026-11-15

Use the implementation snapshot in COMPONENTS.md for the current saved state. Existing unchecked build items can include review/verification of preliminary drawing, not necessarily absent symbols. Current CAD rail names are `5V`, `3V3` and local `Buck_5V`; the planned SYS_5V/+3V3 names must be reconciled consistently across sheets. The current USB sheet data ports and corresponding core ports are incorrectly one-directional for USB: change both D+ and D- to bidirectional when finishing those interfaces. Parent wiring remains incomplete. Passives outside the SD sheet often contain values in their reference names while Value remains R/C/L; normalize them before BOM generation. This update does not certify the power circuitry or full-board ERC.
