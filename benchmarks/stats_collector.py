import os
import time
import importlib
import multiprocessing
from collections import defaultdict
from itertools import combinations

def run_solver_on_folder(solver_path, folder_path, timeout=10):
    module_name, func_name = solver_path.rsplit('.', 1)
    solver_module = importlib.import_module(module_name)
    solver_func = getattr(solver_module, func_name)

    stats = {'solved': 0, 'timeout': 0, 'total': 0, 'times': []}

    for filename in os.listdir(folder_path):
        if not filename.endswith('.cnf'):
            continue
        file_path = os.path.join(folder_path, filename)
        start = time.time()
        try:
            with multiprocessing.get_context("spawn").Pool(1) as pool:
                result = pool.apply_async(solver_func, (load_clauses(file_path),))
                is_sat = result.get(timeout=timeout)
            elapsed = time.time() - start
            stats['solved'] += 1
            stats['times'].append(elapsed)
        except multiprocessing.TimeoutError:
            stats['timeout'] += 1
        stats['total'] += 1

    return stats

def load_clauses(file_path):
    from solver.sat_reader import read_dimacs_cnf
    _, _, raw_clauses = read_dimacs_cnf(file_path)
    return [frozenset(clause) for clause in raw_clauses]
