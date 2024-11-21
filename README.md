Sudoku SAT Solver Project

Table of Contents

	1.	Introduction
	2.	Prerequisites
	3.	Code Files
	1.	Sudoku CNF Generator
	•	Description
	•	Features
	•	Input Format
	•	Examples
	•	Output
	•	Variable Encoding
	•	Usage
	•	Notes
	2.	DPLL.py
	•	Description
	•	Usage
	•	Example
	3.	CDCL.py
	•	Description
	•	Usage
	•	Example
	4.	SAT.py
	•	Description
	•	Usage
	•	Configuration Options
	•	Example
	5.	experiment.py
	•	Description
	•	Usage
	•	Example
	4.	Usage Instructions
	1.	Generating CNF Files from Sudoku Puzzles
	•	Example
	2.	Running DPLL.py
	•	Example
	3.	Running CDCL.py
	•	Example
	4.	Running SAT.py
	•	Configuration Options
	•	Example
	5.	Running experiment.py
	5.	Relation Between the Code Files
	6.	How the Experiment Works
	7.	License

1. Introduction

This project provides tools and algorithms for solving Sudoku puzzles via SAT solving:
	•	Sudoku CNF Generator: Converts Sudoku puzzles into CNF files in DIMACS format.
	•	DPLL.py: Implementation of the DPLL (Davis-Putnam-Logemann-Loveland) SAT solver.
	•	CDCL.py: Implementation of the CDCL (Conflict-Driven Clause Learning) SAT solver.
	•	SAT.py: Unified command-line interface to run the solvers with different configurations.
	•	experiment.py: Script to compare solver performance across multiple Sudoku instances.

Both solvers support the VSIDS (Variable State Independent Decaying Sum) heuristic for variable selection, which can enhance performance by prioritizing variables involved in conflicts.

2. Prerequisites

	•	Python 3.x
	•	NumPy (required for experiment.py)

Install NumPy using pip:

pip install numpy

3. Code Files

3.1. Sudoku CNF Generator

Description

The Sudoku CNF Generator is a tool that generates CNF (DIMACS format) files for Sudoku puzzles of supported sizes (4x4, 9x9, and 16x16). It reads Sudoku puzzles from an input file where each line represents a single puzzle, and generates CNF files by translating the puzzle constraints into CNF clauses and appending the general Sudoku rules based on the grid size.

Features

	•	Supported Sizes: Handles 4x4, 9x9, and 16x16 Sudoku puzzles.
	•	Input File: Reads Sudoku strings from an input file where each line represents a single puzzle.
	•	Output Directory: Creates an output directory named after the input file to store the generated CNF files.
	•	Automatic Rule File Selection: Automatically selects the correct rule file (sudoku-rules-4x4.txt, sudoku-rules-9x9.txt, sudoku-rules-16x16.txt) based on the puzzle size.
	•	DIMACS CNF Format: Generates clauses in DIMACS format with a header specifying the number of variables and clauses.
	•	Error Handling:
	•	Checks for invalid Sudoku sizes.
	•	Reports unsupported puzzle sizes.
	•	Handles missing or invalid rule files.

Input Format

The input file should contain Sudoku puzzles as strings where:
	•	Each line represents a Sudoku puzzle.
	•	Empty cells are denoted by a period (.).
	•	Characters for cells can include:
	•	1-9 for 4x4 and 9x9 puzzles.
	•	A-F (case-insensitive) for 16x16 puzzles, in addition to 1-9.

Examples

For a 9x9 Sudoku puzzle:

53..7....6..195....98....6.8...6...34..8..6...3...2...6.6....28....419..5....8..79

For a 16x16 Sudoku puzzle:

4C..A......3...1..B.....8....56D9.4......E...2.....6.A..F.8.....7...1...G...C.E...

Output

	•	CNF files are saved in an output directory named after the input file (without extension).
	•	Each CNF file corresponds to a single puzzle and includes:
	•	The puzzle constraints translated into CNF clauses.
	•	Rules for Sudoku constraints based on the grid size.

Variable Encoding

Variables in the CNF are encoded using the following formula:
	•	For 4x4 and 9x9 grids:

Variable = N^2 * (row - 1) + N * (column - 1) + (value - 1) + 1


	•	For 16x16 grids:

Variable = 17^2 * row + 17 * column + value



Here:
	•	N is the grid size (4, 9, or 16).
	•	row and column are 1-based indices.
	•	value is the numeric or letter value of the cell.

Usage

Run the script with the following command:

python sudoku_cnf_generator.py <input_filename>

Replace <input_filename> with your file’s name.

Notes

	•	Ensure that the rule files (sudoku-rules-4x4.txt, sudoku-rules-9x9.txt, sudoku-rules-16x16.txt) are in the same directory as the script.
	•	Supported Sudoku sizes are strictly 4x4, 9x9, and 16x16.
	•	Invalid or unsupported puzzles will be skipped with an appropriate error message.

3.2. DPLL.py

Description

DPLL.py implements the DPLL algorithm for solving SAT problems. It can operate with or without the VSIDS heuristic for variable selection.

Usage

python DPLL.py [VSIDS] <filename> [-v]

	•	VSIDS (optional): Variable selection heuristic.
	•	vsids or True: Use the VSIDS heuristic.
	•	non-vsids or False: Do not use the VSIDS heuristic.
	•	both: Run the solver twice, with and without VSIDS.
	•	Default: False (non-VSIDS).
	•	<filename> (required): Path to the DIMACS CNF file.
	•	-v or --verbose (optional): Enable verbose output.

Example

python DPLL.py vsids puzzles/sudoku_1.cnf -v

Runs the DPLL solver with the VSIDS heuristic on sudoku_1.cnf with verbose output.

3.3. CDCL.py

Description

CDCL.py implements the CDCL algorithm, an advanced SAT solver with conflict analysis and clause learning. It supports the VSIDS heuristic.

Usage

python CDCL.py [VSIDS] <filename> [-v]

	•	VSIDS (optional): Variable selection heuristic.
	•	vsids or True: Use the VSIDS heuristic.
	•	non-vsids or False: Do not use the VSIDS heuristic.
	•	both: Run the solver twice, with and without VSIDS.
	•	Default: False (non-VSIDS).
	•	<filename> (required): Path to the DIMACS CNF file.
	•	-v or --verbose (optional): Enable verbose output.

Example

python CDCL.py both puzzles/sudoku_1.cnf

Runs the CDCL solver on sudoku_1.cnf both with and without the VSIDS heuristic.

3.4. SAT.py

Description

SAT.py provides a unified command-line interface to run the DPLL and CDCL solvers with different configurations on a specified SAT problem.

Usage

python SAT.py -Sn <dimacs_file>

	•	-Sn (required): Solver and heuristic configuration, where n is:
	•	1: Basic DPLL without VSIDS.
	•	2: DPLL with VSIDS heuristic.
	•	3: Basic CDCL without VSIDS.
	•	4: CDCL with VSIDS heuristic.
	•	<dimacs_file> (required): Path to the DIMACS CNF file.

Configuration Options

	•	-S1: Basic DPLL without VSIDS.
	•	-S2: DPLL with VSIDS heuristic.
	•	-S3: Basic CDCL without VSIDS.
	•	-S4: CDCL with VSIDS heuristic.

Example

python SAT.py -S4 puzzles/sudoku_1.cnf

Runs the CDCL solver with the VSIDS heuristic on sudoku_1.cnf.

3.5. experiment.py

Description

experiment.py automates the execution of both DPLL and CDCL solvers across multiple Sudoku puzzles, comparing performance with and without the VSIDS heuristic.

Usage

python experiment.py [directory]

	•	[directory] (optional): Path to the directory containing Sudoku CNF files named sudoku_*.cnf.
	•	Default: puzzles/

Example

python experiment.py puzzles/

Runs experiments on all Sudoku puzzles in the puzzles/ directory.

4. Usage Instructions

4.1. Generating CNF Files from Sudoku Puzzles

	1.	Prepare an input file: Create a text file containing Sudoku puzzles, each puzzle on a new line. Each line should represent a single puzzle, and the puzzle size must be one of the supported sizes (4x4, 9x9, or 16x16). Use the following conventions:
	•	Empty cells are denoted by a period (.).
	•	Characters for cells can include:
	•	1-9 for 4x4 and 9x9 puzzles.
	•	A-F (case-insensitive) for 16x16 puzzles, in addition to 1-9.
	2.	Run the Sudoku CNF Generator:

python sudoku_cnf_generator.py <input_filename>

Replace <input_filename> with your file’s name.

	3.	Output: CNF files are generated and saved in an output directory named after the input file (without the extension). Each CNF file corresponds to a single puzzle from the input file.
	4.	Notes:
	•	Ensure that the rule files (sudoku-rules-4x4.txt, sudoku-rules-9x9.txt, sudoku-rules-16x16.txt) are in the same directory as the script.
	•	Only puzzles of size 4x4, 9x9, and 16x16 are supported.
	•	Invalid or unsupported puzzles will be skipped with an appropriate error message.

Example

Given an input file sudoku_puzzles.txt:

python sudoku_cnf_generator.py sudoku_puzzles.txt

This command will:
	1.	Create an output directory named sudoku_puzzles.
	2.	Generate CNF files for each Sudoku puzzle in sudoku_puzzles.txt, saving them in the output directory.
	3.	Append relevant rules from the appropriate rules file based on each puzzle’s size.

4.2. Running DPLL.py

	1.	Prepare a CNF file: Use the Sudoku CNF Generator or provide your own DIMACS CNF file.
	2.	Run the solver:

python DPLL.py [VSIDS] <filename> [-v]

Provide the appropriate VSIDS option and the path to your CNF file.

	3.	Review the output: The solver displays whether a solution was found, runtime, and conflicts.

Example

python DPLL.py vsids puzzles/sudoku_1.cnf -v

Runs the DPLL solver with the VSIDS heuristic on sudoku_1.cnf with verbose output.

4.3. Running CDCL.py

	1.	Prepare a CNF file: Use the Sudoku CNF Generator or provide your own DIMACS CNF file.
	2.	Run the solver:

python CDCL.py [VSIDS] <filename> [-v]

Provide the appropriate VSIDS option and the path to your CNF file.

	3.	Review the output: The solver displays whether a solution was found, runtime, conflicts, and variable assignments if a solution was found.

Example

python CDCL.py both puzzles/sudoku_1.cnf

Runs the CDCL solver on sudoku_1.cnf both with and without the VSIDS heuristic.

4.4. Running SAT.py

	1.	Prepare a CNF file: Use the Sudoku CNF Generator or provide your own DIMACS CNF file.
	2.	Run the solver:

python SAT.py -Sn <dimacs_file>

Replace n with the desired configuration number (1-4) and <dimacs_file> with your CNF file.

	3.	Review the output: The script displays the runtime and number of conflicts.

Configuration Options

	•	-S1: Basic DPLL without VSIDS.
	•	-S2: DPLL with VSIDS heuristic.
	•	-S3: Basic CDCL without VSIDS.
	•	-S4: CDCL with VSIDS heuristic.

Example

python SAT.py -S3 puzzles/sudoku_1.cnf

Runs the basic CDCL solver without the VSIDS heuristic on sudoku_1.cnf.

4.5. Running experiment.py

	1.	Prepare the puzzles directory: Ensure it contains Sudoku CNF files named sudoku_*.cnf.
	2.	Run the experiment script:

python experiment.py [directory]

Replace [directory] with your directory path if not using the default.

	3.	Review the results: The script outputs performance statistics for each solver configuration.

5. Relation Between the Code Files

	•	Sudoku CNF Generator creates CNF files from Sudoku puzzles for the solvers.
	•	DPLL.py and CDCL.py are independent SAT solvers.
	•	SAT.py serves as a wrapper to run the solvers with specified configurations.
	•	experiment.py automates running the solvers across multiple instances for performance comparison.

6. How the Experiment Works

The experiment.py script performs the following steps:
	1.	Load Sudoku Puzzles: Finds all sudoku_*.cnf files in the specified directory.
	2.	Run Solvers: For each puzzle, it runs:
	•	DPLL without VSIDS.
	•	DPLL with VSIDS.
	•	CDCL without VSIDS.
	•	CDCL with VSIDS.
	3.	Collect Data: Records runtime and conflicts for each solver configuration.
	4.	Compute Statistics: Calculates mean, maximum, and minimum values for runtime and conflicts.
	5.	Display Results: Outputs aggregated statistics for comparative analysis.

7. License

This project is open-source and available under the MIT License.

Feel free to modify the scripts or use them for educational purposes. If you encounter any issues or have suggestions, please consider contributing or opening an issue.