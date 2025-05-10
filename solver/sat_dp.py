import os
import functools
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor, TimeoutError
from sat_reader import read_dimacs_cnf  # make sure this is working
import multiprocessing

print = functools.partial(print, flush=True)  # always flush output

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
                    async_result = pool.apply_async(dp_algorithm, (clauses,))
                    try:
                        is_sat = async_result.get(timeout=timeout)
                        print(f"{filename}: {'SAT' if is_sat else 'UNSAT'}")
                    except multiprocessing.TimeoutError:
                        pool.terminate()  # Force-stop the process
                        pool.join()
                        print(f"{filename}: Timeout (> {timeout}s) — Skipping")

            except Exception as e:
                print(f"{filename}: Error — {e}")



def unit_clause_elimination(clauses, assignment, debug=False):
    changed = True
    while changed:
        changed = False
        unit_clauses = [c for c in clauses if len(c) == 1]
        if not unit_clauses:
            break
        if debug:
            print(f"  📌 Unit clauses: {unit_clauses}")
        for unit in unit_clauses:
            literal = next(iter(unit))
            assignment.add(literal)
            new_clauses = []
            for clause in clauses:
                if literal in clause:
                    continue
                if -literal in clause:
                    new_clause = clause - {-literal}
                    if not new_clause:
                        return None, None
                    new_clauses.append(new_clause)
                else:
                    new_clauses.append(clause)
            clauses = new_clauses
            changed = True
            if debug:
                print(f"    → Assigned {literal}, remaining {len(clauses)} clauses")
    return clauses, assignment


def pure_literal_elimination(clauses, assignment, debug=False):
    counts = defaultdict(int)
    for clause in clauses:
        for lit in clause:
            counts[lit] += 1
    pure_literals = {lit for lit in counts if -lit not in counts}
    if debug and pure_literals:
        print(f"  ✨ Pure literals: {pure_literals}")
    if not pure_literals:
        return clauses, assignment
    assignment.update(pure_literals)
    new_clauses = [c for c in clauses if c.isdisjoint(pure_literals)]
    if debug:
        print(f"    → Eliminated clauses with {pure_literals}, remaining {len(new_clauses)} clauses")
    return new_clauses, assignment


def resolve_clauses(clauses, variable, debug=False):
    if debug:
        print(f"  🔀 Resolving on variable: {variable}")
    pos_clauses = [c for c in clauses if variable in c]
    neg_clauses = [c for c in clauses if -variable in c]
    new_clauses = set()
    for c1 in pos_clauses:
        for c2 in neg_clauses:
            resolvent = (c1 | c2) - {variable, -variable}
            if any(-lit in resolvent for lit in resolvent):
                continue
            new_clauses.add(frozenset(resolvent))
    remaining = [c for c in clauses if variable not in c and -variable not in c]
    remaining.extend(new_clauses)
    if debug:
        print(f"    → Generated {len(new_clauses)} resolvents, {len(remaining)} total clauses now")
    return remaining


def dp_algorithm(clauses, assignment=None, debug=False):
    if assignment is None:
        assignment = set()
    step = 0
    while True:
        step += 1
        if debug:
            print(f"\n🧩 Step {step} — {len(clauses)} clauses")
        clauses, assignment = unit_clause_elimination(clauses, assignment, debug)
        if clauses is None:
            if debug:
                print("❌ Conflict during unit propagation")
            return False
        if not clauses:
            if debug:
                print("✅ All clauses satisfied")
            return True
        clauses, assignment = pure_literal_elimination(clauses, assignment, debug)
        if not clauses:
            if debug:
                print("✅ All clauses satisfied after pure literal elimination")
            return True
        literals = {abs(lit) for clause in clauses for lit in clause}
        if not literals:
            return True
        var = next(iter(literals))
        clauses = resolve_clauses(clauses, var, debug)
        if any(len(c) == 0 for c in clauses):
            if debug:
                print("❌ Empty clause found after resolution")
            return False


def process_file(file_path):
    print(f"\n🔍 Starting to process file: {os.path.basename(file_path)}")
    num_vars, num_clauses, raw_clauses = read_dimacs_cnf(file_path)
    clauses = [frozenset(clause) for clause in raw_clauses]
    return dp_algorithm(clauses, debug=True)


if __name__ == "__main__":
    directory_path = '/Users/andrewmiroiu/Desktop/SAT solver/cnfs/UUF50.218.1000'
    #directory_path = '/Users/andrewmiroiu/Desktop/SAT solver/cnfs/UF75.325.100'
    #directory_path = 'C:\\Users\\andre\\SAT-Solver\\cnfs\\test'
    process_all_files(directory_path)

#python3 '/Users/andrewmiroiu/Desktop/SAT solver/solver/sat_dp.py'
