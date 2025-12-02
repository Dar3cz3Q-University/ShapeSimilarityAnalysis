import cv2
import numpy as np
import matplotlib.pyplot as plt
import os
from utils.histogram import plot_histogram, plot_ratio_histogram
from config.constants import ANALYZE_DIR

class ShapeDetector:
    def __init__(self, image_path):
        self.original_image = cv2.imread(image_path)
        if self.original_image is None:
            raise ValueError(f"Cannot load image: {image_path}")

        self.image = self.original_image.copy()
        self.height, self.width = self.image.shape[:2]
        self.output_dir = ANALYZE_DIR

    def preprocess_image(self):
        gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (9, 9), 0)
        edges = cv2.Canny(blurred, 50, 120)

        kernel = np.ones((3, 3), np.uint8)
        edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)

        return gray, edges

    def find_contours(self, edges):
        contours, hierarchy = cv2.findContours(
            edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
        )

        external_contours = []
        for idx, h in enumerate(hierarchy[0]):
            if h[3] == -1:
                if cv2.contourArea(contours[idx]) > 300:
                    external_contours.append(contours[idx])

        return external_contours

    def calculate_ratio(self, contour):
        area = cv2.contourArea(contour)
        perimeter = cv2.arcLength(contour, True)

        if perimeter == 0 or area == 0:
            return None

        ratio = (perimeter ** 2) / area
        return ratio

    def group_by_similarity(self, contours, ratio_threshold=2.0):
        shape_info = []

        for idx, contour in enumerate(contours):
            ratio = self.calculate_ratio(contour)
            if ratio is not None:
                shape_info.append({
                    'index': idx,
                    'ratio': ratio,
                    'area': cv2.contourArea(contour),
                    'perimeter': cv2.arcLength(contour, True),
                    'contour': contour
                })

        if not shape_info:
            return [], []

        shape_info.sort(key=lambda x: x['ratio'])

        groups = []
        current_group = [shape_info[0]]

        for i in range(1, len(shape_info)):
            avg_ratio = np.mean([s['ratio'] for s in current_group])

            if abs(shape_info[i]['ratio'] - avg_ratio) <= ratio_threshold:
                current_group.append(shape_info[i])
            else:
                groups.append(current_group)
                current_group = [shape_info[i]]

        groups.append(current_group)

        return groups, shape_info

    def calculate_group_statistics(self, group):
        if len(group) < 2:
            return {
                'count': len(group),
                'avg_ratio': group[0]['ratio'],
                'min_ratio': group[0]['ratio'],
                'max_ratio': group[0]['ratio'],
                'std_ratio': 0.0,
                'avg_area': group[0]['area'],
                'scale_ratios': []
            }

        ratios = [s['ratio'] for s in group]
        areas = [s['area'] for s in group]

        scale_ratios = []
        for i in range(len(group)):
            for j in range(i + 1, len(group)):
                scale = np.sqrt(max(group[i]['area'], group[j]['area']) / min(group[i]['area'], group[j]['area']))
                scale_ratios.append(scale)

        return {
            'count': len(group),
            'avg_ratio': np.mean(ratios),
            'min_ratio': np.min(ratios),
            'max_ratio': np.max(ratios),
            'std_ratio': np.std(ratios),
            'avg_area': np.mean(areas),
            'scale_ratios': scale_ratios,
            'avg_scale': np.mean(scale_ratios) if scale_ratios else 1.0,
            'min_scale': np.min(scale_ratios) if scale_ratios else 1.0,
            'max_scale': np.max(scale_ratios) if scale_ratios else 1.0
        }

    def visualize_results(self, groups):
        result_image = self.original_image.copy()

        colors = [
            (255, 0, 0),
            (0, 255, 0),
            (0, 0, 255),
            (255, 255, 0),
            (255, 0, 255),
            (0, 255, 255),
            (255, 128, 0),
            (128, 0, 255),
            (0, 255, 128),
            (255, 0, 128),
        ]

        for group_idx, group in enumerate(groups):
            color = colors[group_idx % len(colors)]

            for shape in group:
                contour = shape['contour']
                cv2.drawContours(result_image, [contour], -1, color, -1)

        return result_image

    def save_results_table(self, groups):
        output_path = os.path.join(self.output_dir, 'results_table.txt')

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("SHAPE SIMILARITY GROUPING RESULTS\n")
            f.write("=" * 80 + "\n")
            f.write(f"\nTotal groups found: {len(groups)}\n")

            for group_idx, group in enumerate(groups):
                stats = self.calculate_group_statistics(group)

                f.write(f"\n{'=' * 80}\n")
                f.write(f"GROUP {group_idx + 1}:\n")
                f.write(f"{'=' * 80}\n")
                f.write(f"Count: {stats['count']}\n")
                f.write(f"\nRatio statistics:\n")
                f.write(f"  Average P²/A ratio: {stats['avg_ratio']:.2f}\n")
                f.write(f"  Min ratio: {stats['min_ratio']:.2f}\n")
                f.write(f"  Max ratio: {stats['max_ratio']:.2f}\n")
                f.write(f"  Std deviation: {stats['std_ratio']:.2f}\n")

                if len(group) > 1:
                    f.write(f"\nScale ratios:\n")
                    f.write(f"  Average scale: {stats['avg_scale']:.2f}x\n")
                    f.write(f"  Min scale: {stats['min_scale']:.2f}x\n")
                    f.write(f"  Max scale: {stats['max_scale']:.2f}x\n")

                f.write(f"\nDetailed object data:\n")
                for shape in group:
                    f.write(f"  Object {shape['index']}: ")
                    f.write(f"P²/A ratio={shape['ratio']:.2f}, ")
                    f.write(f"area={shape['area']:.0f}px², ")
                    f.write(f"perimeter={shape['perimeter']:.1f}px\n")

        print(f"Saved results table: results_table.txt")

    def process(self, ratio_threshold=2.0):
        print("=" * 60)
        print("SHAPE SIMILARITY DETECTION")
        print("=" * 60)
        print(f"Ratio threshold: {ratio_threshold}")

        print("\n1. Preprocessing...")
        gray, edges = self.preprocess_image()

        print("2. Generating histograms...")
        plot_histogram(self.original_image, 'Original Image - Normalized Histogram', 'histogram_original.png')
        plot_histogram(gray, 'Grayscale Image - Normalized Histogram', 'histogram_grayscale.png')

        print("3. Detecting contours...")
        contours = self.find_contours(edges)

        if len(contours) == 0:
            print("No objects found!")
            return

        print("4. Grouping similar shapes...")
        groups, shape_info = self.group_by_similarity(contours, ratio_threshold)
        plot_ratio_histogram(shape_info, groups, self.output_dir)

        print("\n" + "=" * 60)
        print("RESULTS")
        print("=" * 60)
        print(f"Total groups: {len(groups)}")

        for group_idx, group in enumerate(groups):
            stats = self.calculate_group_statistics(group)
            print(f"\nGROUP {group_idx + 1}:")
            print(f"  Count: {stats['count']}")
            print(f"  Avg P²/A ratio: {stats['avg_ratio']:.2f}")
            print(f"  Ratio range: [{stats['min_ratio']:.2f}, {stats['max_ratio']:.2f}]")
            if len(group) > 1:
                print(f"  Avg scale: {stats['avg_scale']:.2f}x")

        print("\n5. Generating visualization...")
        result_image = self.visualize_results(groups)

        cv2.imwrite(os.path.join(self.output_dir, 'result_image.png'), result_image)
        print(f"Saved result image: result_image.png")

        cv2.imwrite(os.path.join(self.output_dir, 'edges.png'), edges)
        print(f"Saved edges image: edges.png")

        self._display_results(result_image, edges, gray)

        print("\n6. Saving results table...")
        self.save_results_table(groups)

        print("\n" + "=" * 60)
        print("COMPLETED SUCCESSFULLY")
        print(f"All outputs saved to: {self.output_dir}/")
        print("=" * 60)

        return result_image, groups

    def _display_results(self, result_image, edges, gray):
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))

        axes[0, 0].imshow(cv2.cvtColor(self.original_image, cv2.COLOR_BGR2RGB))
        axes[0, 0].set_title('Original Image (Input)', fontsize=14)
        axes[0, 0].axis('off')

        axes[0, 1].imshow(gray, cmap='gray')
        axes[0, 1].set_title('Grayscale Image', fontsize=14)
        axes[0, 1].axis('off')

        axes[1, 0].imshow(edges, cmap='gray')
        axes[1, 0].set_title('Detected Edges (Canny)', fontsize=14)
        axes[1, 0].axis('off')

        axes[1, 1].imshow(cv2.cvtColor(result_image, cv2.COLOR_BGR2RGB))
        axes[1, 1].set_title('Grouped Similar Shapes', fontsize=14)
        axes[1, 1].axis('off')

        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, 'visualization.png'), dpi=150, bbox_inches='tight')
        print(f"Saved visualization: visualization.png")
        plt.close()
