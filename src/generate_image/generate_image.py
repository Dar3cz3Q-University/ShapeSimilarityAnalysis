import cv2
import numpy as np
import random
import os
from config.constants import GENERATE_DIR

def generate_random_color():
    return (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))

def check_collision(occupied_areas, new_bbox, margin=10):
    x1_new, y1_new, x2_new, y2_new = new_bbox

    x1_new -= margin
    y1_new -= margin
    x2_new += margin
    y2_new += margin

    for (x1, y1, x2, y2) in occupied_areas:
        if not (x2_new < x1 or x1_new > x2 or y2_new < y1 or y1_new > y2):
            return True

    return False

def find_free_position(
    occupied_areas, width, height, obj_width, obj_height,
    margin_border=80, margin_objects=10, max_attempts=100
):
    for _ in range(max_attempts):
        cx = random.randint(margin_border + obj_width // 2, width - margin_border - obj_width // 2)
        cy = random.randint(margin_border + obj_height // 2, height - margin_border - obj_height // 2)

        bbox = (
            cx - obj_width // 2,
            cy - obj_height // 2,
            cx + obj_width // 2,
            cy + obj_height // 2
        )

        if not check_collision(occupied_areas, bbox, margin_objects):
            return cx, cy, bbox

    return None

def rotate_points(points, angle, center):
    angle_rad = np.radians(angle)
    cos_angle = np.cos(angle_rad)
    sin_angle = np.sin(angle_rad)

    rotated = []
    for point in points:
        x, y = point
        x -= center[0]
        y -= center[1]

        x_new = x * cos_angle - y * sin_angle
        y_new = x * sin_angle + y * cos_angle

        x_new += center[0]
        y_new += center[1]

        rotated.append([int(x_new), int(y_new)])

    return np.array(rotated)

def generate_circles(image, width, height, occupied_areas, count=5):
    total_circles = 0
    skipped = 0

    for _ in range(count):
        color = generate_random_color()
        radius = random.randint(20, 60)

        result = find_free_position(occupied_areas, width, height, radius*2, radius*2, margin_objects=15)

        if result is None:
            skipped += 1
            continue

        cx, cy, bbox = result

        cv2.circle(image, (cx, cy), radius, color, -1)

        occupied_areas.append(bbox)
        total_circles += 1

    return total_circles

def generate_squares(image, width, height, occupied_areas, count=5):
    total_squares = 0
    skipped = 0

    for _ in range(count):
        color = generate_random_color()
        size = random.randint(40, 80)

        diag = int(np.sqrt(2 * size**2))
        result = find_free_position(occupied_areas, width, height, diag, diag, margin_objects=15)

        if result is None:
            skipped += 1
            continue

        cx, cy, bbox = result

        angle = random.randint(0, 360)

        x = cx - size // 2
        y = cy - size // 2
        points = [
            [x, y],
            [x + size, y],
            [x + size, y + size],
            [x, y + size]
        ]

        rotated_points = rotate_points(points, angle, (cx, cy))

        cv2.fillPoly(image, [rotated_points], color)

        occupied_areas.append(bbox)
        total_squares += 1

    return total_squares

def generate_triangles(image, width, height, occupied_areas, count=5):
    total_triangles = 0
    skipped = 0

    for _ in range(count):
        color = generate_random_color()
        side_length = random.randint(40, 80)

        height_triangle = int(side_length * np.sqrt(3) / 2)

        diag = int(np.sqrt(side_length**2 + height_triangle**2))
        result = find_free_position(occupied_areas, width, height, diag, diag, margin_objects=15)

        if result is None:
            skipped += 1
            continue

        cx, cy, bbox = result
        angle = random.randint(0, 360)

        h = height_triangle
        pts = [
            [cx, cy - int(2*h/3)],
            [cx - side_length//2, cy + int(h/3)],
            [cx + side_length//2, cy + int(h/3)]
        ]

        rotated_pts = rotate_points(pts, angle, (cx, cy))

        cv2.fillPoly(image, [rotated_pts], color)

        occupied_areas.append(bbox)
        total_triangles += 1

    return total_triangles

def generate_image(
        width=800, height=600, filename='image.png',
        num_circles=5, num_squares=5, num_triangles=5, seed=None):
    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)

    image = np.ones((height, width, 3), dtype=np.uint8) * 255

    occupied_areas = []
    stats = {}

    print(f"Generating image {width}x{height}...")

    stats['circles'] = generate_circles(image, width, height, occupied_areas, num_circles)
    print(f"Circles: {stats['circles']}")

    stats['squares'] = generate_squares(image, width, height, occupied_areas, num_squares)
    print(f"Squares: {stats['squares']}")

    stats['triangles'] = generate_triangles(image, width, height, occupied_areas, num_triangles)
    print(f"Triangles: {stats['triangles']}")

    cv2.imwrite(os.path.join(GENERATE_DIR, filename), image)

    total = sum(stats.values())
    print(f"Generated {total} objects total")
    print(f"Saved to: {filename}")

    return image, stats

if __name__ == "__main__":
    generate_image()
