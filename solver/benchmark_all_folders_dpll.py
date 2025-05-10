import os
import time
import multiprocessing
import json
import re
from sat_reader import read_dimacs_cnf
from sat_dpll import dpll

def run_dpll_with_timeout(clauses, timeout=10):
    """Runs DPLL on clauses with a timeout in seconds."""
    with multiprocessing.get_context("spawn").Pool(1) as pool:
        result = pool.apply_async(dpll, (clauses,))
        try:
            is_sat = result.get(timeout=timeout)
            return is_sat, None
        except multiprocessing.TimeoutError:
            pool.terminate()
            pool.join()
            return None, 'timeout'

def benchmark_folder(folder_path, timeout=10, max_files=None):
    """
    Benchmarks up to `max_files` .cnf files in `folder_path`.
    If max_files is None, benchmarks all files.
    Returns a dict with files_processed, timeouts, avg_time.
    """
    total_time = 0
    timed_out = 0
    file_count = 0

    # Collect CNF files and optionally limit
    cnf_files = [f for f in os.listdir(folder_path) if f.endswith('.cnf')]
    cnf_files.sort()
    if max_files:
        cnf_files = cnf_files[:max_files]

    for filename in cnf_files:
        print(f"🔍 Processing file: {filename}")
        file_path = os.path.join(folder_path, filename)
        try:
            _, _, raw_clauses = read_dimacs_cnf(file_path)
            clauses = [frozenset(clause) for clause in raw_clauses]

            start_time = time.time()
            _, status = run_dpll_with_timeout(clauses, timeout=timeout)
            elapsed = time.time() - start_time

            if status == 'timeout':
                timed_out += 1
            else:
                total_time += elapsed

            file_count += 1

        except Exception as e:
            print(f"⚠️ Skipped due to error: {filename} — {e}")
            continue

    avg_time = total_time / (file_count - timed_out) if (file_count - timed_out) else 0
    return {
        "files_processed": file_count,
        "timeouts": timed_out,
        "avg_time": avg_time
    }

def benchmark_all_folders(base_path, timeout=20, max_files_per_folder=20):
    """
    Benchmarks each sub-folder of base_path, taking at most
    `max_files_per_folder` CNF files from each.
    Saves aggregated results to 'benchmark_all_results.json'.
    """
    results = {}
    for folder in os.listdir(base_path):
        folder_path = os.path.join(base_path, folder)
        if not os.path.isdir(folder_path):
            continue

        print(f"\n⏳ Benchmarking folder: {folder}")
        stats = benchmark_folder(folder_path, timeout, max_files=max_files_per_folder)

        match = re.search(r'\d+', folder)
        if match:
            var_count = int(match.group())
            results[var_count] = stats
        else:
            print(f"⚠️ Could not parse variable count from '{folder}'")

    with open("benchmark_all_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print("\n✅ All benchmark results saved to benchmark_all_results.json")

if __name__ == "__main__":
    # Adjust these parameters as needed
    base_path = '/Users/andrewmiroiu/Desktop/SAT solver/cnfs/realtest'
    timeout_seconds = 10
    max_files_per_folder = 10  # e.g., set to 20 to limit per-folder files

    benchmark_all_folders(base_path, timeout=timeout_seconds, max_files_per_folder=max_files_per_folder)
