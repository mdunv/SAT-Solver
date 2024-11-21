import random
import sys
import time
import os

# Global variables
solution = {}
conflicts = 0
activity_scores = {}
sys.setrecursionlimit(10000)

decay_factor = 0.75  # Decay factor to reduce older activity scores

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

def simplify(pa, clauses, verbose):
    """
    Apply the pure literal and unit rules to remove unnecessary entries.
    """
    # Unit clause rule
    for clause in clauses:
        if len(clause) == 1:
            unit_lit = next(iter(clause))
            if verbose:
                print(f"Unit clause found: {unit_lit}")
            return unit_lit

    # Pure literals rule
    literals = set()
    for clause in clauses:
        literals.update(clause)
    pure_literals = literals - set(-lit for lit in literals)
    if pure_literals:
        pure_lit = next(iter(pure_literals))
        if verbose:
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

def pick_new_literal(pa, clauses, VSIDS, verbose):
    """
    Pick the next variable to branch on, using VSIDS if enabled.
    """
    unassigned_variables = {abs(literal) for clause in clauses for literal in clause if abs(literal) not in pa}

    if not unassigned_variables:  # Check if there are no unassigned variables left
        if verbose:
            print("No unassigned variables left.")
        return None

    if VSIDS:
        chosen = max(unassigned_variables, key=lambda var: activity_scores.get(var, 0))
        if verbose:
            print(f"Choosing variable {chosen} with highest activity score {activity_scores.get(chosen, 0)}.")
        return chosen
    else:
        for clause in clauses:
            for literal in clause:
                if abs(literal) not in pa:
                    if verbose:
                        print(f"Choosing first unassigned variable: {abs(literal)}")
                    return abs(literal)
    return None

def remove_tautologies(clauses, verbose):
    new_clauses = []
    for clause in clauses:
        if any(-lit in clause for lit in clause):
            if verbose:
                print(f"Removing tautological clause: {clause}")
            continue  # Skip tautological clause
        new_clauses.append(clause)
    return new_clauses

def update_activity_scores(conflicting_clause, verbose):
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

    if verbose:
        print(f"Updated Activity Scores (with decay): {activity_scores}")

def DPLL(pa, clauses, assigned_lit, VSIDS, verbose):
    global solution, conflicts

    if assigned_lit is not None:
        updated_clauses, conflicting_clauses = remove_literal(clauses, assigned_lit)
        if verbose:
            print(f"Assigned "
                  f"Literal: {assigned_lit}, Updated Clauses: {updated_clauses}")
    else:
        updated_clauses = clauses
        conflicting_clauses = []

    # Check satisfiability
    if len(updated_clauses) == 0:  # Satisfiable
        solution = pa.copy()
        if verbose:
            print("Solution found!")
        return True
    if conflicting_clauses:  # Unsatisfiable
        conflicts += 1
        if verbose:
            print(f"Conflict encountered! Total conflicts: {conflicts}")
        if VSIDS:
            for conflict_clause in conflicting_clauses:
                update_activity_scores(conflict_clause, verbose)
        return False

    # Perform simplification rules
    unit_literal = simplify(pa, updated_clauses, verbose)
    if unit_literal:
        pa[abs(unit_literal)] = unit_literal > 0
        if verbose:
            print(f"Simplification found unit literal: {unit_literal}")
        return DPLL(pa.copy(), updated_clauses, unit_literal, VSIDS, verbose)

    # Select a new literal to recurse/backtrack with
    new_literal = pick_new_literal(pa, updated_clauses, VSIDS, verbose)
    if new_literal is None:
        if verbose:
            print("No new literal to select. Returning False.")
        return False

    # Try False assignment first
    pa[new_literal] = False
    if verbose:
        print(f"Trying literal {new_literal} as False.")
    if DPLL(pa.copy(), updated_clauses, -new_literal, VSIDS, verbose):
        return True

    # Backtrack and try True assignment
    pa[new_literal] = True
    if verbose:
        print(f"Backtracking and trying literal {new_literal} as True.")
    return DPLL(pa.copy(), updated_clauses, new_literal, VSIDS, verbose)

def run_DPLL(filename, VSIDS, verbose=False):
    """
    Run the DPLL algorithm with or without VSIDS on the given DIMACS file.
    """
    global activity_scores, conflicts, solution
    activity_scores = {}  # Reset activity scores
    conflicts = 0         # Reset conflict counter
    solution = {}         # Reset solution

    clauses = parse_dimacs(filename)

    if verbose:
        print(f"Number of clauses before removing tautologies: {len(clauses)}")
    clauses = remove_tautologies(clauses, verbose)
    if verbose:
        print(f"Number of clauses after removing tautologies: {len(clauses)}")

    start_time = time.time()

    # Tautology rule (not needed as we have remove_tautologies)
    # Initialize partial assignment and activity scores
    pa = {}
    available_literals = list({abs(lit) for clause in clauses for lit in clause})
    for lit in available_literals:
        activity_scores[lit] = 0  # Initialize activity scores

    # Start DPLL algorithm
    satisfiability = DPLL(pa, clauses, None, VSIDS, verbose)

    end_time = time.time()
    runtime = end_time - start_time


    if satisfiability:
        if VSIDS:
            print(f"DPLL with VSIDS has found a solution to: {filename}")
        else:
            print(f"DPLL without VSIDS has found a solution to: {filename}")
        print("Total runtime:", runtime)
        print("Total conflicts:", conflicts)
    else:
        if VSIDS:
            print(f"DPLL with VSIDS could not find a solution for: {filename}")
        else:
            print(f"DPLL without VSIDS could not find a solution for: {filename}")

    # Optionally write solution to file
    # base_filename, _ = os.path.splitext(filename)
    # output_filename = base_filename + '.out'
    # with open(output_filename, "w") as f:
    #     for literal, value in solution.items():
    #         dimacs_literal = str(literal) if value else f"-{literal}"
    #         f.write(dimacs_literal + " 0\n")

    return runtime, conflicts

def run_DPLL_mode(filename, mode="non-vsids", verbose=False):
    """
    Run DPLL in the specified mode: "non-vsids", "vsids", or "both".

    Returns:
        results (dict): A dictionary containing runtime and conflict stats for the specified mode(s).
    """
    results = {}

    if mode == "non-vsids" or mode == "both":
        start = time.time()
        runtime, conflicts = run_DPLL(filename, False, verbose=verbose)
        end = time.time()
        results["non-vsids"] = {"runtime": runtime, "conflicts": conflicts, "total_time": end - start}

    if mode == "vsids" or mode == "both":
        start = time.time()
        runtime, conflicts = run_DPLL(filename, True, verbose=verbose)
        end = time.time()
        results["vsids"] = {"runtime": runtime, "conflicts": conflicts, "total_time": end - start}

    return results

if __name__ == "__main__":
    import argparse

    def interpret_vsids_flag(flag):
        """Interpret VSIDS flag for CLI input."""
        if not flag or flag.lower() in ["false", "non-vsids"]:
            return "non-vsids"
        elif flag.lower() in ["true", "vsids"]:
            return "vsids"
        elif flag.lower() == "both":
            return "both"
        else:
            raise ValueError(f"Invalid VSIDS flag: {flag}. Use 'vsids', 'non-vsids', or 'both'.")

    # Command-line interface
    parser = argparse.ArgumentParser(description="DPLL SAT Solver for Sudoku")
    parser.add_argument("VSIDS", nargs='?', default="False", help="VSIDS heuristic: vsids/True, non-vsids/False, or both")
    parser.add_argument("filename", help="Path to the DIMACS CNF file")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()

    mode = interpret_vsids_flag(args.VSIDS)
    filename = args.filename
    verbose = args.verbose

    print(f"\nTesting {filename} with DPLL solver in {mode} mode:\n")
    results = run_DPLL_mode(filename, mode=mode, verbose=verbose)

    for key, result in results.items():
        print(f"\n{key.capitalize()} Results:")
        print(f"Runtime: {result['runtime']:.3f}s, Conflicts: {result['conflicts']}")

    print("\nTesting completed.")