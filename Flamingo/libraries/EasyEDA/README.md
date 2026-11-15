# EasyEDA project library

This folder holds C-number imports for Flamingo. The older individually named libraries alongside it remain unchanged. EasyEDA imports share one symbol library and one footprint library; they do not need a separate folder for every component.

```text
libraries/EasyEDA/
  EasyEDA.kicad_sym       schematic symbols
  EasyEDA.pretty/         PCB footprints
  EasyEDA.3dshapes/        3D models
```

The library nickname stays `EasyEDA`. Existing references such as `EasyEDA:XT30PW-M` keep working.

## Import another C-number

1. Open the Flamingo project, then launch `impartGUI (IPC API)`.
2. Keep **Local Library** checked. Leave **Single Library** unchecked, or name it `EasyEDA` if enabled.
3. Enter the C-number in **EasyEDA / LCSC Part#** and click the adjacent **Import** button. The separate **Start** button is for downloaded library-file imports.
4. In the schematic press **A**, then search the manufacturer part name. For C431092, search `XT30PW-M`.
5. Reopen the chooser/editor if it has cached the previous library contents. Leave overwrite off unless intentionally replacing an existing part.

## Registered paths

| Resource | Project-relative path |
|---|---|
| Symbol library | `${KIPRJMOD}/libraries/EasyEDA/EasyEDA.kicad_sym` |
| Footprint library | `${KIPRJMOD}/libraries/EasyEDA/EasyEDA.pretty` |
| Model directory | `${KIPRJMOD}/libraries/EasyEDA/EasyEDA.3dshapes` |

These entries are already in Flamingo's project library tables. Another computer can use the checked-in library files without the importer. Include all three resources and the library tables in Git.

## Importer adjustment on this computer

The installed impart GUI version originally wrote Local Library C-number imports directly into the project root. A small local adjustment in its `impart_action.py` now uses `libraries/EasyEDA` whenever that folder exists, and sets matching project-relative model paths. Projects without this folder and imports using a different library name retain the original behavior. Downloaded ZIP/library-file importing is unchanged.

Restart the importer after this setup. Plugin updates may overwrite this adjustment. Before importing after an update, confirm it still reports the nested destination. A copy of the change is recorded in [impart-project-libraries.patch](impart-project-libraries.patch) for maintenance; it is not an upstream plugin feature. Other computers need the adjustment for future imports into this layout, but not for viewing or using the existing parts.

The original plugin and library files were backed up outside the repository at `C:/Users/sikap/AppData/Local/Temp/flamingo-library-backup-20261114-221617`.

## Current import

| C-number | Symbol | Footprint |
|---|---|---|
| C431092 | `EasyEDA:XT30PW-M` | `EasyEDA:CONN-TH_XT30PW-M` |

This is the through-hole, right-angle XT30PW-M30.G.Y. Importing CAD does not validate polarity, pad dimensions or current stock.
