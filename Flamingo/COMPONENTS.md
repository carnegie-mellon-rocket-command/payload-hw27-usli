# Flamingo component tracker

Updated: 2026-10-27.

Flamingo is a new design. Pelican is a source of reusable components and circuits; the Pelican rework is canceled. This is a selection tracker, not a verified or fabrication-ready BOM. A copied library does not establish that its circuit is placed, validated, or suitable for Flamingo.

## Selected parts

| Function | Manufacturer / part | JLCPCB number | Status and integration notes |
|---|---|---|---|
| Processor | Espressif ESP32-P4NRW32 | [C22387510](https://jlcpcb.com/partdetail/EspressifSystems-ESP32P4NRW32/C22387510) | User selected. Bare QFN-104, 10 x 10 mm chip; 32 MB in-package PSRAM. External program flash required. No integrated Wi-Fi/Bluetooth radio. Non-X version is EOL per Espressif; confirm lifecycle, sourcing, chip revision, and matching symbol before design freeze. JLC lists Standard assembly only; stock not verified. |
| GNSS | u-blox SAM-M8Q-0 | [C5447387](https://jlcpcb.com/partdetail/UBLOX-SAM_M8Q0/C5447387) | User selected. UART or I2C; review manufacturer integration manual, antenna placement, power, backup supply, and interface requirements. Symbol/footprint not yet verified. |
| Camera sensor | OMNIVISION OV5675 | Pending exact module | Intended 5 MP camera, 2592 x 1944, MIPI CSI-2 RAW10. Exact camera assembly, lens, connector, rails, and pinout pending. ESP32-P4 driver/capture support must be demonstrated; do not assume OV5640/OV5645 drivers are interchangeable. |

## Processor alternatives under consideration

These are alternatives, not components to fit alongside the selected processor.

| Alternative | JLCPCB number | Notes |
|---|---|---|
| Waveshare ESP32-P4-Module-32MB | [C9900261841](https://jlcpcb.com/partdetail/57402886-ESP32_P4_Module32MB/C9900261841) | Candidate assembled module. Waveshare specifies 32 MB PSRAM, 32 MB onboard flash, ESP32-C6 wireless companion, 3.3 V supply, 25 x 25 mm. JLC lists the matching name under JLCPCB Assembly rather than Waveshare; confirm manufacturer, exact pinout/footprint, chip revision, and sourcing. Not selected. |
| Espressif ESP32-P4NRW32X | [C54540373](https://jlcpcb.com/partdetail/EspressifSystems-ESP32P4NRW32X/C54540373) | Current-generation bare-chip alternative with 32 MB PSRAM; not selected. Pin 54 differs from the older chip; use revision-specific reference designs. |

## Components still to select

| Function | Requirements / next check |
|---|---|
| External program flash | Required if using bare P4. Select capacity, voltage, ESP-IDF compatibility, exact package, and JLC availability. Route dedicated Quad SPI flash signals according to the reference design. |
| Processor supplies | Follow reference design for exact P4 revision, including core DCDC and peripheral/analog/PSRAM rails. A generic 3.3 V input alone does not complete the bare-chip power circuit. |
| Crystal and load network | Select from exact processor reference design and crystal specifications. |
| Reset / boot | CHIP_PU reset network, boot strapping, and accessible recovery/programming controls. |
| Main regulator | Choose after battery/USB architecture and load budget are defined. Pelican's nominal 5 V boost circuit is not a drop-in 3.3 V supply. |
| USB programming / JTAG | Native P4 USB Serial/JTAG connection, USB-C receptacle, protection, CC resistors, and correct power/ground treatment. Verify selected module exposes required pins if switching to a module. |
| Laser rangefinder connector | Six-pin TTL interface requested. Exact sensor, pin order, supply/current, logic voltage, and remaining signal functions are pending; do not guess. Reserve an independent UART. |
| microSD interface | Pelican socket library copied. Confirm SDMMC pins, pulls, supply, card detect, and software support for P4. |
| Camera connector | Pelican connector library copied. Confirm exact OV5675 assembly pinout, pitch, contact orientation, reset, clocks, and power before reuse. |
| Optional GPIO expansion | Expose I2C, SPI, grounds, and spare GPIO after required interfaces and boot restrictions are allocated. |
| Optional independent USB-UART | Only if an independent UART-over-USB connection is needed; native USB Serial/JTAG already supports console/debug functions. |
| Optional wireless companion | Bare P4 lacks Wi-Fi/Bluetooth; select a companion/module only if wireless is required. |

## Pelican libraries copied to Flamingo

These are available locally through sym-lib-table and fp-lib-table. They remain reuse candidates, not approved design choices.

| Libraries | Intended function |
|---|---|
| U_BQ24074RGTT | Single-cell battery charger |
| U_TPS2116DRLR | USB/battery source selection |
| U_TPS61023DRLR; L_FHD4020S-1R0MT | Pelican boost converter; reassess output voltage and topology |
| Q_DMG2305UX-13; Q_NDS7002A | Battery gating and indicator control |
| J_43045-0401 | Battery/external-switch connector |
| C_GRM155R61A105KE15D; C_GRM155R61A106ME11D; C_GRM155R71C104KA88D; C_GRM188R61A226ME15D; C_GRM188R61A475KE15D | Capacitors: 1 uF, 10 uF, 100 nF, 22 uF, 4.7 uF |
| R_RC0402FR | Resistors with multiple values |
| LED_LTST-C193KGKT-5A; LED_LTST-C193KRKT-5A | Power/camera indicators |
| J_0.5K-A-20PB | Camera ribbon connector |
| J_TF-115-BCP9 | microSD socket |
| power | Local schematic power symbols; no physical footprint |

## Verification before release

- [ ] Final processor choice: bare chip versus assembled module, exact revision.
- [ ] External flash, crystal, and required power circuit selected if using bare chip.
- [ ] Each symbol pin number and footprint checked against manufacturer documentation.
- [ ] Exact camera module and lens selected; demonstrate capture and tarp detection on hardware.
- [ ] Rangefinder datasheet and six-pin mating connector obtained.
- [ ] Power budget, battery details, charging settings, and startup/shutdown behavior reviewed.
- [ ] GPIO allocation and voltage domains documented.
- [ ] JLC sourcing/stock and assembly eligibility rechecked before ordering.

## Application context

Detect a colored 16 x 16 m tarp at approximately 1 km. Lens field of view, viewing angle, exposure, motion blur, and color calibration determine detectability. Permanent image storage is optional; temporary image buffers are required by the selected capture path. A 2592 x 1944 frame is about 6.30 MB as packed RAW10 or 10.08 MB in 16-bit containers; extra buffers and processing memory must also be budgeted.

## References

- [Selected processor listing](https://jlcpcb.com/partdetail/EspressifSystems-ESP32P4NRW32/C22387510)
- [Espressif legacy P4 v1.3 datasheet and EOL status](https://documentation.espressif.com/esp32-p4-chip-revision-v1.3_datasheet_en.html)
- [P4 hardware design guidelines](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32p4/index.html)
- [P4 USB/JTAG debugging](https://docs.espressif.com/projects/esp-idf/en/stable/esp32p4/api-guides/jtag-debugging/index.html)
- [Espressif supported camera sensors and ISP limitations](https://github.com/espressif/esp-video-components/blob/master/esp_cam_sensor/README.md)
- [OV5675 product brief](https://www.ovt.com/wp-content/uploads/2022/01/OV5675-PB-v1.2-WEB.pdf)
- [Waveshare P4 module specifications](https://www.waveshare.com/product/esp32-p4-module.htm)
## Processor selection update - 2026-10-27

Selected by the user: **Espressif ESP32-S3-WROOM-1-N16R8**, JLCPCB **C2913202**. This supersedes the earlier processor selection recorded above.

- **PSRAM: 8 MB**, for working memory.
- **Flash: 16 MB**, included on the module for firmware and persistent storage. No separate program-flash chip is needed.
- Flash is separate from PSRAM and does not add working memory. Firmware and data partitions share the 16 MB flash capacity.
- Current JLCPCB stock and lead time for this part are not confirmed.
- [JLCPCB listing](https://jlcpcb.com/partdetail/C2913202)
- [Manufacturer datasheet](https://documentation.espressif.com/esp32-s3-wroom-1_wroom-1u_datasheet_en.pdf)
