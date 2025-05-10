import os
from itertools import combinations
import multiprocessing
from sat_reader import read_dimacs_cnf

def process_all_files(directory_path, timeout=60):
    for filename in os.listdir(directory_path):
        if filename.endswith(".cnf"):
            file_path = os.path.join(directory_path, filename)
            print(f"\n📄 Processing file: {filename}")
            
            try:
                num_vars, num_clauses, raw_clauses = read_dimacs_cnf(file_path)
                clauses = {frozenset(clause) for clause in raw_clauses}

                with multiprocessing.get_context("spawn").Pool(1) as pool:
                    async_result = pool.apply_async(resolution_algorithm, (clauses,))
                    try:
                        is_sat = async_result.get(timeout=timeout)
                        print(f"✅ {filename}: {'SAT' if is_sat else 'UNSAT'}")
                    except multiprocessing.TimeoutError:
                        pool.terminate()
                        pool.join()
                        print(f"⏰ {filename}: Timeout (> {timeout}s) — Skipping")

            except Exception as e:
                print(f"❌ {filename}: Error — {e}")

def resolve(ci, cj):
    resolvents = []
    for lit in ci:
        if -lit in cj:
            new_clause = (ci | cj) - {lit, -lit}
            if any(-x in new_clause for x in new_clause):
                continue
            resolvents.append(frozenset(new_clause))
    return resolvents

def resolution_algorithm(clauses):
    clauses = set(clauses)
    iteration = 1

    while True:
        print(f"\n🔄 Iteration {iteration}: {len(clauses)} clauses")
        new_resolvents = set()
        for ci, cj in combinations(clauses, 2):
            if any(lit in ci and -lit in cj for lit in ci):
                resolvents = resolve(ci, cj)
                for r in resolvents:
                    if not r:
                        return False
                    if r not in clauses and r not in new_resolvents:
                        new_resolvents.add(r)
        if not new_resolvents:
            return True
        clauses |= new_resolvents
        iteration += 1

if __name__ == "__main__":
    directory_path = '/Users/andrewmiroiu/Desktop/SAT solver/cnfs/cnf_10vars_examples'
    process_all_files(directory_path, timeout=60)
