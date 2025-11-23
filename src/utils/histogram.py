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
