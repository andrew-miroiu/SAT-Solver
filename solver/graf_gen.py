# ▣ IMPORTS
import json
import matplotlib.pyplot as plt

# ▣ FILE PATHS
dpll_path = 'benchmark_all_results.json'
dpll_jw = 'benchmark_jw.json'
dpll_mf = 'benchmark_mf.json'

# ▣ SETTINGS
TIMEOUT_PENALTY = 60.0  # Penalty (in seconds) for each timeout

# ▣ HELPER FUNCTIONS

def load_json(path):
    """Load a JSON file from the given path."""
    with open(path) as f:
        return json.load(f)

def extract_data(json_data):
    """
    Extracts variable counts, adjusted average times (with timeout penalty), and timeout percentages.
    Returns: x (variables), y (adjusted avg times), to (timeout percentages)
    """
    x = sorted([int(k) for k in json_data.keys()])
    avg_times = []
    timeout_rates = []

    for k in x:
        entry = json_data[str(k)]
        total = entry["files_processed"]
        timeouts = entry["timeouts"]
        solved = total - timeouts
        avg_time = entry["avg_time"]

        # Adjusted average time includes timeout penalty
        adjusted_time = (
            (avg_time * solved + timeouts * TIMEOUT_PENALTY) / total
            if total > 0 else 0
        )
        timeout_rate = (timeouts / total) * 100 if total > 0 else 0

        avg_times.append(adjusted_time)
        timeout_rates.append(timeout_rate)

    return x, avg_times, timeout_rates

# ▣ LOAD & EXTRACT DATA

x_dpll, y_dpll, to_dpll = extract_data(load_json(dpll_path))
x_jw, y_jw, to_jw = extract_data(load_json(dpll_jw))
x_mf, y_mf, to_mf = extract_data(load_json(dpll_mf))

# ▣ PLOTTING

fig, ax1 = plt.subplots(figsize=(10, 6))

# ▣ Plot Adjusted Execution Times (solid lines)
ax1.set_xlabel('Number of Variables (V)')
ax1.set_ylabel('Adjusted Avg Time (T) [s]', color='black')
ax1.plot(x_dpll, y_dpll, 'g-o', label='DPLL Time')
ax1.plot(x_jw, y_jw, 'r-o', label='DPLL-JW Time')
ax1.plot(x_mf, y_mf, 'b-o', label='DPLL-MF Time')
ax1.tick_params(axis='y', labelcolor='black')

# ▣ Plot Timeout Percentages (dashed lines on secondary Y-axis)
ax2 = ax1.twinx()
ax2.set_ylabel('Timeout %', color='gray')
ax2.plot(x_dpll, to_dpll, 'g--s', label='DPLL Timeout %')
ax2.plot(x_jw, to_jw, 'r--s', label='DPLL-JW Timeout %')
ax2.plot(x_mf, to_mf, 'b--s', label='DPLL-MF Timeout %')
ax2.tick_params(axis='y', labelcolor='gray')

# ▣ Gridlines
ax1.grid(True, which='both', linestyle='--', linewidth=0.5, alpha=0.7)

# ▣ Legends and Title
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')

plt.title('Solver Performance Comparison with Timeout Impact')
plt.tight_layout()

# ▣ Save or Show
plt.savefig('solver_performance_with_timeouts.png')
# plt.show()  # Uncomment to display the plot
