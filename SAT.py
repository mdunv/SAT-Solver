"""""
Usage: python SAT.py -Sn dimacs_file
where:
    n=1: Basic DPLL
    n=2: DPLL + VSIDS heuristic
    n=3: Basic CDCL
    n=4: CDCL + VSIDS heuristic

    dimacs_file: A dimacs encoded SAT problem
"""""
import sys

import DPLL
import CDCL


def run_solver(filename, heuristic):
    if heuristic == 1: # DPLL
        runtime, conflicts = DPLL.run_DPLL(filename, False)
    elif heuristic == 2: # DPLL + VSIDS
        runtime, conflicts = DPLL.run_DPLL(filename, True)
    elif heuristic == 3: # CDCL
        _, runtime, conflicts = CDCL.run_CDCL(filename, False)
    elif heuristic == 4: # CDCL + VSIDS
        _, runtime, conflicts = CDCL.run_CDCL(filename, True)
    else:
        print("No correct heuristic selected:", heuristic)

    print_metrics = True
    if print_metrics:
        print("Runtime:", runtime)
        print("Conflicts:", conflicts)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python SAT.py -Sn <filename>")
        sys.exit(1)

    implementation = sys.argv[1]
    if len(implementation) != 3:
        print("Usage: python SAT.py -Sn <filename>")

    run_solver(sys.argv[2], int(implementation[2]))
