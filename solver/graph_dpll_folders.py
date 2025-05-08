import json
import matplotlib.pyplot as plt
import os
import numpy as np
import sys
import multiprocessing
import time
from sat_reader import read_dimacs_cnf
from sat_dpll import dpll
import json

def plot_multiple_benchmarks(json_path="benchmark_all_results.json", output_path="benchmark_graph.png"):
    if not os.path.exists(json_path):
        print(f"⚠️ File not found: {json_path}")
        return

    with open(json_path, "r") as f:
        data = json.load(f)

    variable_counts = sorted(int(k) for k in data)
    avg_times = [data[str(k)]["avg_time"] for k in variable_counts]

    plt.figure(figsize=(10, 6))
    plt.plot(variable_counts, avg_times, marker='o', linestyle='-', color='blue')
    plt.title("DPLL Solve Time vs. Number of Variables")
    plt.xlabel("Number of Variables")
    plt.ylabel("Average Solve Time (s)")
    plt.grid(True)

    for x, y in zip(variable_counts, avg_times):
        plt.text(x, y, f"{y:.2f}", ha='center', va='bottom')

    plt.tight_layout()
    plt.savefig(output_path)
    print(f"📊 Graph saved to {output_path}")
    plt.show()

if __name__ == "__main__":
    plot_multiple_benchmarks()
