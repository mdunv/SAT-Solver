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
import matplotlib.pyplot as plt
import numpy as np



def plot_bar_runtime(runtimes1, runtimes2, runtimes3):
    # Names for the methods
    methods = ["Basic DPLL", "DPLL VSIDS", "Basic CDCL", "CDCL VSIDS"]
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']

    # Calculate means and standard deviations for runtimes
    runtime1_means = [np.mean(runtimes1[method]) for method in methods]

    # Calculate means and standard deviations for runtimes
    runtime2_means = [np.mean(runtimes2[method]) for method in methods]

    # Calculate means and standard deviations for runtimes
    runtime3_means = [np.mean(runtimes3[method]) for method in methods]

    # Set up the figure and axes for plotting
    fig, axes = plt.subplots(1, 3, figsize=(12, 6))
    # plt.ylabel("Average runtime")

    # Plot 4x4
    for i, method in enumerate(methods):
        axes[0].bar(method, runtime1_means[i], capsize=5,
                    color=colors[i], edgecolor='black', label=method)
    axes[0].set_title("Runtimes of solving 4x4 sudokus")
    axes[0].set_ylabel("Average Runtime")
    axes[0].set_xlabel("Method")
    axes[0].legend()
    axes[0].set_ylim(bottom=0)

    # Plot 9x9
    for i, method in enumerate(methods):
        axes[1].bar(method, runtime2_means[i], capsize=5,
                    color=colors[i], edgecolor='black', label=method)
    axes[1].set_title("Runtimes of solving 9x9 sudokus")
    axes[1].set_xlabel("Method")
    axes[1].legend()
    axes[1].set_ylim(bottom=0)

   # Plot 16x16
    for i, method in enumerate(methods):
        axes[2].bar(method, runtime3_means[i], capsize=5,
                    color=colors[i], edgecolor='black', label=method)
    axes[2].set_title("Runtimes of solving 16x16 sudokus")
    axes[2].set_xlabel("Method")
    axes[2].legend()
    axes[2].set_ylim(bottom=0)

    # Adjust layout for a clean display
    plt.tight_layout()
    plt.show()


def plot_bar_conflict(conflict1, conflict2):
    # Names for the methods
    methods = ["Basic DPLL", "DPLL VSIDS", "Basic CDCL", "CDCL VSIDS"]
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']

    # Calculate means and standard deviations for runtimes
    conflict1_means = [np.mean(conflict1[method]) for method in methods]
    conflict1_stdevs = [np.std(conflict1[method]) for method in methods]

    # Calculate means and standard deviations for runtimes
    conflict2_means = [np.mean(conflict2[method]) for method in methods]
    conflict2_stdevs = [np.std(conflict2[method]) for method in methods]

    # Set up the figure and axes for plotting
    fig, axes = plt.subplots(1, 2, figsize=(12, 6))

    # Plot 9x9
    for i, method in enumerate(methods):
        axes[0].bar(method, conflict1_means[i], capsize=5,
                    color=colors[i], edgecolor='black', label=method)
    axes[0].set_title("Conflicts in 9x9 sudokus")
    axes[0].set_ylabel("Average Conflict Count")
    axes[0].set_xlabel("Method")
    axes[0].legend()
    axes[0].set_ylim(bottom=0)

    # Plot 16x16
    for i, method in enumerate(methods):
        axes[1].bar(method, conflict2_means[i], capsize=5,
                    color=colors[i], edgecolor='black', label=method)
    axes[1].set_title("Conflicts in 16x16 sudokus")
    axes[1].set_xlabel("Method")
    axes[1].legend()
    axes[1].set_ylim(bottom=0)


def plot_bar_combined_single(runtime, conflict):
    # Names for the methods
    methods = ["Basic DPLL", "DPLL VSIDS", "Basic CDCL", "CDCL VSIDS"]
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']

    # Calculate means and standard deviations for runtimes
    runtime_means = [np.mean(runtime[method]) for method in methods]

    # Runtime
    plt.subplot(1, 2, 1)
    for i, method in enumerate(methods):
        plt.bar(method, runtime_means[i], capsize=5,
                    color=colors[i], edgecolor='black', label=method)
    plt.title("Runtimes of solving hard susokus")
    plt.ylabel("Average runtime")
    plt.xlabel("Method")
    plt.ylim(bottom=0)

    conflict_means = [np.mean(conflict[method]) for method in methods]


    # Conflicts
    plt.subplot(1, 2, 2)
    for i, method in enumerate(methods):
        plt.bar(method, conflict_means[i], capsize=5,
                    color=colors[i], edgecolor='black', label=method)
    plt.title("Conflicts in hard sudokus")
    plt.ylabel("Average Conflict Count")
    plt.xlabel("Method")
    plt.ylim(bottom=0)


    # Adjust layout for a clean display
    plt.tight_layout()
    plt.show()


def run_experiment(directory="top100.sdk/", directory2=None, directory3=None):
    all_runtimes = []
    all_conflicts = []

    directories = [dir for dir in [directory, directory2, directory3] if dir != None]
    for dir in directories:
        print(dir)
        runtimes = {"Basic DPLL" : [], "DPLL VSIDS" : [], "Basic CDCL": [], "CDCL VSIDS" : []}
        conflicts = {"Basic DPLL" : [], "DPLL VSIDS" : [], "Basic CDCL": [], "CDCL VSIDS" : []}

        runtime1, runtime2, runtime3, runtime4 = [], [], [], []
        conflicts1, conflicts2, conflicts3, conflicts4 = [], [], [], []

        sudoku_files = glob.glob(os.path.join(dir, "sudoku_*.cnf"))
        sudoku_files.sort(key=lambda x: int(x.split('_')[1].split('.')[0]))  # Extract the number part and sort
        # sudoku_files = sudoku_files[:200]
        for i, filepath in enumerate(sudoku_files):
            # DPLL without heuristic
            runt, conf = DPLL.run_DPLL(filepath, False)
            runtime1.append(runt)
            runtimes["Basic DPLL"].append(runt)
            conflicts1.append(conf)
            conflicts["Basic DPLL"].append(conf)

            # DPLL + VSIDS
            runt, conf = DPLL.run_DPLL(filepath, True)
            runtime2.append(runt)
            runtimes["DPLL VSIDS"].append(runt)
            conflicts2.append(conf)
            conflicts["DPLL VSIDS"].append(conf)

            # CDCL without heuristic
            _, runt, conf = CDCL.run_CDCL(filepath, False)
            runtime3.append(runt)
            runtimes["Basic CDCL"].append(runt)
            conflicts3.append(conf)
            conflicts["Basic CDCL"].append(conf)

            # CDCL + VSIDS
            _, runt, conf = CDCL.run_CDCL(filepath, True)
            runtime4.append(runt)
            runtimes["CDCL VSIDS"].append(runt)
            conflicts4.append(conf)
            conflicts["CDCL VSIDS"].append(conf)

        all_runtimes.append(runtimes)
        all_conflicts.append(conflicts)


        print("\nDPLL without heuristics:")
        print("Mean runtime:", np.mean(runtime1), "\nStdDev:", np.std(runtime1), "\nMax runtime:", np.max(runtime1), "\nMin runtime:", np.min(runtime1))
        print("\nMean conflicts:", np.mean(conflicts1), "\nStdDev:", np.std(conflicts1), "\nMax conflicts:", np.max(conflicts1), "\nMin conflicts:", np.min(conflicts1))

        print("\n\nDPLL with VSIDS:")
        print("Mean runtime:", np.mean(runtime2), "\nStdDev:", np.std(runtime2), "\nMax runtime:", np.max(runtime2), "\nMin runtime:", np.min(runtime2))
        print("\nMean conflicts:", np.mean(conflicts2), "\nStdDev:", np.std(conflicts2), "\nMax conflicts:", np.max(conflicts2), "\nMin conflicts:", np.min(conflicts2))

        print("\n\nCDCL without heuristics:")
        print("Mean runtime:", np.mean(runtime3), "\nStdDev:", np.std(runtime3), "\nMax runtime:", np.max(runtime3), "\nMin runtime:", np.min(runtime3))
        print("\nMean conflicts:", np.mean(conflicts3), "\nStdDev:", np.std(conflicts3), "\nMax conflicts:", np.max(conflicts3), "\nMin conflicts:", np.min(conflicts3))

        print("\n\nCDCL with VSIDS:")
        print("Mean runtime:", np.mean(runtime4), "\nStdDev:", np.std(runtime4), "\nMax runtime:", np.max(runtime4), "\nMin runtime:", np.min(runtime4))
        print("\nMean conflicts:", np.mean(conflicts4), "\nStdDev:", np.std(conflicts4), "\nMax conflicts:", np.max(conflicts4), "\nMin conflicts:", np.min(conflicts4))
        print("\n")


    if len(directories) == 3:
        # For all 3 given directories, make a plot with the runtimes and a plot if the amount of conflicts
        plot_bar_runtime(all_runtimes[0], all_runtimes[1], all_runtimes[2])
        plot_bar_conflict(all_conflicts[1], all_conflicts[2])
    elif len(directories) == 1:
        # For the given directory plot the runtime and conflicts side by side.
        plot_bar_combined_single(all_runtimes[0], all_conflicts[0])


if __name__ == "__main__":
    if len(sys.argv) < 2:
        run_experiment()
    elif len(sys.argv) < 3:
        run_experiment(sys.argv[1])
    else:
        run_experiment(sys.argv[1], sys.argv[2], sys.argv[3])

