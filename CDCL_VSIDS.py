import random
import sys
import time
import os

def parse_dimacs(filename):
    """
    Parse a DIMACs file containing an encoded sudoku, returning clauses:
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

def resolve_clauses(clause1, clause2, literal):
    """
    Resolve two clauses on the given literal.
    """
    return (clause1 | clause2) - {literal, -literal}

def conflict_analysis(pa, current_level, decision_levels, antecedents, conflict_clause, assign_conflicts, activity_scores):
    """
    Perform conflict analysis to produce a learned clause and update activity scores.
    """
    print(f"\nStarting conflict analysis at level {current_level} with conflict clause: {conflict_clause}")
    learned_clause = set(conflict_clause)  # Start with the conflict clause

    while True:
        literals_in_curr_lvl = [lit for lit in learned_clause if decision_levels.get(abs(lit), -1) == current_level and abs(lit) in antecedents]
        if not literals_in_curr_lvl:
            break

        lit = literals_in_curr_lvl.pop()
        assign_conflicts[abs(lit)] += 1  # Update conflict counts
        antecedent_clause = antecedents[abs(lit)]
        print(f"Resolving on literal {lit} with antecedent clause {antecedent_clause}")
        learned_clause = resolve_clauses(learned_clause, antecedent_clause, lit)
        print(f"New learned clause: {learned_clause}")

    # Update activity scores
    for lit in learned_clause:
        activity_scores[abs(lit)] += 1
        print(f"Incremented activity score of variable {abs(lit)} to {activity_scores[abs(lit)]}")

    # Determine the backtrack level
    backtrack_levels = [decision_levels.get(abs(lit), 0) for lit in learned_clause if abs(lit) in decision_levels and decision_levels[abs(lit)] != current_level]
    backtrack_level = max(backtrack_levels) if backtrack_levels else 0
    print(f"Backtrack level determined to be {backtrack_level}")
    return learned_clause, backtrack_level

def clause_sat(pa, clause):
    """
    Check if the clause is satisfied under the current partial assignment.
    """
    for literal in clause:
        if abs(literal) in pa:
            if (literal > 0 and pa[abs(literal)]) or (literal < 0 and not pa[abs(literal)]):
                return True
    return False

def unit_propagation(pa, clauses, decision_levels, antecedents, assign_conflicts, current_level):
    """
    Perform unit propagation and return a conflicting clause if a conflict occurs.
    """
    while True:
        found_unit_clause = False

        for clause in clauses:
            if clause_sat(pa, clause):  # Ignore if already satisfied
                continue

            unassigned_literals = [lit for lit in clause if abs(lit) not in pa]

            if len(unassigned_literals) == 1:  # Unit clause found
                unit_literal = unassigned_literals[0]
                pa[abs(unit_literal)] = unit_literal > 0
                decision_levels[abs(unit_literal)] = current_level
                antecedents[abs(unit_literal)] = clause  # Add clause of origin as antecedent
                found_unit_clause = True
                print(f"Unit propagation: Assigned {unit_literal} at level {current_level} due to clause {clause}")

            elif len(unassigned_literals) == 0:  # Conflict detected
                print(f"Conflict detected during unit propagation at level {current_level} in clause {clause}")
                for literal in clause:
                    assign_conflicts[abs(literal)] += 1  # Update conflict counts
                return clause

        if not found_unit_clause:
            break

    return None

def pick_new_literal(pa, clauses, activity_scores, VSIDS):
    """
    Pick the next variable to assign using VSIDS if enabled.
    """
    unassigned_variables = {abs(literal) for clause in clauses for literal in clause if abs(literal) not in pa}

    if not unassigned_variables:
        print("No unassigned variables left.")
        return None

    if VSIDS:
        best_var = max(unassigned_variables, key=lambda var: activity_scores.get(var, 0))
        print(f"Picking variable {best_var} with highest activity score {activity_scores.get(best_var, 0)}")
        return best_var
    else:
        for clause in clauses:
            for literal in clause:
                if abs(literal) not in pa:
                    print(f"Picking variable {abs(literal)} (default heuristic)")
                    return abs(literal)
    return None

def decay_activity_scores(activity_scores, decay_factor):
    """
    Decay the activity scores of all variables.
    """
    for var in activity_scores:
        activity_scores[var] *= decay_factor
    print(f"Activity scores after decay: {activity_scores}")

def CDCL(clauses, VSIDS):
    # Metrics
    conflicts = 0

    # Initialize variables
    decision_levels = {}
    decision_variable_assignments = {}  # Holds assigned truth values for decision variables
    pa = {}  # Partial assignment
    antecedents = {}  # Antecedent clauses for unit propagated literals
    assign_conflicts = {}
    decision_level = 0

    # Initialize activity scores and decay factor
    activity_scores = {}
    decay_factor = 0.95

    # Initialize activity scores and conflict counts for all variables
    for clause in clauses:
        for l in clause:
            activity_scores.setdefault(abs(l), 0)
            assign_conflicts.setdefault(abs(l), 0)

    conflict = unit_propagation(pa, clauses, decision_levels, antecedents, assign_conflicts, decision_level)
    if conflict:  # Unsatisfiable during initial unit propagation
        print("Unsatisfiable during initial unit propagation")
        return False, conflicts

    while not all(clause_sat(pa, clause) for clause in clauses):
        new_lit = pick_new_literal(pa, clauses, activity_scores, VSIDS)
        if new_lit is None:
            print("No unassigned literals left, but not all clauses are satisfied")
            return False, conflicts
        decision_level += 1

        # Assign False by default
        pa[new_lit] = False
        decision_levels[new_lit] = decision_level
        decision_variable_assignments[new_lit] = False
        print(f"\nDecision level {decision_level}: Assigning variable {new_lit} to False")

        conflict_clause = unit_propagation(pa, clauses, decision_levels, antecedents, assign_conflicts, decision_level)
        while conflict_clause:
            conflicts += 1
            print(f"Conflict detected at decision level {decision_level}. Conflict clause: {conflict_clause}")

            learned_clause, backtrack_level = conflict_analysis(pa, decision_level, decision_levels, antecedents, conflict_clause, assign_conflicts, activity_scores)
            print(f"Learned clause: {learned_clause}")
            print(f"Backtracking to level {backtrack_level}")

            if backtrack_level < 0:
                print("Not satisfiable after conflict analysis")
                return False, conflicts

            clauses.append(learned_clause)  # Add the learned clause
            decay_activity_scores(activity_scores, decay_factor)

            # Backtrack
            decision_level = backtrack_level
            # Remove assignments at levels higher than backtrack_level
            vars_to_remove = [var for var in pa if decision_levels.get(var, -1) > backtrack_level]
            for var in vars_to_remove:
                del pa[var]
                if var in antecedents:
                    del antecedents[var]
                if var in decision_levels:
                    del decision_levels[var]
                if var in decision_variable_assignments:
                    del decision_variable_assignments[var]
                print(f"Backtracked variable {var}")

            conflict_clause = unit_propagation(pa, clauses, decision_levels, antecedents, assign_conflicts, decision_level)
            if conflict_clause:
                print(f"Conflict detected during unit propagation after backtracking at level {decision_level}. Conflict clause: {conflict_clause}")

    print("\nSatisfiable assignment found")
    return pa, conflicts

def run_CDCL(filename, VSIDS):
    clauses = parse_dimacs(filename)

    start_time = time.time()
    pa, conflicts = CDCL(clauses, VSIDS)
    end_time = time.time()

    runtime = end_time - start_time

    if pa:
        print("\nCDCL Solution found:", filename)
        print("Total runtime:", runtime)
        print("Total conflicts:", conflicts)
    else:
        print("Did not find a solution")
        return False

    # Write the solution to an output file
    base_filename, _ = os.path.splitext(filename)
    output_filename = base_filename + '.out'
    with open(output_filename, "w") as f:
        for literal, value in pa.items():
            dimacs_literal = str(literal) if value else f"-{literal}"
            f.write(dimacs_literal + " 0\n")

    # Optional: Print the Sudoku grid representation if applicable
    max_value = max(abs(literal) for literal in pa.keys())
    n = 9  # For standard Sudoku puzzles
    sudoku_grid = [['.' for _ in range(n)] for _ in range(n)]

    # Populate the Sudoku grid with positive literals
    for literal, value in pa.items():
        if value:  # Only consider positive literals (True values)
            # Parse row, column, and digit from the literal key
            row = (literal // 100) - 1
            col = ((literal % 100) // 10) - 1
            digit = (literal % 10)

            # Place the digit in the corresponding Sudoku cell
            sudoku_grid[row][col] = str(digit)

    # Print the Sudoku grid
    print("\nSudoku Grid Representation:")
    for row in sudoku_grid:
        print(" ".join(row))

    return pa, runtime, conflicts

if __name__ == "__main__":
    # Default filename if no argument is provided
    filename = "top91.sdk/sudoku_4.cnf"

    # Check if a filename is provided via command line
    if len(sys.argv) > 1:
        filename = sys.argv[1]

    # Check if the file exists
    if not os.path.exists(filename):
        print(f"File not found: {filename}. Please ensure the file exists at the specified path.")
        sys.exit(1)

    num_trials = 1  # Number of times to run the solver for each mode

    print(f"\nTesting {filename} with CDCL solver:\n")

    # Run CDCL with and without VSIDS
    print("Running CDCL without VSIDS:")
    for i in range(num_trials):
        solution, runtime, conflicts = run_CDCL(filename, False)
        print(f"  Trial {i + 1}: Solution = {solution}, Runtime = {runtime:.3f}s, Conflicts = {conflicts}")

    print("\nRunning CDCL with VSIDS:")
    for i in range(num_trials):
        solution, runtime, conflicts = run_CDCL(filename, True)
        print(f"  Trial {i + 1}: Solution = {solution}, Runtime = {runtime:.3f}s, Conflicts = {conflicts}")

    print("\nTesting completed.")