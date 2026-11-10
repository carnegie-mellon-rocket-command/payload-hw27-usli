# Flamingo component tracker

Updated: 2026-11-03.

Flamingo is a new design. Pelican is a source of reusable components and circuits; the Pelican rework is canceled. This is a selection tracker, not a verified or fabrication-ready BOM. A copied library does not establish that its circuit is placed, validated, or suitable for Flamingo.

## Current system architecture - 2026-11-03

**Decision:** use a low-cost flight controller for flight sensing/control and an ESP32-S3 Flamingo board for camera processing and the six-pin TTL laser. Flamingo receives position, attitude and altitude over a wired MAVLink UART; it does not need its own GNSS receiver, compass, IMU or barometer under this architecture. The ESP32 selection and camera interface below are retained.

**Cheapest verified sourcing baseline:** MicoAir405v2 **Only FC / ArduPilot**, plus **MicoAir M10G-5883** external GPS/compass: **$31.99 + $13.99 = $45.98 USD** before shipping, taxes, cables, power hardware, camera, laser and Flamingo fabrication. This is a documented recommendation, not a purchase or a completed hardware test. The user's preference for GPS physically on the flight-controller PCB remains open; the baseline GPS is a separate module connected to the FC, not installed on Flamingo.

| Assembly | Responsibility | What still needs work |
|---|---|---|
| MicoAir405v2 flight controller | Existing ArduPilot flight firmware; BMI088 acceleration/rotation sensing; SPL06 barometric altitude; motor/servo outputs where required | Select the vehicle firmware/frame, configure/calibrate sensors, receiver, outputs and failsafes for the actual vehicle. Stock board support does not validate rocket ascent or deployment behavior. |
| External M10G-5883 GPS/compass | u-blox M10050 GNSS and QMC5883L compass; connects to FC UART3 and I2C; manufacturer specifies a 20 x 20 x 8 mm module and 5 Hz navigation rate | Confirm cable/contact order, detection and compass orientation; mount for sky view and away from interference. |
| Flamingo ESP32-S3 | OV5640 JPEG capture, tarp-color detection, six-pin laser communication and local image/detection logging | Write/test capture, decoding, detection, laser protocol and MAVLink parsing; no image-processing performance has been measured. |
| FC-to-Flamingo cable | Position, attitude, altitude, fix/health and timestamps; optional detection results back to FC | Add the telemetry connector to the eventual schematic, then validate voltage, timing and link-loss behavior. |

The FC handles the flight loop independently of camera processing. Flamingo's microSD remains for images/payload logs; the FC's microSD is a separate flight-log store. GPS position alone does not locate the tarp: camera calibration, camera-to-body alignment, attitude, range/terrain geometry and measurement timing are still needed.

### External controller/GPS shopping comparison

Checked 2026-11-03. These are complete-board purchases, not JLCPCB components to place on Flamingo. No universal cheapest-price claim is made: this is the lowest-cost documented combination verified among the listings checked.

| Combination | Listed hardware subtotal, USD | GPS physically on FC PCB? | Availability and tradeoff |
|---|---:|---|---|
| [MicoAir405v2 Only FC / ArduPilot](https://store.micoair.com/product/micoair405v2/) + [M10G-5883](https://store.micoair.com/product/m9-m10-gps-module/) | **45.98** | No; external GPS/compass | Cheapest baseline. Both exact variants reported in stock in the store's public variant data. FC: 36 x 36 x 8 mm, barometer, UART telemetry, official ArduPilot target `MicoAir405v2`. No ESC included. |
| Same FC + [MG-A01](https://store.micoair.com/product/m9-m10-gps-module/) | **46.98** | No; external GPS/compass | $14.99 GPS option with manufacturer-listed 10 Hz navigation, QMC5883L compass and 25 x 25 x 8 mm body. Both variants reported in stock. An extra $1 buys the specified higher GPS update rate, not RTK accuracy. |
| [MicoAir743-Lite Only FC](https://store.micoair.com/product/micoair743-lite/) + M10G-5883 | **60.98** | No; external GPS/compass | H743 at 480 MHz, 2 MB program flash, barometer and ArduPilot/PX4 support. **Only-FC variants reported out of stock.** It does not replace Flamingo's image memory or camera interface. |
| MicoAir743-Lite **50A Bluejay Stack** + M10G-5883 | **88.98** | No; external GPS/compass | FC+ESC variant reported in stock at $74.99; useful only if that ESC matches the actual motors/power system. Do not buy an unnecessary ESC simply to obtain the FC. |
| [Holybro Pix32 v6 Mini Set](https://holybro.com/products/pix32-v6) + M10G-5883 | **257.56** | No; external GPS/compass | Mini Set listed at $243.57 and available; includes FC, mini carrier and PM02 power module, **not GPS**. GPS adds $13.99; suitable cable/mating still needs review. More expensive but provides a Pixhawk-style modular arrangement, redundant IMUs and barometer. Do not buy the $189 FC-only module without a compatible carrier. |
| Emlid Navio2 + compatible Raspberry Pi + antenna | Not quoted: current supply/total unverified | **Receiver yes; antenna external** | True onboard NEO-M8N receiver and MS5611 barometer, but Navio2 is a Raspberry Pi HAT, not a standalone FC. Emlid's old purchase link redirects to its general store. Not selected; no current shippable combo under $300 was verified. |

Price evidence: direct public variant data for MicoAir405v2 (FC variant 3170), GPS (M10G-5883 3226; MG-A01 3225), and 743-Lite (Only FC 4390/4391; 50A stack 4408/4409); Holybro's published Mini Set variant 42471638859965. The GPS page's rendered price range differed from the direct variant prices, so confirm the exact checkout total, destination and stock before purchasing. Nothing has been ordered.

Sources: [405v2 manufacturer manual](https://micoair.com/en/docs/flight-controller/micoair405v2/micoair405v2-flight-controller-manual), [official ArduPilot hardware guide](https://ardupilot.org/copter/docs/common-MicoAir405v2.html), [GPS manufacturer manual](https://micoair.com/en/docs/gps-rtk/gps), [743-Lite manufacturer manual](https://micoair.com/en/docs/flight-controller/micoair743/micoair743-lite-flight-controller-manual), [Navio2 GPS documentation](https://docs.emlid.com/navio2/dev/gps-ublox/), [Navio2 hardware setup](https://docs.emlid.com/navio2/hardware-setup/).

### Why keep the camera on Flamingo?

More MCU speed or program flash does not establish image-processing capability. A 2592 x 1944 image uses 10,077,696 bytes in RGB565 or 15,116,544 bytes in RGB888. Pixhawk 4's 512 KB RAM and Pixhawk 6X-RT's 2 MB RAM cannot hold that full color frame. The 6X-RT's advertised 64 MB is flash, not working RAM. Buffered SPI cameras and processing in chunks can reduce RAM demand, but would require custom integration on the flight controller.

The selected S3 has 8 MB PSRAM and 16 MB flash. Keep the camera-compressed JPEG path described below; full 5 MP RGB565 does not fit in its PSRAM either. An OpenMV RT1062 alternative has 32 MB RAM and a supported OV5640 camera, but it has not been established as a supported flight-controller replacement. A Pixhawk 6X with a CM4/5 carrier instead uses an additional Linux compute module; it is not a $300 single-MCU solution.

References: [Pixhawk 4](https://docs.px4.io/main/en/flight_controller/pixhawk4), [Pixhawk 6X-RT memory](https://docs.px4.io/v1.15/en/flight_controller/pixhawk6x-rt), [Pixhawk CM4/5 carrier and bundle contents](https://holybro.com/products/pixhawk-rpi-cm4-baseboard), [OpenMV RT1062](https://docs.openmv.io/dev/openmvcam/quickref/openmv-rt1062.html).

### Altitude, ground distance and location are different measurements

| Measurement | Source | Meaning / limitation |
|---|---|---|
| Latitude/longitude and GPS altitude | External GNSS through FC | Requires a valid satellite fix. Standard-precision M10 is not RTK. GPS altitude uses a reference datum; it is not automatically height above local terrain. |
| Pressure and barometric altitude | FC's onboard SPL06 | Gives pressure-based altitude information; calibration, atmospheric changes and pressure exposure matter. It does not directly measure the distance to the tarp. |
| Estimated position, attitude and relative altitude | FC navigation estimator | Fuses available sensors. Altitude relative to home is not necessarily altitude above ground. Check estimator/fix health before using it. |
| Line-of-sight target distance | Six-pin TTL laser on Flamingo | Retained. Exact range, target reflectivity, sunlight behavior, interface and validity indicators remain pending the laser datasheet. Tilted line-of-sight distance is not vertical height without geometry. |

### Proposed FC-to-Flamingo connection - document only

Use **MicoAir405v2 UART4 / ArduPilot SERIAL4** for Flamingo, leaving UART3 for GPS and UART1 available for an RC receiver or other peripheral. This is a candidate allocation; recheck actual receiver/telemetry needs. UART5 is RX-only and UART6's default RX is inverted for SBUS, so neither is the baseline full-duplex payload port.

| FC connection | Flamingo connection | Purpose |
|---|---|---|
| T4 / UART4 TX | GPIO2 / S3 UART RX | FC sends navigation and sensor information |
| R4 / UART4 RX | GPIO1 / S3 UART TX | Flamingo requests data and can send results |
| GND | GND | Common signal reference |
| Power | Separate power plan below | No power contact or FC-to-Flamingo power path is assigned yet |

Use non-inverted **3.3 V UART logic**, not RS-232; verify the actual board pads/voltage before connecting. Candidate link: MAVLink 2, 115200 baud, 8N1. Configure `SERIAL4_PROTOCOL = 2` for MAVLink 2; set its baud rate to match Flamingo using the firmware's baud selection. No FC parameters or firmware have been changed. No RTS/CTS connection is reserved.

Request useful messages rather than transmitting images across this link:

| MAVLink message | Use on Flamingo |
|---|---|
| `HEARTBEAT`, `SYS_STATUS` | Detect FC presence and sensor health |
| `GLOBAL_POSITION_INT` | Estimated position, velocity, MSL altitude and altitude relative to home; retain units/datum |
| `GPS_RAW_INT` | GNSS fix type, satellite count and reported uncertainty/quality |
| `ATTITUDE` or `ATTITUDE_QUATERNION` | Camera orientation after applying the measured mounting transform |
| `SCALED_PRESSURE` when available | Barometric pressure/temperature; verify the actual firmware build emits it |
| `SYSTEM_TIME` / `TIMESYNC` as appropriate | Associate navigation samples with camera exposure and laser samples |

Start with modest requested rates, then measure delivered rate/latency during capture and logging. ArduPilot supports `MAV_CMD_SET_MESSAGE_INTERVAL`; check acknowledgements and actual received messages. Track stale data and fix/estimator validity; loss of FC telemetry must not silently leave the last position/altitude marked current. Initial integration should read telemetry before introducing any flight commands. The F405's 1 MB flash limits optional firmware features; verify the exact build includes those required by the vehicle. No onboard Lua scripting is assumed.

Connect GPS power to the FC's suitable 5 V output, GPS TX/RX across to FC R3/T3, and compass SDA/SCL to FC I2C, following the exact module wiring diagram. This is signal-level guidance, not a numbered GPS connector pinout. Sources: [serial protocol configuration](https://ardupilot.org/copter/docs/common-serial-options.html), [requesting ArduPilot data](https://ardupilot.org/dev/docs/mavlink-requesting-data.html), [MAVLink message definitions](https://mavlink.io/en/messages/common.html).

### What changes on Flamingo

- Remove the SAM-M8Q-0 from the **planned onboard BOM**. Its previous JLC part C5447387 remains historical, not a component to populate with the external-GPS baseline. No schematic or footprint has been removed by this document update.
- Do not add a separate onboard barometer, IMU or compass solely to duplicate the FC's data. An independent fallback would be a separate requirement, not part of this baseline.
- Reuse the formerly reserved GPS UART GPIO1/GPIO2 for FC telemetry and add a mating connector/cable to the eventual schematic.
- Keep ESP32-S3-WROOM-1-N16R8, OV5640 DVP/JPEG camera, six-pin laser, microSD, USB programming/debug and the provisional power circuits.
- The FC's normal battery input is **2S-6S**; Flamingo's existing **1S** charger/regulator plan is not automatically a shared supply. Final battery, FC power feed and any common regulated rail remain undecided. Do not connect raw FC battery voltage to S3, camera or a 5 V connector. Do not parallel independent regulated outputs.
- GPS/compass placement is now outside the Flamingo PCB outline. FC mounting, vibration clearance, GPS sky view, antenna separation and cable bends still consume payload space.

### Integration checks before relying on this architecture

- [ ] Confirm the final vehicle type, required flight modes/outputs and firmware target; demonstrate that the F405 build has the required features.
- [ ] Confirm FC/GPS stock, checkout price, cables, connector contact order and required power hardware.
- [ ] Finalize battery/power distribution for both boards and laser; verify UART logic levels and power sequencing.
- [ ] Calibrate FC sensors and GPS compass; demonstrate valid position, attitude and altitude on the ground station.
- [ ] Demonstrate timestamped MAVLink reception on Flamingo during camera capture and SD writes; test link loss/stale data.
- [ ] Validate camera optics and tarp detection at the intended distance; obtain and test the laser datasheet/protocol.
- [ ] Mount and test the full payload; no hardware or flight tests have been performed by this documentation update.

## Selected parts and compatible design proposals

The ESP32 processor is user selected. GPS/altitude sensing now come from the external flight-controller system above; the former onboard GNSS choice is superseded. The remaining exact onboard parts below are proposals, not purchased or hardware-validated. JLC codes identify catalog entries; the dated processor stock snapshot below does not establish availability or lead time for the other parts.

| Function | Manufacturer / part | JLCPCB number | Status and integration notes |
|---|---|---|---|
| Processor | Espressif ESP32-S3-WROOM-1-N16R8 | [C2913202](https://jlcpcb.com/partdetail/C2913202) | Current user-selected solder-down module, replacing the earlier P4. 16 MB onboard Quad SPI flash and 8 MB Octal PSRAM; Wi-Fi, Bluetooth LE, PCB antenna, and 40 MHz crystal included. Nominal supply: 3.3 V (allowed 3.0-3.6 V). Body: 18.0 x 25.5 x 3.1 mm. No separate program-flash IC or main crystal is needed. KiCad symbol/footprint family: RF_Module:ESP32-S3-WROOM-1; set the value to the full N16R8 ordering code. See the dated stock snapshot in the image-memory decision below; recheck sourcing and lead time before ordering. |
| Flight-controller telemetry connector | Mating connector/cable for FC UART4 TX/RX and GND | Pending exact connector | Required for the split architecture. Reserve S3 GPIO1 TX / GPIO2 RX; 3.3 V MAVLink UART. GPS, IMU and barometer are external to Flamingo. Physical connector, numbered contacts and optional power provision are not selected. |
| External camera | Waveshare OV5640 Camera Board (A), SKU 13926 | Buy separately | Proposed reference camera assembly: 5 MP, 8-bit DVP, SCCB control, JPEG output and 3.3 V input. Includes the sensor's 1.5 V / 2.8 V regulators; its DOVDD is 3.3 V in the published schematic. Use the 18-position header mapping below. This is a complete camera board, not a bare OV5640 flex sensor. |
| Camera carrier connector/cable | 18-position, 2 x 9 interconnect matching the Waveshare P1 header | Pending exact connector | Logical contact order documented below. Confirm actual pitch, male/female mating, pin-1 orientation and cable end-to-end mapping before choosing a footprint. The copied Pelican 20-pin FFC connector is not a direct substitute. |
| microSD socket | XUNPU TF-115-BCP9 | [C720505](https://jlcpcb.com/partdetail/Xunpu-TF_115BCP9/C720505) | Proposed reuse of the existing Pelican socket library. Operate at 3.3 V in SPI mode to conserve GPIO. Verify symbol/pad mapping and shell grounds; do not invent a card-detect contact. |
| USB-C receptacle | GCT USB4120-03-C | [C3445864](https://jlcpcb.com/partdetail/GCT-USB4120_03C/C3445864) | Proposed native USB 2.0 programming/console/JTAG connector. Vertical entry: confirm enclosure/cable access and exact manufacturer land pattern. Two 5.1 kohm CC pull-downs are required, one on each CC pin. |
| USB data ESD protection | ST USBLC6-2SC6 | [C7519](https://jlcpcb.com/partdetail/C7519) | Proposed USB2.0 ESD device. Verify pin mapping, VBUS reference and ground from ST documentation; place at connector. Do not substitute a different manufacturer's similarly named part without review. |
| 1-cell charger / power path | TI BQ24074RGTR | [C54313](https://jlcpcb.com/partdetail/TexasInstruments-BQ24074RGTR/C54313) | Proposed if using a single 4.2 V charge-voltage Li-ion/LiPo cell. Charger OUT supplies the regulator, not S3/camera directly. Existing RGTT CAD may be reused only after confirming the package/pin correspondence; RGTR is the reel-packaging variant. |
| Main 3.3 V regulator | TI TPS63070RNMR | [C109322](https://jlcpcb.com/partdetail/TexasInstruments-TPS63070RNMR/C109322) | Proposed buck-boost from charger OUT/battery system supply to regulated 3.3 V. Budget approximately 1 A for the 3.3 V rail as an initial design target; verify worst-case load, battery voltage, thermals and transient response. Exact 15-pin RNM footprint is required. |
| Laser connector | Six-position connector matched to actual rangefinder | Pending datasheet | Reserve a UART but leave contact order, supply and extra signals undecided. A 5 V TTL output needs appropriate translation before an S3 input. Battery-powered 5 V operation may require a separate boost rail, depending on the chosen laser. |
| GPIO / SPI connectors | Shared I2C and shared SPI with separate CS; optional UART header | Pending mechanical selection | Use the proposed pin budget below. General GPIO is limited; do not promise a large independent breakout while using camera, FC telemetry, laser, SD and USB together. |

## Camera interface compatibility review

**Documentation-checked path:** ESP32-S3-WROOM-1-N16R8 -> 8-bit LCD_CAM DVP -> Waveshare OV5640 Camera Board (A), configured for JPEG. Espressif's esp32-camera driver lists both ESP32-S3 and OV5640 support. This checks interface compatibility, not an assembled board: there has been no electrical test, capture test, throughput measurement or tarp-detection validation.

The reference is the Waveshare board's 18-position P1 connector. Its internal U1 sensor/flex pin numbers are different and must not be copied onto the carrier connector. The header exposes Y2-Y9, the upper eight sensor bits. Map Y2 to the driver's D0 and Y9 to D7. MIPI-only OV5675 or OV5640 assemblies and Raspberry Pi camera cables are not substitutes for this interface.

| Camera P1 contact | Published signal | Proposed S3 connection / driver function |
|---|---|---|
| 1 | 3.3V | Regulated 3.3 V camera supply |
| 2 | GND | Common ground |
| 3 | SIO_CLK | GPIO5 / pin_sccb_scl |
| 4 | SIO_DAT | GPIO4 / pin_sccb_sda |
| 5 | VSYNC | GPIO17 / pin_vsync |
| 6 | HREF | GPIO18 / pin_href |
| 7 | PCLK | GPIO16 / pin_pclk |
| 8 | XCLK | GPIO21 / pin_xclk, output from S3 |
| 9 | Y9 | GPIO15 / pin_d7 |
| 10 | Y8 | GPIO14 / pin_d6 |
| 11 | Y7 | GPIO13 / pin_d5 |
| 12 | Y6 | GPIO12 / pin_d4 |
| 13 | Y5 | GPIO11 / pin_d3 |
| 14 | Y4 | GPIO10 / pin_d2 |
| 15 | Y3 | GPIO9 / pin_d1 |
| 16 | Y2 | GPIO8 / pin_d0 |
| 17 | RESET | GPIO6 / pin_reset, active low |
| 18 | PWDN / OVPWDN | Leave unconnected on carrier initially; pin_pwdn = -1. Verify actual board revision before using this contact. |

Important published-schematic detail: U1's PWDN is held to ground through R7 (0 ohm), while P1 contact 18 goes through R6 to a net named OVPWDN. The drawing does not establish that header contact 18 controls U1 PWDN. Do not drive it as if it were an ordinary power-down input. For this baseline, leave it open and use the board's default active state; confirm actual stuffing and continuity before implementation. A different camera revision requires a fresh pinout review.

The camera board already shows 4.7 kohm SCCB pull-ups to 3.3 V and a reset pull-up/RC network. Do not automatically duplicate them or pull SCCB above 3.3 V. Its onboard regulators provide 1.5 V and 2.8 V; a bare sensor would require a separate power design. Add carrier supply decoupling near the camera connector after budgeting the module's existing capacitance and any chosen supply filter.

Use a short connection for the first prototype (approximately 5 cm or less as a design goal, not a guaranteed cable limit). Confirm pin-1 orientation on both ends and the real connector pitch. Provide a good ground return and keep the camera clock/data away from switching nodes and RF antenna clearances. Serial damping footprints for XCLK may be reserved, but the final value needs signal-integrity review.

Firmware starting point: esp32-camera, PIXFORMAT_JPEG, one frame buffer in PSRAM, 16 MB flash and Octal PSRAM enabled. A 20 MHz XCLK is an example starting configuration, not a promise of 5 MP throughput. First validate identification and small JPEG captures, then increase resolution toward 2592 x 1944. Read the returned buffer length; JPEG size varies with quality and scene detail. Process JPEG in sections or at a reduced decoded size; do not allocate a full 5 MP RGB565/RGB888 output in 8 MB PSRAM. No frame rate is promised.

### Image memory and processing decision - 2026-11-03

**Confirmed choice:** keep ESP32-S3-WROOM-1-N16R8 (C2913202), with **8 MB PSRAM and 16 MB flash**. No external RAM chip, 16 MB PSRAM upgrade or STM32 redesign is selected.

Capture the OV5640's full-resolution JPEG into one PSRAM frame buffer. Decode sequentially into a reusable strip/block buffer, check each block for tarp color, and retain candidate positions/results before reusing the buffer. Preserve image coordinates and join detections across block boundaries. Do not allocate the complete uncompressed 5 MP image.

| Decoded RGB565 buffer | Size at 2592 x 1944 source resolution |
|---|---:|
| Full image | 10,077,696 bytes (10.08 MB); exceeds PSRAM |
| One quarter of the pixels | 2,519,424 bytes (2.52 MB) |
| Example full-width strip, 64 rows | 331,776 bytes (0.33 MB) |

Quarter-image processing is a memory-budget example, not a requirement to allocate a quarter-frame or decode arbitrary quadrants independently. Prefer smaller sequential blocks/strips compatible with the decoder's alignment requirements. RGB565 uses two bytes per pixel. These sizes exclude the compressed JPEG, decoder workspace, firmware allocations and detection state; the complete memory budget must fit in available PSRAM.

Use Espressif's [esp_new_jpeg block decoder](https://components.espressif.com/components/espressif/esp_new_jpeg/versions/1.0.2/readme) as the implementation candidate. Block decoding support is documented; full-resolution capture/decode time and detection accuracy have not been measured. Validate maximum JPEG buffer use, peak free memory, processing time and tarp-color accuracy on actual hardware. JPEG size depends on scene detail and quality.

**Sourcing snapshot, 2026-11-03:** JLC's public catalog data for [C2913202](https://jlcpcb.com/partdetail/C2913202) reported 32,784 in regular inventory at approximately $5.36 each. This is a stock/price snapshot, not a reservation or lead-time guarantee; recheck checkout availability before ordering.

Sources: [Waveshare Board A manual](https://files.waveshare.com/upload/b/b8/OV5640_Camera_Board_%28A%29_User_Manual_EN.pdf), [Waveshare camera schematic](https://files.waveshare.com/upload/1/1e/OV5640-Camera-Board-Schematic.pdf), [Espressif camera driver](https://github.com/espressif/esp32-camera), [S3-WROOM datasheet](https://documentation.espressif.com/esp32-s3-wroom-1_wroom-1u_datasheet_en.pdf).

## Proposed GPIO budget - document only

These assignments demonstrate a non-overlapping candidate allocation for the exact N16R8 module. They are not implemented in the schematic or firmware. They must be checked again against the final schematic, boot behavior and selected peripherals.

| Interface | S3 GPIO allocation | Integration notes |
|---|---|---|
| Camera | GPIO4/5 SCCB, GPIO6 RESET, GPIO8-15 D0-D7, GPIO16 PCLK, GPIO17 VSYNC, GPIO18 HREF, GPIO21 XCLK | 15 GPIO; camera header 18 remains open as discussed above |
| Native USB | GPIO19 D-, GPIO20 D+ | Reserved for programming, console and USB JTAG |
| Flight-controller MAVLink UART | GPIO1 TX from S3, GPIO2 RX into S3 | Cross to MicoAir405v2 R4/T4 with common GND; replaces the former direct GPS UART; 3.3 V logic |
| Laser UART | GPIO38 TX from S3, GPIO39 RX into S3 | Supply, voltage translation and any auxiliary signals remain pending laser datasheet |
| Shared SPI clock/data | GPIO40 SCLK, GPIO41 MOSI, GPIO42 MISO | Shared by microSD and external SPI connector; coordinate transactions in firmware |
| microSD chip select | GPIO47 | Add a pull-up so SD is deselected during startup |
| External SPI chip select | GPIO48 | Separate CS with pull-up; verify peer is 3.3 V and releases MISO while deselected |
| Optional UART0 debug | GPIO43 TX, GPIO44 RX | Native USB already provides debug; retain UART header only if useful |
| Spare general GPIO | GPIO7 | One spare in this allocation; additional laser/PPS/control needs may require rearrangement |
| Boot/reserved | GPIO0, GPIO3, GPIO45, GPIO46 | Avoid peripheral loads while boot-strapping behavior is being finalized; GPIO0 remains available for the BOOT button |
| Memory pins | GPIO35, GPIO36, GPIO37 | Unavailable on N16R8 because they are used by Octal PSRAM |

GPIO47/48 are suitable for the 3.3 V N16R8 plan; do not apply this voltage assumption to the R16V module variants that have different voltage-domain restrictions. This candidate allocation uses USB JTAG, so GPIO39-42 are assigned to UART/SPI rather than external four-wire JTAG.

For an I2C breakout, expose the existing GPIO4/5 bus rather than claiming a separate bus: use compatible addresses, 3.3 V pull-ups, and coordinated I2C/SCCB driver ownership. For SPI, initialize the SD card into SPI mode before other devices use the bus, keep all CS lines inactive during startup, and ensure each device releases MISO. Shared-bus loading, speed and scheduling still need validation. [Espressif SD/SPI sharing guidance](https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-reference/peripherals/sdspi_share.html)

## Consistent power and support-component plan

Provisional assumption for **Flamingo only**: USB 5 V plus one protected Li-ion/LiPo cell with a 4.2 V charge limit. The separate flight controller normally uses a 2S-6S supply; the system-level power arrangement is unresolved. Connect USB VBUS to BQ24074 IN, battery to BAT, and charger power-path OUT to TPS63070 VIN. TPS63070 generates the common regulated 3.3 V rail. BQ24074 OUT can exceed the S3's 3.6 V maximum, so it must not feed S3 or camera directly. Charger current/input limits and thermal behavior remain to calculate from the actual cell and USB source.

| Support function | Proposed basis | Still required |
|---|---|---|
| S3 supply/reset/boot | 10 uF plus 100 nF near module; EN 10 kohm pull-up / 1 uF RC; RESET and BOOT buttons | Reference-design review, exact packages and startup timing |
| Charger support | Follow BQ24074 reference network; approximately 1 uF input and 4.7 uF OUT/BAT reference capacitors | Full capacitance/inrush review, ISET/ILIM/ITERM/TMR and battery TS/NTC settings; no fixed charge current assumed |
| Buck-boost | TPS63070 with 1.5 uH reference inductor; 312 kohm / 100 kohm candidate feedback gives about 3.296 V | Exact inductor current/saturation rating, RNM footprint, effective input/output capacitance, VAUX bypass, EN/PS/VSEL/FB2/PG configuration and layout |
| USB | 2 x 5.1 kohm CC pull-downs, USBLC6-2SC6, candidate 22 ohm D+/D- series resistors | Connector/pad mapping, USB impedance/layout, ESD/VBUS connections, total VBUS capacitance and input-current policy |
| SD and SPI | 3.3 V socket, local decoupling, mode-appropriate CMD/DAT pull-ups, separate CS pull-ups | Exact resistor/capacitor MPNs, transient load and shared-bus verification |
| Camera | Complete Waveshare Board A supplied with 3.3 V; uses onboard core/analog regulators | Exact mating connector/cable, current budget and revision/continuity check |
| Laser | Reserve UART and connector space | Actual model, power rail/current, all six contacts and logic-level translation |
| External FC interface | GPIO1/2 3.3 V UART plus common GND | Exact mating connector/cable, protection, power sequencing and whether any shared regulated supply is appropriate |

With the proposed charger power path, Pelican's TPS2116 source mux is not automatically needed. Its TPS61023 5 V boost is not the S3's main regulator; retain it only as a future candidate if the rangefinder needs a battery-backed 5 V rail. Do not reuse Pelican's 1 uH inductor as the TPS63070's 1.5 uH reference part without redesign. All passive MPNs and quantities remain provisional until the schematic exists.

Sources: [BQ24074 datasheet](https://www.ti.com/lit/ds/symlink/bq24074.pdf), [TPS63070 datasheet](https://www.ti.com/lit/ds/symlink/tps63070.pdf), [S3 hardware checklist](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32s3/schematic-checklist.html).

## Previous processor alternatives

These are historical P4 candidates, not the current S3 selection or components to fit alongside it.

| Alternative | JLCPCB number | Notes |
|---|---|---|
| Waveshare ESP32-P4-Module-32MB | [C9900261841](https://jlcpcb.com/partdetail/57402886-ESP32_P4_Module32MB/C9900261841) | Candidate assembled module. Waveshare specifies 32 MB PSRAM, 32 MB onboard flash, ESP32-C6 wireless companion, 3.3 V supply, 25 x 25 mm. JLC lists the matching name under JLCPCB Assembly rather than Waveshare; confirm manufacturer, exact pinout/footprint, chip revision, and sourcing. Not selected. |
| Espressif ESP32-P4NRW32X | [C54540373](https://jlcpcb.com/partdetail/EspressifSystems-ESP32P4NRW32X/C54540373) | Current-generation bare-chip alternative with 32 MB PSRAM; not selected. Pin 54 differs from the older chip; use revision-specific reference designs. |

## Components still to select

| Function | Requirements / next check |
|---|---|
| Flash / PSRAM configuration | The N16R8 module already includes 16 MB flash and 8 MB PSRAM. Configure firmware for those capacities and Octal PSRAM; choose a suitable firmware/OTA/data partition table. Flash is persistent storage and does not increase working RAM. |
| Processor supplies | Provide regulated 3.3 V, module decoupling, and sufficient peak current for the ESP32 plus peripherals. Follow the S3 module reference design; the bare-P4 core/PSRAM rail circuit is no longer required. |
| Module clock | Main 40 MHz crystal is integrated in the S3-WROOM module; no separate main crystal/load network is required on the carrier PCB. |
| Reset / boot | S3 EN reset network, GPIO0 boot control, boot-strapping review, and accessible recovery/programming controls. |
| Main regulator | Proposed TPS63070RNMR buck-boost for 3.3 V, fed by BQ24074 OUT under the provisional 1-cell battery architecture; complete support components, footprint, load budget and layout remain to verify. |
| USB programming / JTAG | Native S3 USB Serial/JTAG, USB-C receptacle, protection, CC resistors and power/ground treatment. Reserve GPIO19 (D-) and GPIO20 (D+); no USB-UART bridge is required for the native programming path. |
| Laser rangefinder connector | Six-pin TTL interface requested. Exact sensor, pin order, supply/current, logic voltage, and remaining signal functions are pending; do not guess. Reserve an independent UART. |
| microSD interface | Proposed TF-115-BCP9 socket in SPI mode, sharing SCLK/MOSI/MISO with expansion and using its own CS. Verify pulls, supply decoupling, contact mapping, bus initialization and software scheduling. |
| Camera connector | Use a matching 18-position 2 x 9 interconnect for the proposed Waveshare OV5640 Board A. P1 mapping is documented above; exact pitch, footprint, cable polarity and actual board revision still need confirmation. The Pelican 20-pin FFC connector is not a direct fit. |
| FC telemetry connector | Required S3 GPIO1 TX / GPIO2 RX plus GND; exact mating type and contact order pending. Retrieve navigation and altitude from FC over MAVLink; no local GNSS/barometer fitted in the current baseline. |
| Optional GPIO expansion | Share the camera I2C/SCCB and SD SPI buses with compatible external devices. The candidate allocation leaves GPIO7 spare; final laser auxiliary signals may consume it. |
| Optional independent USB-UART | Only if an independent UART-over-USB connection is needed; native USB Serial/JTAG already supports console/debug functions. |
| Wireless / antenna integration | Wi-Fi and Bluetooth LE are integrated in the selected S3 module; no separate companion is required. Respect the module antenna keepout and enclosure clearance. |

## Pelican libraries copied to Flamingo

These are available locally through sym-lib-table and fp-lib-table. They remain reuse candidates, not approved design choices.

| Libraries | Intended function |
|---|---|
| U_BQ24074RGTT | Single-cell battery charger |
| U_TPS2116DRLR | Historical USB/battery source mux; not required by default with the proposed BQ24074 power path |
| U_TPS61023DRLR; L_FHD4020S-1R0MT | Historical 5 V boost and 1 uH inductor; not the S3 3.3 V regulator or TPS63070 inductor selection |
| Q_DMG2305UX-13; Q_NDS7002A | Battery gating and indicator control |
| J_43045-0401 | Battery/external-switch connector |
| C_GRM155R61A105KE15D; C_GRM155R61A106ME11D; C_GRM155R71C104KA88D; C_GRM188R61A226ME15D; C_GRM188R61A475KE15D | Capacitors: 1 uF, 10 uF, 100 nF, 22 uF, 4.7 uF |
| R_RC0402FR | Resistors with multiple values |
| LED_LTST-C193KGKT-5A; LED_LTST-C193KRKT-5A | Power/camera indicators |
| J_0.5K-A-20PB | Historical 20-pin FFC camera connector; do not use for Waveshare Board A 18-pin P1 without an explicitly designed adapter |
| J_TF-115-BCP9 | microSD socket |
| power | Local schematic power symbols; no physical footprint |

## Verification before release

- [x] Processor selected: ESP32-S3-WROOM-1-N16R8, 8 MB PSRAM and 16 MB flash.
- [x] Split FC/payload architecture documented; cheapest sourced FC/GPS baseline and alternatives compared.
- [ ] FC/GPS hardware received and configured; navigation, altitude and timestamped MAVLink validated on Flamingo.
- [ ] S3 module power/reset/boot circuit, antenna keepout, and memory configuration reviewed.
- [ ] Each symbol pin number and footprint checked against manufacturer documentation.
- [x] Proposed camera assembly and logical interface checked from manufacturer documents: Waveshare OV5640 Board A, 3.3 V, 8-bit DVP/JPEG, P1 18-pin mapping.
- [ ] Confirm physical module revision, connector/cable and optics; demonstrate identification, JPEG capture and tarp detection on hardware.
- [ ] Demonstrate 5 MP JPEG capture and sequential block decoding within 8 MB PSRAM; measure peak memory, processing time, color accuracy and detections across block boundaries.
- [ ] Rangefinder datasheet and six-pin mating connector obtained.
- [ ] Power budget, battery details, charging settings, and startup/shutdown behavior reviewed.
- [x] Non-overlapping candidate GPIO allocation and voltage assumptions documented for N16R8.
- [ ] Check that allocation against the final schematic and firmware, shared buses, boot state and exact laser requirements.
- [ ] JLC sourcing/stock and assembly eligibility rechecked before ordering.

## Preliminary board size estimate - 2026-11-03

Keep **50 x 80 mm** as a conservative Flamingo planning allowance and **50 x 100 mm** as the maximum. This is not a measured placement/routing result. Removing onboard GNSS may allow a smaller PCB, but no new outline or packing exercise has been performed.

This allowance now includes the S3 module, microSD, USB, power/charging circuitry, camera connector, six-pin laser connector, FC telemetry connector and modest GPIO/SPI headers. **No SAM-M8Q antenna/ground-plane region is required on Flamingo under the current external-GPS plan.** The earlier GNSS-driven board-size reasoning is superseded.

| Assembly / constraint | Planning allowance |
|---|---|
| Flamingo S3 module | 18.0 x 25.5 mm module body plus Espressif antenna clearance; place antenna end at a suitable board edge. |
| MicoAir405v2, external to Flamingo | Manufacturer body 36 x 36 x 8 mm, 30.5 x 30.5 mm mounting pattern; reserve standoffs, vibration clearance and cables. Stacking is a mechanical proposal, not a validated fit. |
| M10G-5883 GPS/compass, external | Manufacturer body 20 x 20 x 8 mm; requires sky view and separation from interference. A cable allows placement independent of FC and Flamingo. |
| Camera, battery and laser | External assemblies; mounting envelopes, cable bends and optics must be budgeted separately. |
| Power and connectors | Regulator/inductor/charger layout and accessible cable/card insertion can determine the final PCB size. |

Sources: [Espressif module dimensions](https://documentation.espressif.com/esp32-s3-wroom-1_wroom-1u_datasheet_en.pdf), [antenna placement guidance](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32s3/pcb-layout-design.html), [FC dimensions](https://micoair.com/flightcontroller_micoair405v2/), [GPS dimensions](https://micoair.com/en/docs/gps-rtk/gps).

## Application context

Detect a colored 16 x 16 m tarp at approximately 1 km. Lens field of view, viewing angle, exposure, motion blur, and color calibration determine detectability. Permanent image storage is optional; temporary image buffers are required by the selected capture path. A 2592 x 1944 RGB565 frame alone requires 10,077,696 bytes, exceeding 8 MB PSRAM. The proposed S3 path captures camera-compressed JPEG and decodes/processes sections or a reduced-resolution image. Buffer sizes, decoding speed, color tolerances and detection performance remain to validate.

## References

- [Proposed camera assembly: Waveshare OV5640 Board A](https://www.waveshare.com/product/modules/cameras-audio-video/cameras/ov5640-camera-board-a.htm)
- [Waveshare Board A manual](https://files.waveshare.com/upload/b/b8/OV5640_Camera_Board_%28A%29_User_Manual_EN.pdf)
- [Waveshare camera schematic / P1 header](https://files.waveshare.com/upload/1/1e/OV5640-Camera-Board-Schematic.pdf)
- [ESP32-S3 / OV5640 camera driver](https://github.com/espressif/esp32-camera)

- [Selected ESP32-S3-WROOM-1-N16R8 listing](https://jlcpcb.com/partdetail/C2913202)
- [S3-WROOM-1/1U datasheet: memory variants and dimensions](https://documentation.espressif.com/esp32-s3-wroom-1_wroom-1u_datasheet_en.pdf)
- [Espressif legacy P4 v1.3 datasheet and EOL status](https://documentation.espressif.com/esp32-p4-chip-revision-v1.3_datasheet_en.html)
- [S3 hardware design guidelines](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32s3/index.html)
- [S3 USB Serial/JTAG](https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-guides/usb-serial-jtag-console.html)
- [Espressif supported camera sensors and ISP limitations](https://github.com/espressif/esp-video-components/blob/master/esp_cam_sensor/README.md)
- [OV5675 product brief](https://www.ovt.com/wp-content/uploads/2022/01/OV5675-PB-v1.2-WEB.pdf)
- [Waveshare P4 module specifications](https://www.waveshare.com/product/esp32-p4-module.htm)

## Processor selection history - 2026-10-27

Selected by the user: **Espressif ESP32-S3-WROOM-1-N16R8**, JLCPCB **C2913202**. This selection is now reflected in the main parts table above.

- **PSRAM: 8 MB**, for working memory.
- **Flash: 16 MB**, included on the module for firmware and persistent storage. No separate program-flash chip is needed.
- Flash is separate from PSRAM and does not add working memory. Firmware and data partitions share the 16 MB flash capacity.
- Selection reaffirmed 2026-11-03: retain 8 MB PSRAM and use sequential JPEG block decoding. See the dated sourcing snapshot above; delivery lead time remains unconfirmed.
- [JLCPCB listing](https://jlcpcb.com/partdetail/C2913202)
- [Manufacturer datasheet](https://documentation.espressif.com/esp32-s3-wroom-1_wroom-1u_datasheet_en.pdf)
