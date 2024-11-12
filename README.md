# Sudoku CNF Generator

## Overview

This project generates CNF files from Sudoku puzzles for SAT solvers. Each input file contains multiple Sudoku strings (81 characters each), and the program outputs CNF files ready for solving.

## Files

- **sudoku-rules-9x9.txt**: Common rules for all 9x9 Sudoku puzzles.
- **sudoku\_cnf\_generator.py**: Script to generate CNF files from Sudoku puzzles.

## How It Works

1. Reads Sudoku strings (81 characters per line: digits for values, dots for empty cells).
2. Generates CNF clauses for each puzzle.
3. Appends general Sudoku rules from `sudoku-rules-9x9.txt`.
4. Saves each CNF in an output folder named after the input file.

## Usage

```sh
python sudoku_cnf_generator.py <input_filename>
```

- **\<input\_filename>**: File with Sudoku puzzles, each line must have 81 characters.

### Example

```sh
python sudoku_cnf_generator.py top91.sdk.txt
```

- Creates an output folder `top91.sdk`.
- Generates CNF files like `sudoku_1.cnf`, `sudoku_2.cnf`, etc.

Note: The current version of the script uses a default hardcoded file (top91.sdk.txt). 
This can be changed to use any input file by modifying the <input_filename> argument when running the script.

## Functions

- **`SudokuCNFGenerator`**: Class to generate CNF clauses.
  - `generate_cnf()`: Generates CNF for the given puzzle.
  - `save_cnf_with_rules(filename)`: Saves CNF with general rules.
- **`create_output_directory(filename)`**: Creates an output directory.
- **`process_sudoku_file(filename, rules_filename, output_dir)`**: Processes each Sudoku puzzle and generates CNF files.

## Notes
- The input file (top91.sdk.txt) is currently hardcoded in the script, but this can be easily modified to accept any filename as an argument.
- Ensure input lines have exactly 81 characters.
- Invalid lines are skipped.

Enjoy solving Sudoku with SAT solvers!

