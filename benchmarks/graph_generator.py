import os
import matplotlib.pyplot as plt
import json
import numpy as np

def generate_graphs(all_stats, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    for solver, folder_data in all_stats.items():
        folders = list(folder_data.keys())
        avg_times = []
        timeouts = []

        for folder in folders:
            stats = folder_data[folder]
            times = stats['times']
            avg_time = sum(times)/len(times) if times else 0
            avg_times.append(avg_time)
            timeouts.append(stats['timeout'])

        x = range(len(folders))
        width = 0.35

        fig, ax1 = plt.subplots(figsize=(10, 6))
        ax1.bar(x, avg_times, width=width, label='Avg Solve Time (s)', color='skyblue')
        ax2 = ax1.twinx()
        ax2.plot(x, timeouts, label='Timeouts', color='red', marker='o')

        ax1.set_xlabel('CNF Folders')
        ax1.set_ylabel('Time (s)', color='skyblue')
        ax2.set_ylabel('Timeouts', color='red')
        ax1.set_title(f'{solver.upper()} — Performance by Folder')
        ax1.set_xticks(x)
        ax1.set_xticklabels(folders, rotation=45, ha='right')

        fig.tight_layout()
        fig.legend(loc='upper right')
        plt.savefig(os.path.join(output_dir, f"{solver}.png"))
        plt.close()
