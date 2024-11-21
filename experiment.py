"""""
Usage: python experiment.py <directory>
where:
    directory: directory containing sudoku's of form sudoku_*.cnf,
               default is: 'top100.sdk/'
"""""

import glob
import sys
import os
import numpy as np

import DPLL_VSIDS as DPLL
import CDCL_VSIDS as CDCL

def run_experiment(directory="top100.sdk/"):
    sudoku_files = glob.glob(os.path.join(directory, "sudoku_*.cnf"))
    sudoku_files.sort(key=lambda x: int(x.split('_')[1].split('.')[0]))  # Extract the number part and sort

    runtime1, runtime2, runtime3, runtime4 = [], [], [], []
    conflicts1, conflicts2, conflicts3, conflicts4 = [], [], [], []

    for filepath in sudoku_files:
        # DPLL without heuristic
        runt, conf = DPLL.run_DPLL(filepath, False)
        runtime1.append(runt)
        conflicts1.append(conf)

        # DPLL + VSIDS
        runt, conf = DPLL.run_DPLL(filepath, True)
        runtime2.append(runt)
        conflicts2.append(conf)

        # CDCL without heuristic
        _, runt, conf = CDCL.run_CDCL(filepath, False)
        runtime3.append(runt)
        conflicts3.append(conf)

        # CDCL + VSIDS
        _, runt, conf = CDCL.run_CDCL(filepath, True)
        runtime4.append(runt)
        conflicts4.append(conf)

    print("\n\nDPLL without heuristics:")
    print("Mean runtime:", np.mean(runtime1), "\nMax runtime:", np.max(runtime1), "\nMin runtime:", np.min(runtime1))
    print("\nMean conflicts:", np.mean(conflicts1), "\nMax conflicts:", np.max(conflicts1), "\nMin conflicts:", np.min(conflicts1))

    print("\n\nDPLL with VSIDS:")
    print("Mean runtime:", np.mean(runtime2), "\nMax runtime:", np.max(runtime2), "\nMin runtime:", np.min(runtime2))
    print("\nMean conflicts:", np.mean(conflicts2), "\nMax conflicts:", np.max(conflicts2), "\nMin conflicts:", np.min(conflicts2))

    print("\n\nCDCL without heuristics:")
    print("Mean runtime:", np.mean(runtime3), "\nMax runtime:", np.max(runtime3), "\nMin runtime:", np.min(runtime3))
    print("\nMean conflicts:", np.mean(conflicts3), "\nMax conflicts:", np.max(conflicts3), "\nMin conflicts:", np.min(conflicts3))

    print("\n\nCDCL with VSIDS:")
    print("Mean runtime:", np.mean(runtime4), "\nMax runtime:", np.max(runtime4), "\nMin runtime:", np.min(runtime4))
    print("\nMean conflicts:", np.mean(conflicts4), "\nMax conflicts:", np.max(conflicts4), "\nMin conflicts:", np.min(conflicts4))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        run_experiment()
    else:
        run_experiment(sys.argv[1])

    # implementation = sys.argv[1]
    # if len(implementation) != 3:
    #     print("Usage: python SAT.py -Sn")

