import sys
import os

# Predefined Hack symbols mapping to RAM addresses
PREDEFINED_SYMBOLS = {
    'SP': 0, 'LCL': 1, 'ARG': 2, 'THIS': 3, 'THAT': 4,
    'SCREEN': 16384, 'KBD': 24576
}
for i in range(16):
    PREDEFINED_SYMBOLS[f'R{i}'] = i

# Hack C-Instruction Lookups
COMP_TABLE = {
    '0': '0101010', '1': '0111111', '-1': '0111010', 'D': '0001100',
    'A': '0110000', '!D': '0001101', '!A': '0110001', '-D': '0001111',
    '-A': '0110011', 'D+1': '0011111', 'A+1': '0110111', 'D-1': '0001110',
    'A-1': '0110010', 'D+A': '0000010', 'D-A': '0010011', 'A-D': '0000111',
    'D&A': '0000000', 'D|A': '0010101',
    'M': '1110000', '!M': '1110001', '-M': '1110011', 'M+1': '1110111',
    'M-1': '1110010', 'D+M': '1000010', 'D-M': '1010011', 'M-D': '1000011',
    'D&M': '1000000', 'D|M': '1010101'
}

DEST_TABLE = {
    '': '000', 'M': '001', 'D': '010', 'MD': '011',
    'A': '100', 'AM': '101', 'AD': '110', 'AMD': '111'
}

JUMP_TABLE = {
    '': '000', 'JGT': '001', 'JEQ': '010', 'JGE': '011',
    'JLT': '100', 'JNE': '101', 'JLE': '110', 'JMP': '111'
}

def clean_line(line):
    """Removes comments and whitespace."""
    line = line.split('//')[0]
    return line.strip().replace(" ", "")

def generate_intel_hex_line(address, byte_value):
    """Generates a standard Intel HEX record string for a single byte."""
    record_type = 0
    byte_count = 1
    # Checksum: 2's complement of the sum of all fields modulo 256
    checksum = (byte_count + (address >> 8) + (address & 0xFF) + record_type + byte_value) & 0xFF
    checksum = (-checksum) & 0xFF
    return f":01{address:04X}00{byte_value:02X}{checksum:02X}\n"

def assemble_to_ints(asm_filepath):
    """Translates Hack Assembly into a list of 16-bit integer instruction values."""
    with open(asm_filepath, 'r') as f:
        lines = f.readlines()

    # Pass 1: Parse Label Declarations (LOOP)
    symbol_table = PREDEFINED_SYMBOLS.copy()
    rom_address = 0
    cleaned_lines = []
    
    for line in lines:
        cleaned = clean_line(line)
        if not cleaned:
            continue
        if cleaned.startswith('(') and cleaned.endswith(')'):
            label = cleaned[1:-1]
            symbol_table[label] = rom_address
        else:
            cleaned_lines.append(cleaned)
            rom_address += 1

    # Pass 2: Variable Allocation & Machine Code Translation
    next_variable_address = 16
    instructions = []

    for line in cleaned_lines:
        if line.startswith('@'): # A-Instruction
            val_str = line[1:]
            if val_str.isdigit():
                val = int(val_str)
            else:
                if val_str not in symbol_table:
                    symbol_table[val_str] = next_variable_address
                    next_variable_address += 1
                val = symbol_table[val_str]
            instructions.append(val & 0xFFFF)
        else: # C-Instruction
            dest, comp, jump = "", "", ""
            if '=' in line:
                dest, rest = line.split('=')
            else:
                dest, rest = "", line
            
            if ';' in rest:
                comp, jump = rest.split(';')
            else:
                comp, jump = rest, ""

            binary_str = f"111{COMP_TABLE[comp]}{DEST_TABLE[dest]}{JUMP_TABLE[jump]}"
            instructions.append(int(binary_str, 2))
            
    return instructions

def main():
    if len(sys.argv) < 2:
        print("Usage: python hack_to_intel_hex.py <path_to_file.asm>")
        sys.exit(1)

    asm_file = sys.argv[1]
    if not os.path.exists(asm_file):
        print(f"Error: File '{asm_file}' not found.")
        sys.exit(1)

    # Compile the .asm to numbers
    try:
        raw_words = assemble_to_ints(asm_file)
    except KeyError as e:
        print(f"Assembly Translation Error: Invalid token or field syntax {e}")
        sys.exit(1)

    base_name = os.path.splitext(asm_file)[0]
    upper_file_path = f"{base_name}_upper.hex"
    lower_file_path = f"{base_name}_lower.hex"

    # Write the Upper (High Byte) and Lower (Low Byte) files
    with open(upper_file_path, 'w') as f_up, open(lower_file_path, 'w') as f_lo:
        for addr, word in enumerate(raw_words):
            high_byte = (word >> 8) & 0xFF
            low_byte = word & 0xFF
            
            f_up.write(generate_intel_hex_line(addr, high_byte))
            f_lo.write(generate_intel_hex_line(addr, low_byte))

        # Append standard Intel End-of-File (EOF) records
        f_up.write(":00000001FF\n")
        f_lo.write(":00000001FF\n")

    print(f"Successfully generated:\n -> {upper_file_path}\n -> {lower_file_path}")

if __name__ == "__main__":
    main()

