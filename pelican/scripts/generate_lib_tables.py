#!/usr/bin/env python3
"""Regenerate sym-lib-table and fp-lib-table from libraries/ contents.

Scans libraries/ for *.kicad_sym files and footprints.pretty directories,
and rewrites the project's library tables to reference all of them. Run
this after adding, renaming, or removing a library folder under libraries/
instead of hand-editing the tables.

Convention assumed (matches existing libraries/ layout): each part gets its
own folder containing <name>.kicad_sym and, optionally, a
footprints.pretty/ directory. The folder/file stem is used as the library
nickname.
"""

import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
LIBRARIES_DIR = PROJECT_ROOT / "libraries"
SYM_LIB_TABLE = PROJECT_ROOT / "sym-lib-table"
FP_LIB_TABLE = PROJECT_ROOT / "fp-lib-table"


def lib_entry(name: str, uri: str) -> str:
    return (
        f'\t(lib (name "{name}") (type "KiCad") (uri "{uri}") '
        f'(options "") (descr ""))'
    )


def find_sym_entries():
    entries = {}
    for path in sorted(LIBRARIES_DIR.rglob("*.kicad_sym")):
        name = path.stem
        rel = path.relative_to(PROJECT_ROOT).as_posix()
        if name in entries:
            sys.exit(
                f"error: duplicate symbol library nickname '{name}':\n"
                f"  {entries[name]}\n  {rel}"
            )
        entries[name] = rel
    return entries


def find_fp_entries():
    entries = {}
    for path in sorted(LIBRARIES_DIR.rglob("footprints.pretty")):
        if not path.is_dir():
            continue
        name = path.parent.name
        rel = path.relative_to(PROJECT_ROOT).as_posix()
        if name in entries:
            sys.exit(
                f"error: duplicate footprint library nickname '{name}':\n"
                f"  {entries[name]}\n  {rel}"
            )
        entries[name] = rel
    return entries


def write_table(table_path: Path, root_tag: str, entries: dict):
    lines = [f"({root_tag}", "\t(version 7)"]
    for name, rel in sorted(entries.items()):
        uri = "${KIPRJMOD}/" + rel
        lines.append(lib_entry(name, uri))
    lines.append(")")
    table_path.write_text("\n".join(lines) + "\n")


def footprint_names_in(fp_dir_rel: str) -> set:
    # KiCad resolves a footprint by its FILENAME within the .pretty dir, not by
    # the internal (footprint "...") token — so the file stem is the real name.
    return {mod.stem for mod in (PROJECT_ROOT / fp_dir_rel).glob("*.kicad_mod")}


def validate_footprint_links(sym_entries: dict, fp_entries: dict) -> list:
    """Check every symbol's Footprint property resolves to a real library:footprint."""
    problems = []
    fp_name_cache = {}
    for sym_name, sym_rel in sym_entries.items():
        text = (PROJECT_ROOT / sym_rel).read_text()
        for value in re.findall(r'\(property "Footprint" "([^"]*)"', text):
            if value == "":
                continue
            if ":" not in value:
                problems.append(f"{sym_rel}: Footprint '{value}' has no 'library:footprint' prefix")
                continue
            nickname, fp_name = value.split(":", 1)
            if nickname not in fp_entries:
                problems.append(f"{sym_rel}: Footprint '{value}' references unknown fp library '{nickname}'")
                continue
            if nickname not in fp_name_cache:
                fp_name_cache[nickname] = footprint_names_in(fp_entries[nickname])
            if fp_name not in fp_name_cache[nickname]:
                problems.append(f"{sym_rel}: Footprint '{value}' not found in {fp_entries[nickname]}")
    return problems


def main():
    sym_entries = find_sym_entries()
    fp_entries = find_fp_entries()

    write_table(SYM_LIB_TABLE, "sym_lib_table", sym_entries)
    write_table(FP_LIB_TABLE, "fp_lib_table", fp_entries)

    print(f"wrote {SYM_LIB_TABLE.relative_to(PROJECT_ROOT)} ({len(sym_entries)} libraries)")
    print(f"wrote {FP_LIB_TABLE.relative_to(PROJECT_ROOT)} ({len(fp_entries)} libraries)")

    problems = validate_footprint_links(sym_entries, fp_entries)
    if problems:
        print(f"\n{len(problems)} footprint link problem(s):")
        for p in problems:
            print(f"  - {p}")
        sys.exit(1)


if __name__ == "__main__":
    main()
