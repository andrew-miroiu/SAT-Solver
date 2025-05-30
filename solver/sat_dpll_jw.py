from sat_reader import read_dimacs_cnf
import os
import math
from collections import defaultdict
import multiprocessing
from itertools import combinations


def process_all_files(directory_path, timeout=60):
    for filename in os.listdir(directory_path):
        if filename.endswith(".cnf"):
            file_path = os.path.join(directory_path, filename)
            print(f"Processing file: {filename}")
            
            try:
                num_vars, num_clauses, raw_clauses = read_dimacs_cnf(file_path)
                clauses = {frozenset(clause) for clause in raw_clauses}

                # Spawn a separate process (not just a thread pool)
                with multiprocessing.get_context("spawn").Pool(1) as pool:
                    async_result = pool.apply_async(dpll_jw, (clauses,))
                    try:
                        is_sat = async_result.get(timeout=timeout)
                        print(f"{filename}: {'SAT' if is_sat else 'UNSAT'}")
                    except multiprocessing.TimeoutError:
                        pool.terminate()  # Force-stop the process
                        pool.join()
                        print(f"{filename}: Timeout (> {timeout}s) — Skipping")

            except Exception as e:
                print(f"{filename}: Error — {e}")


def unit_propagate(clauses, assignment):
    changed = True
    while changed:
        changed = False
        unit_clauses = [c for c in clauses if len(c) == 1]
        for unit in unit_clauses:
            literal = next(iter(unit))
            assignment.add(literal)
            new_clauses = []
            for clause in clauses:
                if literal in clause:
                    continue
                if -literal in clause:
                    new_clause = set(clause)
                    new_clause.discard(-literal)
                    if not new_clause:
                        return None, None
                    new_clauses.append(new_clause)
                else:
                    new_clauses.append(set(clause))
            clauses = new_clauses
            changed = True
    return clauses, assignment


def pure_literal_elimination(clauses, assignment):
    all_literals = set(lit for clause in clauses for lit in clause)
    pure_literals = {lit for lit in all_literals if -lit not in all_literals}

    if not pure_literals:
        return clauses, assignment

    assignment |= pure_literals
    new_clauses = [clause for clause in clauses if not clause & pure_literals]

    return new_clauses, assignment


def choose_literal_jw(clauses):
    scores = defaultdict(float)
    for clause in clauses:
        weight = 2 ** (-len(clause))
        for literal in clause:
            scores[literal] += weight

    if not scores:
        return None
    return max(scores, key=scores.get)


def dpll_jw(clauses, assignment=None):
    if assignment is None:
        assignment = set()

    clauses = [set(clause) for clause in clauses]

    clauses, assignment = unit_propagate(clauses, assignment)
    if clauses is None:
        return False
    if not clauses:
        return True

    clauses, assignment = pure_literal_elimination(clauses, assignment)
    if not clauses:
        return True

    literal = choose_literal_jw(clauses)
    if literal is None:
        return False

    # Try assigning literal True
    new_clauses = []
    for clause in clauses:
        if literal in clause:
            continue
        new_clause = set(clause)
        new_clause.discard(-literal)
        if not new_clause:
            continue
        new_clauses.append(new_clause)
    if dpll_jw(new_clauses, assignment | {literal}):
        return True

    # Try assigning literal False
    new_clauses = []
    for clause in clauses:
        if -literal in clause:
            continue
        new_clause = set(clause)
        new_clause.discard(literal)
        if not new_clause:
            continue
        new_clauses.append(new_clause)
    return dpll_jw(new_clauses, assignment | {-literal})


if __name__ == "__main__":
    #directory_path = '/Users/andrewmiroiu/Desktop/SAT solver/UUF50.218.1000'
    directory_path = 'C:\\Users\\andre\\SAT-Solver\\cnfs\\50-250\\uf100-430'
    process_all_files(directory_path)
