import os
from .stats_collector import run_solver_on_folder
from .graph_generator import generate_graphs


CNF_ROOT = 'cnfs'
SOLVERS = {
    'dp': 'solver.sat_dp.dp_algorithm',
    'dpll': 'solver.sat_dpll.dpll',
    'resolution': 'solver.sat_resolution.resolution_algorithm',
}

RESULTS_PATH = 'results/benchmark_stats.json'

def main():
    all_stats = {}

    for solver_name, solver_path in SOLVERS.items():
        print(f"\n🔍 Benchmarking {solver_name.upper()}...")
        solver_stats = {}
        for folder_name in os.listdir(CNF_ROOT):
            folder_path = os.path.join(CNF_ROOT, folder_name)
            if not os.path.isdir(folder_path):
                continue
            print(f"\n📁 Folder: {folder_name}")
            stats = run_solver_on_folder(solver_path, folder_path)
            solver_stats[folder_name] = stats
        all_stats[solver_name] = solver_stats

    # Save and generate graphs
    generate_graphs(all_stats, output_dir="results/graphs")

if __name__ == "__main__":
    main()
