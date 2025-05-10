import json
import matplotlib.pyplot as plt

# Paths to your JSON benchmark files
dpll_path = 'benchmark_all_results.json'
jw_path = 'benchmark_jw.json'
mf_path = 'benchmark_mf.json'

def load_json(path):
    with open(path) as f:
        return json.load(f)

def extract_avg_times(data):
    x = sorted([int(k) for k in data.keys()])
    y = []
    for k in x:
        item = data[str(k)]
        processed = item["files_processed"]
        timeouts = item["timeouts"]
        if processed - timeouts > 0:
            y.append(item["avg_time"])
        else:
            y.append(None)  # Skip full timeouts
    return x, y

# Load the data
dpll_data = load_json(dpll_path)
jw_data = load_json(jw_path)
mf_data = load_json(mf_path)

# Extract (x = variables, y = avg time without full timeouts)
x_dpll, y_dpll = extract_avg_times(dpll_data)
x_jw, y_jw = extract_avg_times(jw_data)
x_mf, y_mf = extract_avg_times(mf_data)

# Plot
plt.figure(figsize=(10, 6))
plt.plot(x_dpll, y_dpll, 's-', label="DPLL", color='green')
plt.plot(x_jw, y_jw, 's-', label="DPLL-JW", color='red')
plt.plot(x_mf, y_mf, 's-', label="DPLL-MF", color='blue')

plt.grid(True)
plt.xlabel("Number of Variables")
plt.ylabel("Avg Solve Time (s)")
plt.title("Avg Solve Time (Excluding Timeouts)")
plt.legend()
plt.tight_layout()
plt.savefig("avg_solve_time_comparison.png")
plt.show()
