import random
import sys
import time

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


def resolve_clauses(clause1, clause2, literal):
    return (clause1 | clause2) - {literal, -literal}


def conflict_analysis(pa, current_level, decision_levels, antecedents, conflict_clause):
    """
    Simplified conflict analysis using union of conflict and antecedent clauses.
    """
    learned_clause = set(conflict_clause)  # Start with the conflict clause

    while True:
        literals_in_curr_lvl = [lit for lit in learned_clause if decision_levels[abs(lit)] == current_level and abs(lit) in antecedents]
        if len(literals_in_curr_lvl) == 0:
            break
        while len(literals_in_curr_lvl) > 0:
            lit = literals_in_curr_lvl.pop()

            antecedent_clause = antecedents[abs(lit)]
            learned_clause = resolve_clauses(learned_clause, antecedent_clause, lit)

    # Determine the backtrack level
    backtrack_level = max((decision_levels[abs(lit)] for lit in learned_clause if decision_levels[abs(lit)] < current_level), default=-1)

    return learned_clause, backtrack_level


def clause_sat(pa, clause):
    for literal in clause:
        if abs(literal) in pa:
            if (literal > 0 and pa[abs(literal)]) or (literal < 0 and not pa[abs(literal)]):
                return True

    return False


def unit_propogation(pa, clauses, decision_levels, antecedents, conflicts_per_assignment, current_level):
    while True:
        found_unit_clause = False
        for clause in clauses:
            if clause_sat(pa, clause): # Ignore if already satisfied
                continue

            unassigned_literals = [lit for lit in clause if abs(lit) not in pa]
            if len(unassigned_literals) == 1: # Unit literal found
                unit_literal = unassigned_literals[0]
                pa[abs(unit_literal)] = True if unit_literal > 0 else False
                decision_levels[abs(unit_literal)] = current_level
                antecedents[abs(unit_literal)] = clause # Add clause of origin as antecedent
                found_unit_clause = True

            elif len(unassigned_literals) == 0: # Conflict (Fully assigned but none satisfy clause)
                for literal in clause:
                    truth_value = pa[abs(literal)]  # Add to conflicts found
                    conflicts_per_assignment[abs(literal)][truth_value] += 1
                return clause

        if not found_unit_clause:
            break


    return None


def pick_new_literal(pa, clauses):
    for clause in clauses:
        for literal in clause:
            if abs(literal) not in pa:
                return literal
    return None


def pick_truth_value(literal, past_conflicts):
    true_confs, false_confs = past_conflicts[abs(literal)][True], past_conflicts[abs(literal)][False]
    total_conflicts = true_confs + false_confs

    if total_conflicts == 0:
        return random.choices([True, False])[0]
        # return False
    # Calculate probabilities
    p_true = true_confs / total_conflicts
    p_false = false_confs / total_conflicts

    # Choose based on probability
    return random.choices([True, False], weights=[p_true, p_false])[0]


def CDCL(clauses):
    # Metrics
    assignments = 0

    # Initialize variables
    decision_levels = {}
    decision_variable_assignments = {}
    pa = {}
    antecedents = {}
    conflicts_per_assignment = {}
    decision_level = 0

    for clause in clauses:
        for l in clause:
            if l not in conflicts_per_assignment:
                conflicts_per_assignment[abs(l)] = {True : 0, False : 0}

    conflict = unit_propogation(pa, clauses, decision_levels, antecedents, conflicts_per_assignment, decision_level)
    if (conflict): # Unsatisfiable
        return False

    while not all(clause_sat(pa,clause) for clause in clauses):
        new_lit = pick_new_literal(pa, clauses)
        decision_level += 1
        assignments += 1

        pa[abs(new_lit)] = pick_truth_value(new_lit, conflicts_per_assignment)

        # Decide value
        # if new_lit not in decision_variable_assignments:
        #     decision_variable_assignments[abs(new_lit)] = False
        #     pa[abs(new_lit)] = decision_variable_assignments[abs(new_lit)]
        # else:
        #     new_truth = not decision_variable_assignments[abs(new_lit)]
        #     decision_variable_assignments[abs(new_lit)] = new_truth
        #     pa[abs(new_lit)] = new_truth

        decision_levels[abs(new_lit)] = decision_level

        conflict_clause = unit_propogation(pa, clauses, decision_levels, antecedents, conflicts_per_assignment, decision_level)
        while (conflict_clause):
            learned_clause, backtrack_level = conflict_analysis(pa, decision_level, decision_levels, antecedents, conflict_clause)
            # Decay conflicts:
            for l in conflicts_per_assignment:
                conflicts_per_assignment[l][True] *= 0.95  # Decay factor
                conflicts_per_assignment[l][False] *= 0.95
            if backtrack_level < 0:
                print("Not satisfiable")
                return False

            clauses.append(learned_clause)  # Add the learned clause
            decision_level = backtrack_level  # Backtrack
            # Remove assignments at levels higher than backtrack_level
            pa = {var: val for var, val in pa.items() if decision_levels[var] <= backtrack_level}
            antecedents = {var: level for var, level in antecedents.items() if decision_levels[var] <= backtrack_level}
            decision_levels = {var: level for var, level in decision_levels.items() if level <= backtrack_level}

            conflict_clause = unit_propogation(pa, clauses, decision_levels, antecedents, conflicts_per_assignment, decision_level)

    print("End clauses", len(clauses))
    return pa, assignments


def run_CDCL(filename):
    clauses = parse_dimacs(filename)
    print("Start clauses:", len(clauses))

    start_time = time.time()
    pa, assignments = CDCL(clauses)
    end_time = time.time()

    print("Runtime:", f"{end_time - start_time}s")
    print("assignments:", assignments)

    if pa:
        print("Solution found")
    else:
        print("Did not find a solution")
        return False

    filename = filename.split(".")
    filename = f"{filename[0]}.out"
    with open(filename, "w") as f:  # Write the DIMACS output to file
        for literal, value in pa.items():
            dimacs_literal = str(literal) if value else f"-{literal}"
            f.write(dimacs_literal + " 0\n")

    return pa


if len(sys.argv) > 1:
    solution = run_CDCL(sys.argv[1])

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


