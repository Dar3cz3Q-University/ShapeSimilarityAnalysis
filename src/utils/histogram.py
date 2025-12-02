import cv2
import matplotlib.pyplot as plt
import os
from config.constants import ANALYZE_DIR

def plot_histogram(image, title, filename):
    plt.figure(figsize=(10, 5))

    if len(image.shape) == 3:
        colors = ('b', 'g', 'r')
        color_names = ('Blue', 'Green', 'Red')

        for i, (color, name) in enumerate(zip(colors, color_names)):
            hist = cv2.calcHist([image], [i], None, [256], [0, 256])
            hist = hist / hist.sum()
            plt.plot(hist, color=color, linewidth=2, label=name)

        plt.xlim([0, 256])
        plt.xlabel('Pixel value')
        plt.ylabel('Normalized frequency')
        plt.title(title)
        plt.legend()
        plt.grid(True, alpha=0.3)
    else:
        hist = cv2.calcHist([image], [0], None, [256], [0, 256])
        hist = hist / hist.sum()

        plt.plot(hist, color='black', linewidth=2)
        plt.xlim([0, 256])
        plt.xlabel('Pixel value')
        plt.ylabel('Normalized frequency')
        plt.title(title)
        plt.grid(True, alpha=0.3)

    plt.savefig(os.path.join(ANALYZE_DIR, filename), dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved histogram: {filename}")

def plot_ratio_histogram(shape_info, groups, output_dir):
    ratios = [s['ratio'] for s in shape_info]

    plt.figure(figsize=(12, 6))
    plt.hist(ratios, bins=20, color='steelblue', edgecolor='black', alpha=0.7)

    colors = ['red', 'green', 'blue', 'orange', 'purple', 'cyan', 'magenta', 'lime', 'pink', 'brown']

    for group_idx, group in enumerate(groups):
        group_ratios = [s['ratio'] for s in group]
        min_ratio = min(group_ratios)
        max_ratio = max(group_ratios)
        color = colors[group_idx % len(colors)]

        plt.axvline(min_ratio, color=color, linestyle='--', linewidth=2, label=f'Group {group_idx+1}')
        plt.axvline(max_ratio, color=color, linestyle='--', linewidth=2)

    plt.xlabel('P²/A Ratio', fontsize=12)
    plt.ylabel('Count', fontsize=12)
    plt.title('Distribution of Shape Ratios with Group Boundaries', fontsize=14)
    plt.legend()
    plt.grid(axis='y', alpha=0.3)
    plt.savefig(os.path.join(output_dir, 'ratio_histogram.png'), dpi=150)
    print(f"Saved ratio histogram: ratio_histogram.png")
    plt.close()
