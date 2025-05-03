import matplotlib.pyplot as plt
from shapely.geometry import Polygon, Point, box
from shapely.affinity import rotate
import random
import numpy as np
from image_processing import extract_yard_and_obstacles

# --- Parameters ---
yard_poly, obstacle = extract_yard_and_obstacles()
print(yard_poly)
grave_width = 1
grave_height = 2
spacing = 0.5
num_obstacles = 5
grave_angle_deg = -60
indicator_angle_deg = 30

# --- Helper Functions ---
def generate_irregular_polygon(center_x, center_y, radius, num_points=8):
    angles = sorted([random.uniform(0, 2 * np.pi) for _ in range(num_points)])
    points = [
        (center_x + np.cos(angle) * (radius * random.uniform(0.7, 1.0)),
         center_y + np.sin(angle) * (radius * random.uniform(0.7, 1.0)))
        for angle in angles
    ]
    return Polygon(points).buffer(0)

def generate_random_obstacles(polygon, count=5, max_size=4):
    minx, miny, maxx, maxy = polygon.bounds
    obstacles = []
    tries = 0
    while len(obstacles) < count and tries < 1000:
        tries += 1
        w, h = random.uniform(1, max_size), random.uniform(1, max_size)
        x, y = random.uniform(minx, maxx - w), random.uniform(miny, maxy - h)
        ob = box(x, y, x + w, y + h)
        if polygon.contains(ob):
            obstacles.append(ob)
    return obstacles

def place_graves_with_circles(yard, obstacles, grave_size=(1, 2), spacing=0.5, angle=0):
    graves = []
    circles = []
    w, h = grave_size
    diagonal = np.hypot(w, h)
    diameter = diagonal + spacing
    radius = diameter / 2

    minx, miny, maxx, maxy = yard.bounds
    y = miny
    while y + diameter <= maxy:
        x = minx
        while x + diameter <= maxx:
            circle_center = Point(x + radius, y + radius)
            c = circle_center.buffer(radius)
            g = box(x + radius - w/2, y + radius - h/2, x + radius + w/2, y + radius + h/2)
            g_center = g.centroid
            g_rotated = rotate(g, angle, origin=g_center, use_radians=False)

            # Avoid intersecting with obstacles and previously placed graves
            if yard.contains(c) and yard.contains(g_rotated) and \
               all(not c.intersects(ob) for ob in obstacles) and \
               all(not c.intersects(other) for other in circles):
                graves.append(g_rotated)
                circles.append(c)
            x += diameter  # Step to the next possible grave position
        y += diameter
    return graves, circles

def draw_direction_arrows(ax, corner, length=5, angle=0):
    directions = {
        "N": (0, 1),
        "E": (1, 0),
        "S": (0, -1),
        "W": (-1, 0)
    }
    angle_rad = np.radians(angle)
    cos_a, sin_a = np.cos(angle_rad), np.sin(angle_rad)
    for label, (dx, dy) in directions.items():
        rx = dx * cos_a - dy * sin_a
        ry = dx * sin_a + dy * cos_a
        ax.arrow(corner[0], corner[1], rx * length, ry * length,
                 head_width=0.7, head_length=1, fc='blue', ec='blue')
        ax.text(corner[0] + rx * (length + 1), corner[1] + ry * (length + 1), label,
                fontsize=10, ha='center', va='center', color='blue')

# --- Generate Yard and Obstacles ---
yard_poly1 = generate_irregular_polygon(25, 25, 25)
print(yard_poly1)
obstacles = generate_random_obstacles(yard_poly, count=num_obstacles)

# --- Place Graves ---
graves, circles = place_graves_with_circles(yard_poly, obstacles, (grave_width, grave_height), spacing, angle=grave_angle_deg)

# --- Visualization ---
fig, ax = plt.subplots(figsize=(10, 10))
x, y = yard_poly.exterior.xy
ax.fill(x, y, color='lightgreen', label='Yard')

for ob in obstacles:
    x, y = ob.exterior.xy
    ax.fill(x, y, color='brown')

for i, grave in enumerate(graves):
    x, y = grave.exterior.xy
    ax.fill(x, y, color='gray')
    center = grave.centroid
    ax.text(center.x, center.y, str(i + 1), fontsize=6, ha='center', va='center', color='white')

for c in circles:
    x, y = c.exterior.xy
    ax.plot(x, y, color='cyan', linestyle='--', linewidth=0.8)

minx, miny, maxx, maxy = yard_poly.bounds
indicator_corner = (maxx + 5, maxy + 5)
draw_direction_arrows(ax, indicator_corner, length=3, angle=indicator_angle_deg)

ax.set_title(f"Graves Facing {grave_angle_deg}° | Indicator Angle: {indicator_angle_deg}°")
ax.set_aspect('equal')
ax.axis('off')
plt.tight_layout()
plt.show()
