import os
from itertools import combinations
from concurrent.futures import ProcessPoolExecutor, TimeoutError
from sat_reader import read_dimacs_cnf
import multiprocessing

def process_all_files(directory_path, timeout=10):
    for filename in os.listdir(directory_path):
        if filename.endswith(".cnf"):
            file_path = os.path.join(directory_path, filename)
            print(f"Processing file: {filename}")
            
            try:
                num_vars, num_clauses, raw_clauses = read_dimacs_cnf(file_path)
                clauses = {frozenset(clause) for clause in raw_clauses}

                # Spawn a separate process (not just a thread pool)
                with multiprocessing.get_context("spawn").Pool(1) as pool:
                    async_result = pool.apply_async(resolution_algorithm, (clauses,))
                    try:
                        is_sat = async_result.get(timeout=timeout)
                        print(f"{filename}: {'SAT' if is_sat else 'UNSAT'}")
                    except multiprocessing.TimeoutError:
                        pool.terminate()  # Force-stop the process
                        pool.join()
                        print(f"{filename}: Timeout (> {timeout}s) — Skipping")

            except Exception as e:
                print(f"{filename}: Error — {e}")

def resolve(ci, cj):
    resolvents = []
    for lit in ci:
        if -lit in cj:
            new_clause = (ci | cj) - {lit, -lit}
            if any(-x in new_clause for x in new_clause):
                continue  # Tautology
            resolvents.append(frozenset(new_clause))
    return resolvents

def resolution_algorithm(clauses):
    clauses = set(clauses)
    while True:
        new_resolvents = set()
        for ci, cj in combinations(clauses, 2):
            if any(lit in ci and -lit in cj for lit in ci):
                resolvents = resolve(ci, cj)
                for r in resolvents:
                    if not r:
                        return False  # Empty clause → UNSAT
                    if r not in clauses and r not in new_resolvents:
                        new_resolvents.add(r)
        if not new_resolvents:
            return True  # No new resolvents → SAT
        clauses |= new_resolvents

if __name__ == "__main__":
    directory_path = 'C:\\Users\\andre\\SAT-Solver\\cnfs\\uf20-91'
    #directory_path = '/Users/andrewmiroiu/Desktop/SAT solver/UUF50.218.1000'
    process_all_files(directory_path, timeout=10)
