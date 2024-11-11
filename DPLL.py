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


def find_truth(literal, truth_value):
    """
    "From a literal (negated or not), and an assigned truth value,
    find the resulting truth value
    """
    return truth_value if literal > 0 else not truth_value


def update_clauses(clauses, new_lit, truth_value):
    updated_clauses = []

    for clause in clauses:
        clause_is_true = False
        new_clause = set()

        for literal in clause:
            if abs(literal) == new_lit:
                if find_truth(literal, truth_value): # If the literal makes the clause true, mark the clause as true
                    clause_is_true = True
                    break
            else:
                new_clause.add(literal)

        if not clause_is_true: # Only add clauses that are not yet true
            updated_clauses.append(new_clause)


    return updated_clauses


def simplify(pa, clauses):
    "Apply the tautology, pure literal and unit rules to remove unnecessary entries"
    # Tautology rule
    for clause in clauses:
        for variable in clause:
            if -variable in clause:
                clause.remove(variable)
                # If the tautology is the only left in the clause, just remove one, so the unit clause rule will handle the rest
                if len(clause) > 1: # else just remove both
                    clause.remove(-variable)

    # Pure literals
    pure_literals = set()
    clause_mapping = create_clause_mapping(clauses)
    for variable in clause_mapping:
        if variable*-1 not in clause_mapping: # check if literal is pure
            pure_literals.add(variable)

    for literal in pure_literals:
        if literal > 0:
            pa[abs(literal)] = True
            clauses = update_clauses(clauses, abs(literal), True)
        else:
            pa[abs(literal)] = False
            clauses = update_clauses(clauses, abs(literal), False)

    # Unit clause rule
    while True:
        unit_literals = {next(iter(clause)) for clause in clauses if len(clause) == 1}
        if len(unit_literals) == 0:
            break

        for literal in unit_literals:
            if literal > 0:
                pa[abs(literal)] = True
                clauses = update_clauses(clauses, abs(literal), True)
            else:
                pa[abs(literal)] = False
                clauses = update_clauses(clauses, abs(literal), False)


    return pa, clauses


def DPLL(pa, clauses):
    "DPLL is used recursively, making use of backtracking to explore whole search space"
    global solution

    # Perform simplification rules
    pa, clauses = simplify(pa, clauses)

    # Check satisfiability
    if len(clauses) == 0: # Satisfiable (sudoku is done)
        solution = pa.copy()
        return True
    if any(len(clause) == 0 for clause in clauses): # Unsatisfiable
        return False


    # Select a new literal randomly to recurse/backtrack with
    available_literals = {abs(lit) for clause in clauses for lit in clause}
    new_literal = random.choice(list(available_literals))
    pa[new_literal] = False # For now assign false
    if (DPLL(pa, update_clauses(clauses, new_literal, False))):
        return True

    pa[new_literal] = True # False didn't work so backtrack for true
    return DPLL(pa, update_clauses(clauses, new_literal, True))


def run_DPLL(filename):
    clauses = parse_dimacs(filename)

    pa = {}
    satisfiability = DPLL(pa, clauses)
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
    start_time = time.time()
    run_DPLL(sys.argv[1])
    end_time = time.time()
    print("Runtime:", f"{end_time - start_time}s")

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







