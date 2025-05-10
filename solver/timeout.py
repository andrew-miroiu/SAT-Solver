import json
import matplotlib.pyplot as plt

# Paths to benchmark files
dpll_path = 'benchmark_all_results.json'
jw_path = 'benchmark_jw.json'
mf_path = 'benchmark_mf.json'

def load_json(path):
    with open(path) as f:
        return json.load(f)

def extract_timeout_percentage(data):
    x = sorted([int(k) for k in data.keys()])
    y = []
    for k in x:
        item = data[str(k)]
        processed = item["files_processed"]
        timeouts = item["timeouts"]
        percent = (timeouts / processed) * 100 if processed else 0
        y.append(percent)
    return x, y

# Load the data
dpll_data = load_json(dpll_path)
jw_data = load_json(jw_path)
mf_data = load_json(mf_path)

# Extract (x = vars, y = timeout %)
x_dpll, y_dpll = extract_timeout_percentage(dpll_data)
x_jw, y_jw = extract_timeout_percentage(jw_data)
x_mf, y_mf = extract_timeout_percentage(mf_data)

# Plot
plt.figure(figsize=(10, 6))
plt.plot(x_dpll, y_dpll, 's-', label="DPLL", color='green')
plt.plot(x_jw, y_jw, 's-', label="DPLL-JW", color='red')
plt.plot(x_mf, y_mf, 's-', label="DPLL-MF", color='blue')

plt.grid(True)
plt.xlabel("Number of Variables")
plt.ylabel("Timeout Percentage (%)")
plt.title("Timeout Rate per Solver")
plt.legend()
plt.tight_layout()
plt.savefig("timeout_rate_comparison.png")
plt.show()
