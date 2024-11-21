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

import DPLL
import CDCL

def run_experiment(directory="top100.sdk/"):
    sudoku_files = glob.glob(os.path.join(directory, "sudoku_*.cnf"))
    sudoku_files.sort(key=lambda x: int(x.split('_')[1].split('.')[0]))  # Extract the number part and sort

    runtime1, runtime2, runtime3, runtime4 = [], [], [], []
    conflicts1, conflicts2, conflicts3, conflicts4 = [], [], [], []

    for filepath in sudoku_files:
        # DPLL without heuristic
        results = DPLL.run_DPLL_mode(filepath, mode="non-vsids")
        runtime1.append(results["non-vsids"]["runtime"])
        conflicts1.append(results["non-vsids"]["conflicts"])

        # DPLL with VSIDS
        results = DPLL.run_DPLL_mode(filepath, mode="vsids")
        runtime2.append(results["vsids"]["runtime"])
        conflicts2.append(results["vsids"]["conflicts"])

        # CDCL without heuristic
        results = CDCL.run_CDCL_mode(filepath, mode="non-vsids")
        runtime3.append(results["non-vsids"]["runtime"])
        conflicts3.append(results["non-vsids"]["conflicts"])

        # CDCL with VSIDS
        results = CDCL.run_CDCL_mode(filepath, mode="vsids")
        runtime4.append(results["vsids"]["runtime"])
        conflicts4.append(results["vsids"]["conflicts"])

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

