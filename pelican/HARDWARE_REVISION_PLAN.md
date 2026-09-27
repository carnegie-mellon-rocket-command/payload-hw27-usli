# Pelican PCB revision plan

Updated: 2026-09-27. Baseline: upstream commit `f4fa639f4edbf574fbee9e2e419bedeffa69f34d` ("pushed place").

This document plans the payload adaptation. The upstream project has been imported; the Ethernet removal and new interfaces have not yet been implemented. Pin assignments below were checked against the imported schematic's KiCad XML netlist, but still require verification against the exact module variant and electrical specifications before release.

## 1. Objective and physical arrangement

Adapt Pelican for the payload by removing unused Ethernet, adding a six-pin laser-rangefinder interface, exposing more GPIO, and adding a likely cabled board-to-board SPI connection. Preserve the required camera, USB, storage, microphone, power, and debug functions.

The comment that the layout is "optimized for a switchband mounted camera with external USB and LED access" likely means the original camera installation sat at the rocket switchband, with USB and indicators accessible from outside. That physical arrangement influenced connector positions, component placement, and trace paths. Confirm the intended mounting with the original designer; this interpretation is not a verified mechanical requirement.

The payload layout may be rearranged to suit its enclosure, cable exits, and access requirements. Treat the existing placement as a starting point. Establish camera position, USB access, visible LEDs, mounting points, rangefinder cable exit, and inter-board cable routing before committing to placement.

## 2. Repository and imported baseline

| Item | Current state |
|---|---|
| Parent repository / origin | [payload-hw27-usli](https://github.com/carnegie-mellon-rocket-command/payload-hw27-usli) |
| Design source | [avionics-hw27-pelican main](https://github.com/carnegie-mellon-rocket-command/avionics-hw27-pelican/tree/main) |
| Imported source commit | `f4fa639f4edbf574fbee9e2e419bedeffa69f34d` |
| PCB | 91 footprints, four copper layers, 36 track segments, one via, no zones |
| Remaining connectivity | 235 unrouted connections reported by KiCad at import |
| Validation completed | Imported upstream files compared to Git blobs, allowing line-ending conversion; PCB parsed; matching schematic netlist exported |
| Validation outstanding | ERC, full DRC, mechanical review, impedance/timing checks, and hardware validation |

The board is mostly placed with some routing started; it is not an empty board or a finished routed design.

The `pelican/` folder is ordinary tracked content in the parent repository, originally imported through Git subtree metadata in commit `e351d88` and merged in PR #2. It is not a separate checkout or submodule. The latest source was fetched and its project files imported into this folder; the parent `origin` was not changed and no subtree merge was performed for this update.

The earlier plan was committed locally as `2e0fdbf`. The latest upstream import and this updated plan are working-tree changes at the time of writing; nothing has been pushed by this work.

Project structure:

- Parent repository root: SolidWorks mechanical parts and assemblies.
- `pelican.kicad_pro`: project settings and design rules.
- `pelican.kicad_sch`: top-level schematic, linking power, core, camera, microphone, storage, USB, and Ethernet sheets in `schematics/`.
- `pelican.kicad_pcb`: placed PCB and initial routing.
- `libraries/`: project symbols, footprints, and models; `sym-lib-table` and `fp-lib-table` resolve local libraries through `${KIPRJMOD}`.
- `scripts/generate_lib_tables.py`: regenerate library tables after library changes.
- `pcb/`: currently contains `.gitkeep`.
- The old schematic PDF was removed by upstream. Generate a fresh export after revisions.
- Upstream `.gitignore` now excludes `.kicad_prl`, locks, and backups. Previously tracked preferences may still appear as modified despite this ignore rule.

Pre-import files, including the user's local KiCad edits, were saved in `pelican-backups/before-upstream-20260927-164711.zip`. Local `.kicad_prl` preferences were retained. Reopen/reload the imported project before editing; do not overwrite it by saving an older open KiCad session.

## 3. Ethernet removal

Remove the Ethernet sheet instance, jack `J801`, resistors `R801/R802`, capacitors `C801` through `C804`, and their obsolete PCB footprints, traces, and labels. Clean up the core-sheet Ethernet connections and review the now-unused `GNDETH` network.

| Module pad | Current connection | Planned treatment |
|---|---|---|
| 85, 86 | ETH_RX_N, ETH_RX_P | Dedicated PHY pins; handle unused pins per module documentation |
| 87, 88 | ETH_TX_N, ETH_TX_P | Dedicated PHY pins; not GPIO expansion candidates |
| 92 / GPIO1_D1 | LED_ETH_YELLOW | Available for reassignment after removal |
| 93 / GPIO1_D0 | LED_ETH_GREEN | Available for reassignment after removal |

Removing the carrier circuitry does not itself disable the module's Ethernet hardware. Update firmware/device-tree configuration as required.

## 4. Six-pin rangefinder interface

The six-pin connector is for a laser rangefinder, not an assumed standard FTDI cable. Obtain its exact model/datasheet before assigning connector pins.

Resolve supply voltage, running/startup current, UART logic voltage, baud rate, connector part and mating orientation, pin numbering, and the purpose/direction of every extra signal. "TTL" alone does not establish voltage compatibility.

Candidate independent UART:

| Function | Core1106 pad | Current carrier use |
|---|---|---|
| UART1_M0 TX / GPIO1_A3 | 68 | Unconnected |
| UART1_M0 RX / GPIO1_A4 | 69 | Unconnected |

Connect module TX to rangefinder RX and module RX to rangefinder TX. Add level translation if the verified electrical levels require it. Check the power budget and choose protection and filtering appropriate to the cable. Do not assign the two additional sensor pins by guessing that they are enable, trigger, or flow control.

Preserve the existing debug UART on module pads 59 (TX) and 58 (RX), exposed in the imported design through `UART_TP304` and `UART_TP305`; `UART_TP303` exposes VCC_3V3. The previous revision's four-pin `UART_J301` header is no longer the current implementation.

## 5. Cabled SPI connection

The imported schematic has already moved LEDs away from SPI0_M0. These pins are unconnected on the carrier and are candidates for the new interface:

| SPI function | Module pad / GPIO |
|---|---|
| MISO | 98 / GPIO1_C3 |
| MOSI | 99 / GPIO1_C2 |
| SCLK | 100 / GPIO1_C1 |
| CS0 | 101 / GPIO1_C0 |
| Optional CS1 | 91 / GPIO1_D2 |

No LED relocation is currently required to use these pins. The earlier plan's SPI/LED conflict applied to the older design and is superseded.

Avoid selecting SPI1 pads 41–44 solely because they look unconnected on the carrier: they overlap eMMC functions and may be used inside the module. Confirm the exact Core1106 variant, internal storage wiring, bank voltages, and supported pinmux for any allocation.

Proposed connector topology, not a finalized pinout:

| Pin | Signal | Pin | Signal |
|---|---|---|---|
| 1 | SCLK | 2 | GND |
| 3 | MOSI | 4 | GND |
| 5 | MISO | 6 | GND |
| 7 | CS0 | 8 | GND |
| 9 | IRQ, optional | 10 | GND |

Use a keyed/locking connector with an appropriate cable assembly. This proposal assumes the peer board is separately powered and places ground beside each signal in a suitable cable. Confirm the physical conductor mapping rather than relying on connector numbering alone. Pad 93 is an IRQ candidate after Ethernet removal.

Determine cable length, peer device, controller/peripheral roles, SPI mode, target clock rate, logic levels, and power sequencing. Cable propagation and signal edge speed matter as well as clock frequency. Evaluate source termination and return paths; if the required cable is unsuitable for direct SPI, reconsider the link architecture. Do not promise a cable length or clock rate without analysis and testing.

## 6. GPIO expansion

A revised 12-signal candidate allocation, reserving UART1 pads 68/69, SPI0 pads 98–101, optional CS1 pad 91, and optional IRQ pad 93:

| Module pad | GPIO | Present carrier state |
|---|---|---|
| 60 | GPIO0_A2 | Unconnected |
| 63 | GPIO0_A5 | Unconnected |
| 64 | GPIO0_A6 | Unconnected |
| 65 | GPIO1_A0 | Unconnected |
| 66 | GPIO1_A1 | Unconnected |
| 67 | GPIO1_A2 | Unconnected |
| 70 | GPIO1_B0 | Unconnected |
| 71 | GPIO1_B1 | Unconnected |
| 90 | GPIO1_D3 | Unconnected |
| 92 | GPIO1_D1 | Available after Ethernet LED removal |
| 108 | GPIO2_A6 | Unconnected |
| 109 | GPIO2_A7 | Unconnected |

Pads 110/111 are additional candidates if more signals are needed. Pads 94–97 currently serve LED_REC, LED_BAT, LED_HEALTH, and LED_ALIVE, respectively, and are not free expansion pins.

Finalize the GPIO count, input/output roles, current requirements, voltage domains, and any desired I2C/PWM/interrupt functions. Check internal module use, boot functions, pull states, and device-tree ownership. An unconnected carrier pad is not proof that it is unrestricted or 3.3 V compatible. Include adequate ground pins and only expose supply rails with a defined power budget.

## 7. Differential pairs and other routing constraints

The current schematic has six physical differential pairs. Ethernet removal leaves four: three camera pairs and one USB pair.

| Interface | Nets | Required routing attention |
|---|---|---|
| MIPI CSI camera | CSI_CLK_P/N, CSI_D0_P/N, CSI_D1_P/N | Highest-priority signal group: short direct module-to-connector routes, controlled impedance, within-pair skew and device-specific clock/data timing limits, minimal discontinuities |
| USB 2.0 | USB_P/N, continuing as USB_ESD_P/N through ESD protection | One physical pair split into named net sections; maintain impedance, return path, and clean connector/ESD transitions |
| Ethernet, until removed | ETH_TX_P/N and ETH_RX_P/N | Two PHY-to-jack/magnetics pairs; remove their routing requirements with the interface |

Typical starting differential impedance targets are 100 ohms for MIPI CSI and 90 ohms for USB 2.0. Final geometry and timing limits must come from the manufacturer-approved stackup and actual device specifications. Do not assume a universal length-matching tolerance or that all pairs must have identical length. Include relevant module and cable contributions in the timing assessment.

Other difficult routing:

- **Boost converter:** `BOOST_U202`, `L201`, and nearby capacitors require compact high-current loops, a small switching node, and appropriate copper widths. Keep sensitive feedback away from switching noise. Follow the TPS61023 layout guidance rather than treating these as ordinary connections.
- **microSD:** SDMMC clock, command, and four data signals are single-ended but timing-sensitive. Keep paths short with continuous return references and check the actual operating mode's timing requirements.
- **Camera control:** route CAM_MCLK with a good return path; preserve I2C pull-up voltage compatibility and reset behavior.
- **Microphone:** protect low-level analog signals and bias from switching-converter and digital-clock noise.
- **Cabled SPI:** include the cable, connector, return conductors, termination, and peer board in signal-integrity analysis.
- **Power distribution:** size battery, boost, USB, sensor supply, and ground paths for their currents; preserve charger and power-mux behavior.

The Core1106 contains the processor and memory subsystem. Do not assume this carrier needs a new external DDR routing exercise; verify the module boundaries and avoid repurposing its storage pins blindly.

## 8. Stackup and KiCad rules

The imported PCB specifies four copper layers and an overall thickness of approximately 2.0066 mm:

| Layer | Existing designation |
|---|---|
| F.Cu | Top signals |
| In1.Cu | GND |
| In2.Cu | PWR |
| B.Cu | Bottom signals |

The file specifies 0.035 mm copper per layer, 0.1 mm outer dielectrics, a 1.6466 mm inner core, and 0.01 mm solder mask on each face. This is a design-file stackup, not confirmation of a fabrication service's construction.

There are currently no copper zones. Naming a layer GND does not create a continuous ground plane. Top-layer fast signals can reference In1 once properly implemented; bottom-layer signals need particular care because their adjacent layer is designated PWR and may contain splits.

Only a default netclass is configured, with 0.2 mm differential trace width and 0.25 mm gap and no interface-specific netclass assignments. Those numbers do not establish the required impedance.

Before routing:

1. Agree the stackup and manufacturing limits with the fabricator.
2. Calculate controlled-impedance widths and gaps for the intended layers.
3. Configure netclasses/custom constraints for camera, USB, SDMMC, SPI, and power as appropriate.
4. Enter justified skew/length constraints from device documentation.
5. Establish continuous reference copper and return transitions; keep fast routes away from plane splits and milled regions.
6. Resolve the mechanical pocket before committing copper in that area.

## 9. Blind milled slot / underside pocket

A blind milled slot is a recess cut partway into the board from one face. Material remains at the bottom of the recess. A through-slot cuts all the way through; a blind via is an electrical inter-layer connection and is a different feature.

Conceptual cross-section of a pocket milled from the bottom, not to scale:

```text
Top surface     =============================
Remaining PCB   #############################
Pocket region   ########             ########
Bottom surface  ########             ########
                         open below
```

The actual PCB has `User.1` named "bottom blind slots layer", containing an approximately 20.5 x 23.5 mm rectangular outline. It suggests an underside pocket, possibly for mechanical clearance. Its purpose is not established, and no milling depth was found in the inspected annotations. The outline alone is not a complete manufacturing instruction.

Decide whether the payload still needs this feature. If retained, specify:

- Pocket purpose, location, size, machining side, and datum.
- Milling depth, depth tolerance, and minimum remaining board thickness.
- Corner radii/tool access and dimensional tolerances.
- Which copper layers fall within the removed material.
- Copper, via, and component keepouts including manufacturing tolerances.
- Remaining mechanical strength and mounting loads.
- A fabrication drawing and explicit manufacturer acceptance of the operation.

Depth-controlled milling can remove bottom or internal copper, expose conductors, interrupt return paths, and change local impedance. Avoid routing critical signals across the recess unless the remaining stackup and reference paths have been explicitly engineered. A drawing on a user layer does not itself enforce copper keepouts or tell the fabricator the machining depth. Do not turn it into an ordinary through-cut on Edge.Cuts unless that is the intended mechanical change.

## 10. Work sequence and completion criteria

1. **Resolve interfaces and mechanics.** Obtain the rangefinder datasheet and exact Core1106 variant; define GPIO needs, SPI cable/peer/rate, mounting, connector access, and the pocket's purpose/depth or removal.
2. **Revise the schematic.** Remove Ethernet; add the verified rangefinder interface, SPI connector, and GPIO expansion; preserve required peripherals and power controls. Update library tables as needed.
3. **Validate connectivity.** Run ERC, export the netlist, and review every new connector pin and voltage domain. Check that obsolete Ethernet nets/components are removed and existing required functions remain connected.
4. **Update firmware assignments.** Configure UART1, SPI0, GPIO ownership, pulls and startup states, and unused Ethernet. Confirm no debug-console or boot-function conflict with the rangefinder.
5. **Update PCB placement.** Transfer schematic changes into the existing placed board. Adjust placement for the payload mechanics, short camera/USB paths, converter loops, and cable access. Retain existing routing only where it still fits the revised nets and constraints.
6. **Establish manufacturing rules.** Approve stackup, impedance geometry, current-carrying copper, pocket details, keepouts, and fabrication limits before detailed routing.
7. **Route and review.** Prioritize converter loops and sensitive/high-speed paths, then remaining signals. Add reference/power copper, verify return paths, and apply justified length/skew tuning.
8. **Release checks.** Run DRC with no unexplained violations or unintended unconnected nets. Review schematic/PCB consistency, mechanical fit, connectors/cable mating, fabrication outputs, and blind-pocket documentation. Generate fresh schematic and assembly exports.
9. **Bring-up.** Check rails/current consumption, debug access, camera, USB, microSD, microphone, rangefinder communication, GPIO, and SPI operation over the intended cable. Verify performance under representative concurrent loads.

A successful netlist export or clean DRC alone does not demonstrate electrical or mechanical correctness. Record unresolved issues rather than treating this plan as fabrication approval.

## 11. Decisions still needed

| Decision | Why it matters |
|---|---|
| Rangefinder model/datasheet and connector | Six-pin assignment, supply, current, logic levels, extra signals |
| Exact Core1106 variant | Internal storage use, available pins, I/O bank voltages |
| SPI peer, cable length, clock/mode, power arrangement | Connector, termination, link feasibility, software roles |
| GPIO count and intended functions | Final pin allocation and protection requirements |
| Mounting, camera location, USB/LED access | Placement and cable routing |
| Pocket purpose and depth, or permission within mechanical design to omit it | Copper keepouts, remaining stackup, board strength and fabrication |
| PCB manufacturer and approved stackup | Impedance geometry and manufacturing constraints |

## 12. References and evidence

- Local evidence: imported `pelican.kicad_pcb`, `pelican.kicad_pro`, schematic sheets, library symbols, and KiCad-exported XML connectivity from the imported revision.
- [Exact upstream baseline](https://github.com/carnegie-mellon-rocket-command/avionics-hw27-pelican/tree/f4fa639f4edbf574fbee9e2e419bedeffa69f34d).
- [Luckfox Core1106 pinout and downloadable documentation](https://wiki.luckfox.com/Core1106/Pinout/). The linked module schematic PDF could not be retrieved during the audit; manufacturer cross-checking remains required.
- [TI high-speed interface layout guidance](https://edgeworker.ti.com/lit/an/spraar7j/spraar7j.pdf), including typical USB 2.0 and CSI impedance guidance. Apply actual connected-device limits rather than copying another device's timing limits.
- [TI TPS61022/TPS61023 layout guidance](https://www.ti.com/lit/an/slvaes4/slvaes4.pdf).
- [Eurocircuits mechanical-layer documentation](https://www.eurocircuits.com/technical-guidelines/pcb-design-guidelines/mechanical-layer/), for communicating mechanical fabrication requirements; confirm blind milling with the selected manufacturer separately.
