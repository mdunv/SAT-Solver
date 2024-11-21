import random
import sys
import time
import os

solution = {}
conflicts = 0
activity_scores = {}

def parse_dimacs(filename):
    """
    Parse a DIMACs file containing a sudoku, returning variables:
    clauses: a list of sets, representing different clauses.
    """
    clauses = []
    with open(filename, 'r') as f:
        for line in f:
            if line.startswith('p') or line.startswith('c') or not line.strip():
                continue
            clause = {int(x) for x in line.strip().split()[:-1]}  # Remove trailing 0
            clauses.append(clause)

    return clauses


def create_clause_mapping(clauses):
    "Create a mapping from literals to all clause numbers they are in."
    cell_mapping = dict(set())
    for clause_index, clause in enumerate(clauses):
        for variable in clause:
            if variable not in cell_mapping:
                cell_mapping[variable] = set()
            cell_mapping[variable].add(clause_index)

    return cell_mapping


def simplify(pa, clauses):
    """
    Apply the pure literal and unit rules to remove unnecessary entries.
    """
    # Unit clause rule
    for clause in clauses:
        if len(clause) == 1:
            unit_lit = next(iter(clause))
            print(f"Unit clause found: {unit_lit}")
            return unit_lit

    # Pure literals rule
    literals = set()
    for clause in clauses:
        literals.update(clause)
    pure_literals = literals - set(-lit for lit in literals)
    if pure_literals:
        pure_lit = next(iter(pure_literals))
        print(f"Pure literal found: {pure_lit}")
        return pure_lit

    return None


def remove_literal(clauses, assigned_lit):
    """
    Remove clauses satisfied by the literal and update remaining clauses.
    Returns updated clauses and a list of conflicting clauses if any clauses become empty.
    """
    updated_clauses = []
    conflicting_clauses = []
    for clause in clauses:
        if assigned_lit in clause:
            continue  # Clause is satisfied
        elif -assigned_lit in clause:
            new_clause = clause - {-assigned_lit}
            if len(new_clause) == 0:
                conflicting_clauses.append(clause)  # Use the original clause
            updated_clauses.append(new_clause)
        else:
            updated_clauses.append(clause)
    return updated_clauses, conflicting_clauses


def pick_new_literal(pa, clauses, VSIDS):
    """
    Pick the next variable to branch on, using VSIDS if enabled.
    """
    unassigned_variables = {abs(literal) for clause in clauses for literal in clause if abs(literal) not in pa}

    if not unassigned_variables:  # Check if there are no unassigned variables left
        print("No unassigned variables left.")
        return None

    if VSIDS:
        chosen = max(unassigned_variables, key=lambda var: activity_scores.get(var, 0))
        print(f"Choosing variable {chosen} with highest activity score {activity_scores.get(chosen, 0)}.")
        return chosen
    else:
        for clause in clauses:
            for literal in clause:
                if abs(literal) not in pa:
                    print(f"Choosing first unassigned variable: {abs(literal)}")
                    return abs(literal)
    return None

def remove_tautologies(clauses):
    new_clauses = []
    for clause in clauses:
        if any(-lit in clause for lit in clause):
            print(f"Removing tautological clause: {clause}")
            continue  # Skip tautological clause
        new_clauses.append(clause)
    return new_clauses

decay_factor = 0.75  # Decay factor to reduce older activity scores

def update_activity_scores(conflicting_clause):
    """
    Increment the activity scores of variables in the conflicting clause
    and apply decay to all scores.
    """
    global activity_scores
    for variable in conflicting_clause:
        activity_scores[abs(variable)] = activity_scores.get(abs(variable), 0) + 1

    # Apply decay to all activity scores
    for var in activity_scores:
        activity_scores[var] *= decay_factor

    print(f"Updated Activity Scores (with decay): {activity_scores}")

def DPLL(pa, clauses, assigned_lit, VSIDS):
    global solution, conflicts

    if assigned_lit is not None:
        updated_clauses, conflicting_clauses = remove_literal(clauses, assigned_lit)
        print(f"Assigned Literal: {assigned_lit}, Updated Clauses: {updated_clauses}")
    else:
        updated_clauses = clauses
        conflicting_clauses = []

    # Check satisfiability
    if len(updated_clauses) == 0:  # Satisfiable
        solution = pa.copy()
        print("Solution found!")
        return True
    if conflicting_clauses:  # Unsatisfiable
        conflicts += 1
        print(f"Conflict encountered! Total conflicts: {conflicts}")
        if VSIDS:
            for conflict_clause in conflicting_clauses:
                update_activity_scores(conflict_clause)
        return False

    # Perform simplification rules
    unit_literal = simplify(pa, updated_clauses)
    if unit_literal:
        pa[abs(unit_literal)] = unit_literal > 0
        print(f"Simplification found unit literal: {unit_literal}")
        return DPLL(pa.copy(), updated_clauses, unit_literal, VSIDS)

    # Select a new literal to recurse/backtrack with
    new_literal = pick_new_literal(pa, updated_clauses, VSIDS)
    if new_literal is None:
        print("No new literal to select. Returning False.")
        return False

    # Try False assignment first
    pa[new_literal] = False
    print(f"Trying literal {new_literal} as False.")
    if DPLL(pa.copy(), updated_clauses, -new_literal, VSIDS):
        return True

    # Backtrack and try True assignment
    pa[new_literal] = True
    print(f"Backtracking and trying literal {new_literal} as True.")
    return DPLL(pa.copy(), updated_clauses, new_literal, VSIDS)

def run_DPLL(filename, VSIDS):
    """
    Run the DPLL algorithm with or without VSIDS on the given DIMACS file.
    """
    global activity_scores, conflicts
    activity_scores = {}  # Reset activity scores
    conflicts = 0  # Reset conflict counter

    clauses = parse_dimacs(filename)

    print(f"Number of clauses before removing tautologies: {len(clauses)}")
    clauses = remove_tautologies(clauses)
    print(f"Number of clauses after removing tautologies: {len(clauses)}")

    start_time = time.time()
    # Tautology rule
    for clause in clauses:
        for variable in clause:
            if -variable in clause:
                clause.remove(variable)
                if len(clause) > 1:
                    clause.remove(-variable)

    pa = {}
    available_literals = list({abs(lit) for clause in clauses for lit in clause})
    for lit in available_literals:
        activity_scores[lit] = 0  # Initialize activity scores

    # Select a new literal to recurse/backtrack with
    new_literal = available_literals[0]

    pa[new_literal] = False  # Assign False initially
    satisfiability = DPLL(pa, clauses, -new_literal, VSIDS)
    if not satisfiability:
        pa[new_literal] = True
        satisfiability = DPLL(pa, clauses, new_literal, VSIDS)

    end_time = time.time()
    runtime = end_time - start_time

    if satisfiability:
        print("DPLL Solution found:", filename)
    else:
        print("Did not find a solution")
        return runtime, conflicts

    base_filename, _ = os.path.splitext(filename)
    filename = base_filename + '.out'
    with open(filename, "w") as f:  # Write the DIMACS output to file
        for literal, value in solution.items():
            dimacs_literal = str(literal) if value else f"-{literal}"
            f.write(dimacs_literal + " 0\n")

    return runtime, conflicts


if __name__ == "__main__":

    # if len(sys.argv) > 1:
    #     runtime, conflicts = run_DPLL(sys.argv[1], False)
    #
    #     print("Runtime:", runtime)
    #     print("Conflicts:", conflicts)
    # else:
    #     print("Add a filename")

    filename = "top91.sdk/sudoku_3.cnf"  # Replace with your file path
    if not os.path.exists(filename):
        print("File not found. Please ensure the file exists at the specified path.")
        exit()

    num_trials = 1  # Number of times to run the solver for each mode

    print(f"\nTesting {filename} with DPLL solver:\n")

    print("Running DPLL without VSIDS:")
    for i in range(num_trials):
        runtime, conflicts = run_DPLL(filename, False)
        print(f"  Trial {i + 1}: Runtime = {runtime:.3f}s, Conflicts = {conflicts}")

    print("\nRunning DPLL with VSIDS:")
    for i in range(num_trials):
        runtime, conflicts = run_DPLL(filename, True)
        print(f"  Trial {i + 1}: Runtime = {runtime:.3f}s, Conflicts = {conflicts}")

    print("\nTesting completed.")