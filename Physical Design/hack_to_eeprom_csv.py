#!/usr/bin/env python3
"""
hack_to_eeprom_csv.py

Reads a compiled Nand2Tetris .hack binary file (one 16-bit binary string
per line, e.g. "0000000000010101") and produces:

  1. A combined CSV with columns: address, instruction (binary), low_byte (hex), high_byte (hex)
  2. A low-byte-only CSV, for programming the first AT28C256 (D0-D7 = instruction[0..7])
  3. A high-byte-only CSV, for programming the second AT28C256 (D0-D7 = instruction[8..15])

Usage:
    python3 hack_to_eeprom_csv.py program.hack

Outputs (in the same directory as the input file, or current directory):
    program_combined.csv
    program_low.csv
    program_high.csv
"""

import sys
import os
import csv

ROWS_COLS = 16          # 16 columns per row, matching Digital's ROM data grid view
AT28C256_DEPTH = 32768  # 15-bit address space


def parse_hack_file(path):
    """Read a .hack file and return a list of 16-bit integers, one per instruction."""
    instructions = []
    with open(path, "r") as f:
        for line_num, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue  # skip blank lines
            if len(line) != 16 or any(c not in "01" for c in line):
                raise ValueError(
                    f"Line {line_num} is not a valid 16-bit binary string: {line!r}"
                )
            instructions.append(int(line, 2))
    return instructions


def split_bytes(value):
    """Given a 16-bit int, return (low_byte, high_byte) as ints 0-255."""
    low_byte = value & 0xFF          # instruction[0..7]
    high_byte = (value >> 8) & 0xFF  # instruction[8..15]
    return low_byte, high_byte


def write_grid_csv(path, byte_values, pad_to=AT28C256_DEPTH):
    """
    Write a CSV in the same layout as Digital's ROM data grid:
    header row = Address, 0x0000, 0x0001, ... 0x000F
    each data row = a hex row-start address, then 16 decimal byte values.

    byte_values: list of ints (0-255), one per address, in order.
    pad_to: total number of addresses to fill (remaining filled with 0),
            matching the full AT28C256 depth so the grid is complete.
    """
    padded = list(byte_values) + [0] * max(0, pad_to - len(byte_values))

    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        header = ["Address"] + [f"0x{i:04X}" for i in range(ROWS_COLS)]
        writer.writerow(header)

        for row_start in range(0, len(padded), ROWS_COLS):
            row_values = padded[row_start:row_start + ROWS_COLS]
            row_label = f"0x{row_start:04X}"
            writer.writerow([row_label] + row_values)


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 hack_to_eeprom_csv.py <program.hack> [--no-pad]")
        sys.exit(1)

    input_path = sys.argv[1]
    pad = "--no-pad" not in sys.argv[2:]

    if not os.path.isfile(input_path):
        print(f"Error: file not found: {input_path}")
        sys.exit(1)

    instructions = parse_hack_file(input_path)
    num_instr = len(instructions)

    if num_instr > AT28C256_DEPTH:
        print(
            f"Warning: {num_instr} instructions exceeds {AT28C256_DEPTH} (15-bit address "
            f"space, AT28C256 depth). Extra instructions will still be written but won't "
            f"fit in a single chip's address range."
        )

    base_name = os.path.splitext(os.path.basename(input_path))[0]
    out_dir = os.path.dirname(input_path) or "."

    low_path = os.path.join(out_dir, f"{base_name}_low.csv")
    high_path = os.path.join(out_dir, f"{base_name}_high.csv")

    low_bytes = []
    high_bytes = []
    for value in instructions:
        low_byte, high_byte = split_bytes(value)
        low_bytes.append(low_byte)
        high_bytes.append(high_byte)

    pad_to = AT28C256_DEPTH if pad else len(instructions)
    write_grid_csv(low_path, low_bytes, pad_to=pad_to)
    write_grid_csv(high_path, high_bytes, pad_to=pad_to)

    print(f"Parsed {num_instr} instructions from {input_path}")
    print(f"Wrote low-byte grid CSV:  {low_path}  (program into EEPROM #1, D0-D7 = instruction[0..7])")
    print(f"Wrote high-byte grid CSV: {high_path}  (program into EEPROM #2, D0-D7 = instruction[8..15])")
    if pad:
        print(f"Both files padded with 0 up to address {AT28C256_DEPTH - 1} (full AT28C256 depth).")
    else:
        print("Files NOT padded (--no-pad used) — only contain your actual instructions.")


if __name__ == "__main__":
    main()
