import os
import time
import json
import multiprocessing
from sat_reader import read_dimacs_cnf
from sat_dpll import dpll
from sat_dp import dp_algorithm
from sat_resolution import resolution_algorithm

ALGORITHMS = {
    'DPLL': dpll,
    'DP': dp_algorithm,
    'Resolution': resolution_algorithm
}

def run_solver_with_timeout(solver_func, clauses, timeout=10):
    with multiprocessing.get_context("spawn").Pool(1) as pool:
        result = pool.apply_async(solver_func, (clauses,))
        try:
            output = result.get(timeout=timeout)
            return output, None
        except multiprocessing.TimeoutError:
            pool.terminate()
            pool.join()
            return None, 'timeout'

def benchmark_solver(solver_name, solver_func, folder_path, timeout=10):
    print(f"\n🚀 Benchmarking {solver_name} on folder: {os.path.basename(folder_path)}\n")
    results = []

    for filename in os.listdir(folder_path):
        if not filename.endswith('.cnf'):
            continue

        file_path = os.path.join(folder_path, filename)
        print(f"🧩 File: {filename}")

        try:
            num_vars, _, raw_clauses = read_dimacs_cnf(file_path)
            clauses = [frozenset(clause) for clause in raw_clauses]

            start_time = time.time()
            result, status = run_solver_with_timeout(solver_func, clauses, timeout=timeout)
            elapsed = time.time() - start_time

            result_entry = {
                "file": filename,
                "vars": num_vars,
                "time": None,
                "status": "timeout" if status == 'timeout' else "done",
                "result": None
            }

            if status == 'timeout':
                print(f"⏱️ Timeout (> {timeout}s)")
            else:
                print(f"✅ Result: {'SAT' if result else 'UNSAT'} — {elapsed:.2f}s")
                result_entry["time"] = round(elapsed, 4)
                result_entry["result"] = "SAT" if result else "UNSAT"

            results.append(result_entry)

        except Exception as e:
            print(f"❌ Error on {filename}: {e}")

    return results

def main():
    folder_path = r'C:\Users\andre\SAT-Solver\cnfs\realtest'
    timeout = 60  # seconds
    all_results = {}

    for name, func in ALGORITHMS.items():
        all_results[name] = benchmark_solver(name, func, folder_path, timeout)

    with open("benchmark_results.json", "w") as f:
        json.dump(all_results, f, indent=2)

    print("\n✅ All benchmark results saved to benchmark_results.json")

if __name__ == "__main__":
    main()
