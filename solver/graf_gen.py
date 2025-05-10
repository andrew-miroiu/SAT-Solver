import json
import matplotlib.pyplot as plt

# Paths to your JSON files
dpll_path = 'benchmark_all_results.json'
resolution_path = 'benchmark_resolution_results.json'
dp_path = 'benchmark_dp_results.json'

# Penalty value for total timeouts
TIMEOUT_PENALTY = 5.0  # or whatever you want to reflect a "big" timeout

def load_json(path):
    with open(path) as f:
        return json.load(f)

def extract_data(json_data):
    x = sorted([int(k) for k in json_data.keys()])
    y = []
    for k in x:
        entry = json_data[str(k)]
        if entry["timeouts"] == entry["files_processed"]:
            y.append(TIMEOUT_PENALTY)
        else:
            y.append(entry["avg_time"])
    return x, y

# Load JSON data
dpll_data = load_json(dpll_path)
resolution_data = load_json(resolution_path)
dp_data = load_json(dp_path)

# Extract data points
x_dpll, y_dpll = extract_data(dpll_data)
x_res, y_res = extract_data(resolution_data)
x_dp, y_dp = extract_data(dp_data)

# Plotting
plt.plot(x_dpll, y_dpll, color='green', label='DPLL')
plt.plot(x_res, y_res, color='red', label='Resolution')
plt.plot(x_dp, y_dp, color='blue', label='DP')

# Labels, title, legend
plt.xlabel('V')
plt.ylabel('T')
plt.title('Solver Performance Comparison')
plt.legend()

# Save the figure
plt.savefig('solver_performance.png')

# Optional: show it too
# plt.show()
