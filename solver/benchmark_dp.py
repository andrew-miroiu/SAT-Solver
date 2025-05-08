import os
import time
import multiprocessing
from sat_reader import read_dimacs_cnf
from sat_dp import dp_algorithm
import json

def run_dp_with_timeout(clauses, timeout=60):
    with multiprocessing.get_context("spawn").Pool(1) as pool:
        result = pool.apply_async(dp_algorithm, (clauses,))
        try:
            is_sat = result.get(timeout=timeout)
            return is_sat, None
        except multiprocessing.TimeoutError:
            pool.terminate()
            pool.join()
            return None, 'timeout'

def benchmark_dp_folder(folder_path, timeout=60):
    print(f"\n🚀 Benchmarking DP on folder: {os.path.basename(folder_path)}\n")
    total_time = 0
    timed_out = 0
    file_count = 0

    for filename in os.listdir(folder_path):
        if not filename.endswith('.cnf'):
            continue

        file_path = os.path.join(folder_path, filename)
        print(f"🧩 File: {filename}")
        try:
            _, _, raw_clauses = read_dimacs_cnf(file_path)
            clauses = [frozenset(clause) for clause in raw_clauses]

            start_time = time.time()
            result, status = run_dp_with_timeout(clauses, timeout=timeout)
            elapsed = time.time() - start_time

            if status == 'timeout':
                print(f"⏱️ Timeout (> {timeout}s)")
                timed_out += 1
            else:
                print(f"✅ Result: {'SAT' if result else 'UNSAT'} — {elapsed:.2f}s")
                total_time += elapsed

            file_count += 1

        except Exception as e:
            print(f"❌ Error: {e}")

    print("\n📊 Benchmark Summary:")
    print(f"  → Files processed: {file_count}")
    print(f"  → Timeouts: {timed_out}")
    print(f"  → Total time (non-timeout): {total_time:.2f}s")
    print(f"  → Avg time per file: {total_time/(file_count - timed_out):.2f}s" if (file_count - timed_out) else "  → All files timed out.")

    stats = {
        "files_processed": file_count,
        "timeouts": timed_out,
        "avg_time": total_time / (file_count - timed_out) if (file_count - timed_out) else 0
    }
    with open("benchmark_stats_dp.json", "w") as f:
        json.dump(stats, f)

if __name__ == "__main__":
    folder_path = r'C:\Users\andre\SAT-Solver\cnfs\test'
    benchmark_dp_folder(folder_path)
