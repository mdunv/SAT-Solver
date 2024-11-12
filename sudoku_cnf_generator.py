import os


class SimplifiedSudokuCNFGenerator:
    def __init__(self, sudoku_string, rules_filename):
        self.sudoku_string = sudoku_string
        self.rules_filename = rules_filename
        self.clauses = []

    def generate_cnf(self):
        """
        Generates CNF clauses from the given Sudoku string.
        The string should have 81 characters, with '.' representing empty cells and digits representing given values.
        """
        for i in range(9):
            for j in range(9):
                value = self.sudoku_string[i * 9 + j]
                if value != '.':
                    # Convert the row, column, and value to a CNF literal in the format row column value
                    # Rows and columns are indexed from 1 to 9
                    row = i + 1
                    column = j + 1
                    number = int(value)
                    # Append the literal in the required format
                    self.clauses.append(f"{row}{column}{number} 0")

    def save_cnf_with_rules(self, filename):
        """
        Saves the CNF clauses to a file in DIMACS format, including additional rules.
        """
        with open(filename, 'w') as cnf_file:
            # Write the header specifying the number of clauses (including rules)
            cnf_file.write(f"p cnf 729 {len(self.clauses) + self.get_rules_clause_count()}\n")

            # Write the generated clauses for the current Sudoku
            for clause in self.clauses:
                cnf_file.write(clause + "\n")

            # Append the common rules from the rules file
            with open(self.rules_filename, 'r') as rules_file:
                for line in rules_file:
                    cnf_file.write(line)

    def get_rules_clause_count(self):
        """
        Counts the number of clauses in the rules file.
        """
        count = 0
        with open(self.rules_filename, 'r') as rules_file:
            for _ in rules_file:
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
                if len(sudoku_string) != 81:
                    print(f"Error: Line {line_number} in the file does not contain exactly 81 characters.")
                    continue

                # Generate CNF for each Sudoku
                generator = SimplifiedSudokuCNFGenerator(sudoku_string, rules_filename)
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
    # import sys
    #
    # if len(sys.argv) != 2:
    #     print("Usage: python simplified_sudoku_cnf_generator.py <filename>")
    #     sys.exit(1)

    filename = "top91.sdk.txt"
    rules_filename = 'sudoku-rules-9x9.txt'

    # Create the output directory named after the source file
    output_dir = create_output_directory(filename)

    # Process the Sudoku file and generate CNF files
    process_sudoku_file(filename, rules_filename, output_dir)
