import random
import sys
import time

solution = {}

def parse_dimacs(filename):
    """
    Parse a DIMACs file containing a ecnoded sudoku, returning a variables:
    clauses: a list of sets, representing different clauses
    """
    clauses = []
    with open(filename, 'r') as f:
        for line in f:
            if line.startswith('p') or line.startswith('c') or not line:
                continue
            clause = {int(x) for x in line.strip().split()[:-1]}  # Remove trailing 0
            clauses.append(clause)

    return clauses


def create_clause_mapping(clauses):
    "Create a mapping from literals to all clause numbers they are in"
    cell_mapping = dict(set())
    for clause_index, clause in enumerate(clauses):
        for variable in clause:
            if variable not in cell_mapping:
                cell_mapping[variable] = set()

            cell_mapping[variable].add(clause_index)

    return cell_mapping


def simplify(pa, clauses):
    "Apply the pure literal and unit rules to remove unnecessary entries"
    # Unit clause rule
    for clause in clauses:
        if len(clause) == 1:
            return next(iter(clause))

    # Pure literals rule
    clause_mapping = create_clause_mapping(clauses)
    for variable in clause_mapping:
        if variable*-1 not in clause_mapping: # check if literal is pure
            return variable

    return None


def remove_literal(clauses, assigned_lit):
    updated_clauses = []
    for clause in clauses:
        if assigned_lit in clause:
            continue
        elif -assigned_lit in clause:
            # Remove the negation of the assigned literal from this clause
            new_clause = set(clause) - {-assigned_lit}
            updated_clauses.append(new_clause)
        else:
            updated_clauses.append(clause)

    return updated_clauses


def pick_new_literal(pa, clauses):
    for clause in clauses:
        for literal in clause:
            return abs(literal)
    return None


def DPLL(pa, clauses, assigned_lit):
    "DPLL is used recursively, making use of backtracking to explore whole search space"
    global solution

    updated_clauses = remove_literal(clauses, assigned_lit)

    # Check satisfiability
    if len(updated_clauses) == 0: # Satisfiable (sudoku is done)
        solution = pa.copy()
        return True
    if any(len(clause) == 0 for clause in updated_clauses): # Unsatisfiable
        return False

    # Perform simplification rules
    unit_literal = simplify(pa, updated_clauses)
    if unit_literal:
        pa[abs(unit_literal)] = True if unit_literal > 0 else False
        return DPLL(pa, updated_clauses, unit_literal)

    # Select a new literal to recurse/backtrack with
    new_literal = pick_new_literal(pa, updated_clauses)

    pa[new_literal] = False # For now assign false
    if (DPLL(pa, updated_clauses, -new_literal)):
        return True

    pa[new_literal] = True # False didn't work so backtrack for true
    return DPLL(pa, updated_clauses, new_literal)


def run_DPLL(filename):
    clauses = parse_dimacs(filename)

    start_time = time.time()
    # Tautology rule
    for clause in clauses:
        for variable in clause:
            if -variable in clause:
                clause.remove(variable)
                # If the tautology is the only left in the clause, just remove one, so the unit clause rule will handle the rest
                if len(clause) > 1: # else just remove both
                    clause.remove(-variable)

    pa = {}
    # Select a new literal to recurse/backtrack with
    available_literals = list({abs(lit) for clause in clauses for lit in clause})
    new_literal = list(available_literals)[0]

    pa[new_literal] = False  # Assign False initially
    satisfiability = DPLL(pa, clauses, -new_literal)
    if not satisfiability:
        pa[new_literal] = True
        satisfiability = DPLL(pa, clauses, new_literal)

    end_time = time.time()
    print("Runtime:", f"{end_time - start_time}s")

    if satisfiability:
        print("Solution found")
    else:
        print("Did not find a solution")
        return

    filename = filename.split(".")
    filename = f"{filename[0]}.out"
    with open(filename, "w") as f: # Write the DIMACS output to file
        for literal, value in solution.items():
            dimacs_literal = str(literal) if value else f"-{literal}"
            f.write(dimacs_literal + " 0\n")

    return


if len(sys.argv) > 1:
    run_DPLL(sys.argv[1])

    ### Sudoku representation
    max_value = max(abs(literal) for literal in solution.keys())
    # Assuming literals are in the form XYZ, extract the largest component and derive n
    n = max((max_value // 100), (max_value % 100) // 10, max_value % 10)

    sudoku_grid = [['.' for _ in range(n)] for _ in range(n)]

    # Populate the Sudoku grid with positive literals
    for literal, value in solution.items():
        if value:  # Only consider positive literals (True values)
            # Parse row, column, and digit from the literal key
            row = (literal // 100) - 1
            col = ((literal % 100) // 10) - 1
            digit = (literal % 10)

            # Place the digit in the corresponding Sudoku cell
            sudoku_grid[row][col] = str(digit)

    # Print the Sudoku grid
    print("Sudoku Grid Representation:")
    for row in sudoku_grid:
        print(" ".join(row))
else:
    print("Add a filename")







