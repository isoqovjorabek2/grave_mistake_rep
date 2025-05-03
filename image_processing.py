import cv2
import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import Polygon, box
import random
path = 'C:/Users/computter/PycharmProjects/grave_mistake/img.png'
# Use this if you want to test without an image
def generate_irregular_polygon(center_x, center_y, radius, num_points=8):
    angles = sorted([random.uniform(0, 2 * np.pi) for _ in range(num_points)])
    points = [
        (
            center_x + np.cos(angle) * (radius * random.uniform(0.7, 1.0)),
            center_y + np.sin(angle) * (radius * random.uniform(0.7, 1.0))
        )
        for angle in angles
    ]
    return Polygon(points).buffer(0)

def generate_random_obstacles(polygon, count=5, max_size=30):
    minx, miny, maxx, maxy = polygon.bounds
    obstacles = []
    tries = 0
    while len(obstacles) < count and tries < 1000:
        tries += 1
        w, h = random.uniform(10, max_size), random.uniform(10, max_size)
        x, y = random.uniform(minx, maxx - w), random.uniform(miny, maxy - h)
        ob = box(x, y, x + w, y + h)
        if polygon.contains(ob):
            obstacles.append(ob)
    return obstacles

# This handles real image processing
def extract_yard_and_obstacles(image_path=path):
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError("Failed to load image!")

    image = cv2.resize(image, (800, 600))
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    lower_green = np.array([40, 40, 40])
    upper_green = np.array([80, 255, 255])
    green_mask = cv2.inRange(hsv, lower_green, upper_green)

    kernel = np.ones((15, 15), np.uint8)
    green_mask_closed = cv2.morphologyEx(green_mask, cv2.MORPH_CLOSE, kernel)

    contours, _ = cv2.findContours(green_mask_closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        raise ValueError("No green area found!")

    main_contour = max(contours, key=cv2.contourArea)
    epsilon = 0.01 * cv2.arcLength(main_contour, True)
    approx = cv2.approxPolyDP(main_contour, epsilon, True)
    pts = [tuple(pt[0]) for pt in approx]
    if pts[0] != pts[-1]:
        pts.append(pts[0])
    yard_polygon = Polygon(pts)

    polygon_mask = np.zeros(image.shape[:2], dtype=np.uint8)
    cv2.fillPoly(polygon_mask, [np.array(pts, dtype=np.int32)], 255)

    lower_red1 = np.array([0, 70, 50])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([170, 70, 50])
    upper_red2 = np.array([180, 255, 255])
    red_mask = cv2.inRange(hsv, lower_red1, upper_red1) | cv2.inRange(hsv, lower_red2, upper_red2)
    red_mask_in_polygon = cv2.bitwise_and(red_mask, red_mask, mask=polygon_mask)

    red_contours, _ = cv2.findContours(red_mask_in_polygon, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    obstacles = []
    for cnt in red_contours:
        epsilon = 0.01 * cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, epsilon, True)
        poly = Polygon([tuple(pt[0]) for pt in approx])
        if poly.is_valid and poly.area > 0:
            obstacles.append(poly)

    return yard_polygon, obstacles

# Visualization helper
def plot_polygon_with_obstacles(yard_poly, obstacles):
    fig, ax = plt.subplots(figsize=(8, 6))
    x, y = yard_poly.exterior.xy
    ax.fill(x, y, color='green', alpha=0.4, label="Yard")

    for i, ob in enumerate(obstacles):
        ox, oy = ob.exterior.xy
        ax.fill(ox, oy, color='red', alpha=0.6)

    ax.set_title("Yard and Obstacles")
    ax.set_aspect('equal')
    plt.legend()
    plt.grid(True)
    plt.show()

# ================================
# USE IMAGE OR GENERATE SYNTHETIC
# ================================
try:

    yard, obs = extract_yard_and_obstacles(path)
    plot_polygon_with_obstacles(yard, obs)
except Exception as e:
    print(f"Image failed, generating synthetic data instead: {e}")
    yard = generate_irregular_polygon(400, 300, 250)
    obs = generate_random_obstacles(yard, count=10)
    plot_polygon_with_obstacles(yard, obs)
