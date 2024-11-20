import os
import sys

class SudokuCNFGenerator:
    def __init__(self, sudoku_string, rules_filename):
        self.sudoku_string = sudoku_string
        self.rules_filename = rules_filename
        self.clauses = []
        self.N = int(len(sudoku_string) ** 0.5)
        if self.N * self.N != len(sudoku_string):
            raise ValueError("Invalid Sudoku puzzle size.")
        self.char_to_num = self.create_char_to_number_mapping()

    def create_char_to_number_mapping(self):
        """
        Creates a mapping from characters in the Sudoku puzzle to numbers from 1 to N.
        """
        mapping = {}
        mapping['.'] = 0  # Empty cell
        for i in range(1, self.N + 1):
            if i <= 9:
                mapping[str(i)] = i
            else:
                # For N > 9, use letters starting from 'A' for 10, 'B' for 11, etc.
                mapping[chr(ord('A') + i - 10)] = i
        return mapping

    def generate_cnf(self):
        """
        Generates CNF clauses from the given Sudoku string.
        Each 'given' is translated into the format row_column_number and stored as a CNF clause.
        """
        for i in range(self.N):
            for j in range(self.N):
                value = self.sudoku_string[i * self.N + j]
                if value != '.':
                    if value not in self.char_to_num:
                        print(f"Error: Invalid character '{value}' at position ({i + 1}, {j + 1})")
                        continue
                    row = i + 1
                    column = j + 1
                    number = self.char_to_num[value]

                    # Construct the variable in the row_column_number format
                    variable_number = f"{row}{column}{number}"

                    # Append this as a clause
                    self.clauses.append(f"{variable_number} 0")

    def save_cnf_with_rules(self, filename):
        """
        Saves the CNF clauses to a file in DIMACS format, including additional rules.
        """
        variables = self.N * self.N * self.N
        total_clauses = len(self.clauses) + self.get_rules_clause_count()
        with open(filename, 'w') as cnf_file:
            # Write the header specifying the number of variables and clauses
            cnf_file.write(f"p cnf {variables} {total_clauses}\n")

            # Write the generated clauses for the current Sudoku
            for clause in self.clauses:
                cnf_file.write(clause + "\n")

            # Append the common rules from the rules file
            with open(self.rules_filename, 'r') as rules_file:
                for line in rules_file:
                    line = line.strip()
                    if not line or line.startswith('c') or line.startswith('p'):
                        continue
                    cnf_file.write(line + "\n")

    def get_rules_clause_count(self):
        """
        Counts the number of clauses in the rules file, excluding comments and headers.
        """
        count = 0
        with open(self.rules_filename, 'r') as rules_file:
            for line in rules_file:
                line = line.strip()
                if not line or line.startswith('c') or line.startswith('p'):
                    continue
                count += 1
        return count

def create_output_directory(filename):
    """
    Creates an output directory named after the source file (without extension).
    """
    output_dir = os.path.splitext(os.path.basename(filename))[0]
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    return output_dir

def process_sudoku_file(filename, rules_filename, output_dir):
    """
    Reads a file containing Sudoku strings, generates CNF for each line, and saves them to individual files.
    """
    try:
        with open(filename, 'r') as file:
            for line_number, line in enumerate(file, start=1):
                sudoku_string = line.strip()
                if not sudoku_string:
                    continue  # Skip empty lines
                N = int(len(sudoku_string) ** 0.5)
                if N * N != len(sudoku_string):
                    print(f"Error: Line {line_number} in the file does not contain a valid Sudoku puzzle. Expected a perfect square grid, but got length {len(sudoku_string)}.")
                    continue

                # Generate CNF for each Sudoku
                generator = SudokuCNFGenerator(sudoku_string, rules_filename)
                generator.generate_cnf()

                # Save each solution in a separate CNF file, with general rules appended
                output_filename = os.path.join(output_dir, f"sudoku_{line_number}.cnf")
                generator.save_cnf_with_rules(output_filename)
                print(f"CNF saved to {output_filename}")

    except FileNotFoundError:
        print(f"Error: The file '{filename}' was not found.")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python sudoku_cnf_generator.py <input_filename> <rules_filename>")
        sys.exit(1)

    input_filename = sys.argv[1]
    rules_filename = sys.argv[2]

    # Create the output directory named after the source file
    output_dir = create_output_directory(input_filename)

    # Process the Sudoku file and generate CNF files
    process_sudoku_file(input_filename, rules_filename, output_dir)