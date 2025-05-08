import json
import matplotlib.pyplot as plt
import os

def plot_benchmark_from_file(json_path="benchmark_stats_dp.json", output_path="benchmark_graph_dp.png"):
    if not os.path.exists(json_path):
        print(f"⚠️ Stats file not found: {json_path}")
        return

    with open(json_path, "r") as f:
        stats = json.load(f)

    files_processed = stats["files_processed"]
    timeouts = stats["timeouts"]
    avg_time = stats["avg_time"]

    labels = ["Files Processed", "Timeouts", "Avg Time per File (s)"]
    values = [files_processed, timeouts, avg_time]
    colors = ["#4CAF50", "#F44336", "#2196F3"]

    plt.figure(figsize=(8, 5))
    bars = plt.bar(labels, values, color=colors)
    plt.title("DPLL Benchmark Results")
    plt.ylabel("Count / Seconds")

    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2., height,
                 f'{height:.2f}' if isinstance(height, float) else f'{int(height)}',
                 ha='center', va='bottom')

    plt.tight_layout()
    plt.savefig(output_path)
    print(f"📈 Graph saved to {output_path}")
    plt.show()

if __name__ == "__main__":
    plot_benchmark_from_file()
