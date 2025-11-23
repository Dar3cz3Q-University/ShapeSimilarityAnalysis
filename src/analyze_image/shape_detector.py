import cv2
import numpy as np
import matplotlib.pyplot as plt
import sys
import os
from utils.histogram import plot_histogram
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
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, 50, 150)

        return gray, edges

    def find_contours(self, edges):
        contours, hierarchy = cv2.findContours(
            edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        min_area = 500
        filtered_contours = [cnt for cnt in contours if cv2.contourArea(cnt) > min_area]

        print(f"Found {len(filtered_contours)} objects")

        return filtered_contours

    def classify_shape(self, contour):
        area = cv2.contourArea(contour)
        perimeter = cv2.arcLength(contour, True)

        if perimeter == 0:
            return "unknown", 0

        ratio = (perimeter ** 2) / area

        circle_ratio = 4 * np.pi
        square_ratio = 16
        triangle_ratio = 20.78

        diff_circle = abs(ratio - circle_ratio)
        diff_square = abs(ratio - square_ratio)
        diff_triangle = abs(ratio - triangle_ratio)

        min_diff = min(diff_circle, diff_square, diff_triangle)

        if min_diff == diff_circle:
            return "circle", ratio
        elif min_diff == diff_square:
            return "square", ratio
        else:
            return "triangle", ratio

    def group_by_shape(self, contours):
        groups = {
            "circle": [],
            "square": [],
            "triangle": [],
            "unknown": []
        }

        shape_info = []

        for idx, contour in enumerate(contours):
            shape_type, ratio = self.classify_shape(contour)
            groups[shape_type].append(idx)
            shape_info.append({
                'index': idx,
                'type': shape_type,
                'ratio': ratio,
                'area': cv2.contourArea(contour),
                'perimeter': cv2.arcLength(contour, True)
            })

        return groups, shape_info

    def calculate_similarity_within_group(self, group_indices, shape_info):
        if len(group_indices) < 2:
            return {
                'count': len(group_indices),
                'avg_similarity': 1.0,
                'min_similarity': 1.0,
                'max_similarity': 1.0,
                'scale_ratios': []
            }

        similarities = []
        scale_ratios = []

        for i in range(len(group_indices)):
            for j in range(i + 1, len(group_indices)):
                idx1, idx2 = group_indices[i], group_indices[j]
                info1 = shape_info[idx1]
                info2 = shape_info[idx2]

                ratio_diff = abs(info1['ratio'] - info2['ratio'])
                max_ratio = max(info1['ratio'], info2['ratio'])
                ratio_similarity = 1.0 - (ratio_diff / max_ratio)

                area_diff = abs(info1['area'] - info2['area'])
                max_area = max(info1['area'], info2['area'])
                area_similarity = 1.0 - (area_diff / max_area)

                similarity = (ratio_similarity + area_similarity) / 2
                similarities.append(similarity)

                scale = np.sqrt(max(info1['area'], info2['area']) / min(info1['area'], info2['area']))
                scale_ratios.append(scale)

        return {
            'count': len(group_indices),
            'avg_similarity': np.mean(similarities),
            'min_similarity': np.min(similarities),
            'max_similarity': np.max(similarities),
            'scale_ratios': scale_ratios,
            'avg_scale': np.mean(scale_ratios) if scale_ratios else 1.0,
            'min_scale': np.min(scale_ratios) if scale_ratios else 1.0,
            'max_scale': np.max(scale_ratios) if scale_ratios else 1.0
        }

    def visualize_results(self, contours, groups):
        result_image = self.original_image.copy()

        colors = {
            "circle": (255, 0, 0),
            "square": (0, 255, 0),
            "triangle": (0, 0, 255),
            "unknown": (128, 128, 128)
        }

        for shape_type, indices in groups.items():
            if len(indices) == 0:
                continue

            color = colors[shape_type]

            for idx in indices:
                cv2.drawContours(result_image, [contours[idx]], -1, color, 3)

                M = cv2.moments(contours[idx])
                if M["m00"] != 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])
                    cv2.putText(result_image, shape_type[0].upper(), (cx, cy), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)

        return result_image

    def save_results_table(self, groups, shape_info, similarities):
        output_path = os.path.join(self.output_dir, 'results_table.txt')

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("SHAPE DETECTION RESULTS\n")
            f.write("=" * 80 + "\n")

            for shape_type in ["circle", "square", "triangle"]:
                indices = groups[shape_type]
                if len(indices) == 0:
                    continue

                f.write(f"\n{shape_type.upper()}S:\n")
                f.write("-" * 80 + "\n")
                f.write(f"Count: {len(indices)}\n")

                if len(indices) > 1:
                    sim = similarities[shape_type]
                    f.write(f"\nSimilarity metrics:\n")
                    f.write(f"  Average similarity: {sim['avg_similarity']:.2%}\n")
                    f.write(f"  Min similarity: {sim['min_similarity']:.2%}\n")
                    f.write(f"  Max similarity: {sim['max_similarity']:.2%}\n")

                    f.write(f"\nScale ratios:\n")
                    f.write(f"  Average scale: {sim['avg_scale']:.2f}x\n")
                    f.write(f"  Min scale: {sim['min_scale']:.2f}x\n")
                    f.write(f"  Max scale: {sim['max_scale']:.2f}x\n")

                f.write(f"\nDetailed object data:\n")
                for idx in indices:
                    info = shape_info[idx]
                    f.write(f"  Object {info['index']}: ")
                    f.write(f"P^2/A ratio={info['ratio']:.2f}, ")
                    f.write(f"area={info['area']:.0f}px^2, ")
                    f.write(f"perimeter={info['perimeter']:.1f}px\n")

                f.write("\n")

        print(f"Saved results table: results_table.txt")

    def process(self):
        print("=" * 60)
        print("SHAPE DETECTION AND CLASSIFICATION")
        print("=" * 60)

        print("1. Preprocessing...")
        gray, edges = self.preprocess_image()

        print("2. Generating histograms...")
        plot_histogram(self.original_image, 'Original Image - Normalized Histogram', 'histogram_original.png')
        plot_histogram(gray, 'Grayscale Image - Normalized Histogram', 'histogram_grayscale.png')

        print("3. Detecting contours...")
        contours = self.find_contours(edges)

        if len(contours) == 0:
            print("No objects found!")
            return

        print("4. Classifying shapes...")
        groups, shape_info = self.group_by_shape(contours)

        print("5. Calculating similarity...")
        similarities = {}
        for shape_type, indices in groups.items():
            if len(indices) > 0:
                similarities[shape_type] = self.calculate_similarity_within_group(indices, shape_info)

        print("\n" + "=" * 60)
        print("RESULTS")
        print("=" * 60)

        for shape_type in ["circle", "square", "triangle"]:
            indices = groups[shape_type]
            if len(indices) == 0:
                continue

            print(f"\n{shape_type.upper()}S:")
            print(f"  Count: {len(indices)}")

            if len(indices) > 1:
                sim = similarities[shape_type]
                print(f"  Avg similarity: {sim['avg_similarity']:.2%}")
                print(f"  Min similarity: {sim['min_similarity']:.2%}")
                print(f"  Max similarity: {sim['max_similarity']:.2%}")
                print(f"  Avg scale: {sim['avg_scale']:.2f}x")

        print("\n6. Generating visualization...")
        result_image = self.visualize_results(contours, groups)

        cv2.imwrite(os.path.join(self.output_dir, 'result_image.png'), result_image)
        print(f"Saved result image: result_image.png")

        cv2.imwrite(os.path.join(self.output_dir, 'edges.png'), edges)
        print(f"Saved edges image: edges.png")

        self._display_results(result_image, edges, gray)

        print("\n7. Saving results table...")
        self.save_results_table(groups, shape_info, similarities)

        print("\n" + "=" * 60)
        print("COMPLETED SUCCESSFULLY")
        print(f"All outputs saved to: {self.output_dir}/")
        print("=" * 60)

        return result_image, groups, similarities

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
        axes[1, 1].set_title('Classified Shapes (Output)', fontsize=14)
        axes[1, 1].axis('off')

        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, 'visualization.png'), dpi=150, bbox_inches='tight')
        print(f"Saved visualization: visualization.png")
        plt.close()
