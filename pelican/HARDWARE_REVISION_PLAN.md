# Pelican interface revision — design review

Inspected 2026-09-27 using KiCad 10's exported XML netlist. This is a proposed allocation, not a released schematic or PCB revision. Hardware files have not been changed.

## Repository and project structure

- Repository root: `payload-hw27-usli/`; mechanical SolidWorks parts and assemblies live at the root.
- Git remote `origin`: https://github.com/carnegie-mellon-rocket-command/payload-hw27-usli.git
- Current branch: `main`, tracking `origin/main`; both local refs pointed at `83a4068` during inspection. No remote fetch was performed.
- `pelican/` was imported with Git subtree metadata in commit `e351d88`, from source commit `1a82895`, then merged in PR #2. It is ordinary tracked content in the parent repository, not an independently connected Git repository or submodule. The original source repository URL is not recorded in the inspected remote configuration or subtree commit message.
- `pelican.kicad_pro`: project settings; `pelican.kicad_sch`: top-level schematic linking seven sheets in `schematics/` (power, core, camera, microphone, storage, USB, Ethernet).
- `libraries/`: local symbols and footprints. `sym-lib-table` and `fp-lib-table` use `${KIPRJMOD}` paths. Regenerate these with `scripts/generate_lib_tables.py` after changing local libraries.
- `pelican.kicad_pcb`: currently an empty board with setup/layers but no footprints, tracks, or outline. `pcb/` contains only `.gitkeep`.
- `pelican.kicad_sch.pdf` is an existing export, not the editable source.
- Existing uncommitted changes were present in `.kicad_pcb`, `.kicad_prl`, and `.kicad_pro`. KiCad lock files also indicate an open editing session; coordinate disk edits with saving/reloading that session.
- No tracked README, `.github` workflow, or `.gitmodules` was found in the inspected tree. Project-local `.gitignore` excludes locks and backups but does not exclude `.kicad_prl`.

## Ethernet removal

The removable carrier circuitry is the Ethernet sheet: `ETH_J801`, `R801`, `R802`, and `C801`–`C804`. Remove its top-level sheet instance and clean up the corresponding core-sheet connections.

| Core1106 pad | Existing net | Result of removal |
|---|---|---|
| 85–88 | ETH_RX_N/P, ETH_TX_N/P | Dedicated PHY connections; do not treat as GPIO |
| 94 | LED_ETH_YELLOW | Frees GPIO1_C7 |
| 95 | LED_ETH_GREEN | Frees GPIO1_C6 |

Unused PHY pins must be handled according to the exact module documentation. Carrier removal alone does not disable the module's Ethernet hardware in software.

## Rangefinder UART

User intent: six-pin TTL connector for a laser rangefinder. Model, connector pin order, supply requirements, logic levels, and the two extra signal functions are still unknown; a generic six-pin FTDI header must not be assumed compatible.

- Keep existing `UART_J301` for debug: pin 1 = VCC_3V3, pin 2 = module TX (pad 59), pin 3 = module RX (pad 58), pin 4 = GND.
- Candidate independent sensor UART: UART1_M0 TX on module pad 68 (GPIO1_A3), RX on pad 69 (GPIO1_A4). Both are unconnected in the exported carrier netlist.
- Connect module TX to sensor RX and module RX to sensor TX, with translation if required by the verified logic levels.
- Reserve the sensor's additional pins only after identifying its interface. Do not guess enable, trigger, flow-control, or power connections.
- Confirm regulator capacity, startup current, module I/O voltage, and software pinmux before finalizing.

## Cabled SPI

SPI0_M0 is available in the module symbol but its main pins are already assigned:

| Signal | Module pad | Current use |
|---|---|---|
| MISO | 98 / GPIO1_C3 | LED_BAT, driving Q204 gate |
| MOSI | 99 / GPIO1_C2 | LED_STORE, through R602 |
| SCLK | 100 / GPIO1_C1 | LED_UART, through R302 |
| CS0 | 101 / GPIO1_C0 | LED_ALIVE, through R301 |
| Optional CS1 | 91 / GPIO1_D2 | Unconnected |

Preferred candidate: reclaim pads 98–101 for SPI0, relocating the four LED/control nets to unused pads 108–111 after module voltage and firmware checks. Do not simply attach an SPI connector to the existing LED-loaded nets. Removing Ethernet alone does not free the SPI0 group.

SPI1_M0 uses pads 41–44, which overlap eMMC signals. Although unconnected on the carrier schematic, they may be used inside the module. Do not use them without verifying the exact Core1106 variant and internal storage wiring.

Proposed connector topology for review: keyed 2x5, odd pins 1/3/5/7/9 = SCLK/MOSI/MISO/CS0/IRQ, even pins 2/4/6/8/10 = GND. This provides a ground conductor beside each signal in a suitable cable. The other board would be separately powered. Select an actual locking connector and cable assembly after cable length, clock rate, and peer-board requirements are known; signal integrity and termination remain to be designed.

## GPIO expansion candidate

With UART1 pads 68/69 reserved, LEDs tentatively moved to 108–111, and Ethernet removed, a candidate 12-signal expansion is:

`60, 63, 64, 65, 66, 67, 70, 71, 90, 92, 94, 95`.

These correspond to GPIO0_A2, GPIO0_A5, GPIO0_A6, GPIO1_A0, GPIO1_A1, GPIO1_A2, GPIO1_B0, GPIO1_B1, GPIO1_D3, GPIO1_D1, GPIO1_C7, GPIO1_C6. The first ten are unconnected in the current carrier netlist; 94/95 become available after Ethernet removal. Pad 93 is another possible IRQ signal for the SPI connector.

This is an allocation candidate, not proof all pins are usable at 3.3 V. Check module bank voltages, boot/default functions, internal connections, and device-tree assignments. Do not assume every unconnected carrier pad is available inside the module. Provide ground returns on the final expansion connector.

## Implementation sequence and validation

1. Identify rangefinder model and exact Core1106 variant; establish cable length, SPI role/rate, and GPIO voltage requirements.
2. Save the active KiCad session; make the coordinated schematic changes, including LED reassignment and the three connectors.
3. Export the netlist again; verify every connector pin, absence of Ethernet components, and preservation of camera, USB, storage, and power-control nets.
4. Run ERC and inspect the schematic visually. Netlist export succeeded during this audit; ERC and electrical validation have not been completed.
5. Update firmware/device tree for UART, SPI, GPIO, relocated LEDs, and unused Ethernet.
6. Populate the empty PCB from the revised schematic, place connectors against mechanical constraints, route, and run DRC before fabrication.

Manufacturer reference: https://wiki.luckfox.com/Core1106/Pinout/ . The linked manufacturer schematic PDF could not be retrieved during this audit; pin allocations above come from the repository symbol and KiCad-exported connectivity and still require manufacturer cross-checking.
