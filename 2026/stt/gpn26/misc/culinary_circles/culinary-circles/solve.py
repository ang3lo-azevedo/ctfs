import numpy as np
import matplotlib.pyplot as plt

def latlon_to_cartesian(lat, lon):
    """Convert Lat/Lon (degrees) to 3D Cartesian coordinates on a unit sphere."""
    lat_rad = np.radians(lat)
    lon_rad = np.radians(lon)
    x = np.cos(lat_rad) * np.cos(lon_rad)
    y = np.cos(lat_rad) * np.sin(lon_rad)
    z = np.sin(lat_rad)
    return np.array([x, y, z])<

def cartesian_to_latlon(v):
    """Convert 3D Cartesian vectors back to Lat/Lon."""
    x, y, z = v
    lat = np.degrees(np.arcsin(z))
    lon = np.degrees(np.arctan2(y, x))
    return lat, lon

# 1. Input the coordinates from all 9 known locations
points = {
    # Circle A
    "Adam": latlon_to_cartesian(55.4578, 12.1818),      # Køge, DK
    "Alice": latlon_to_cartesian(52.8620, -8.1985),     # Nenagh, IE
    "Alkalem": latlon_to_cartesian(49.0075, 8.4193),    # Karlsruhe, DE
    
    # Circle C (Updated Catherine)
    "Carol": latlon_to_cartesian(59.3247, 18.0763),     # Stockholm, SE
    "Catherine": latlon_to_cartesian(55.8982821, -3.7026378), # Armadale, UK
    "Cristoph": latlon_to_cartesian(54.8994, 9.7955),   # Sønderborg, DK
    
    # Circle B (Checksum + Bob)
    "Bruno": latlon_to_cartesian(51.9954, 4.4752),      # Berkel en Rodenrijs, NL
    "Beatrice": latlon_to_cartesian(47.3226, 5.0381),   # Dijon, FR
    "Bob": latlon_to_cartesian(38.6975, -9.2032)        # Belem, PT (Pastéis de Belém)
}

# 2. Define Plane A and Plane C
vA1, vA2, vA3 = points["Adam"], points["Alice"], points["Alkalem"]
normalA = np.cross(vA2 - vA1, vA3 - vA1)
normalA = normalA / np.linalg.norm(normalA)
distanceA = np.dot(normalA, vA1)

vC1, vC2, vC3 = points["Carol"], points["Catherine"], points["Cristoph"]
normalC = np.cross(vC2 - vC1, vC3 - vC1)
normalC = normalC / np.linalg.norm(normalC)
distanceC = np.dot(normalC, vC1)

# 3. Define Plane B
vB1, vB2, vB3 = points["Bruno"], points["Beatrice"], points["Bob"]
normalB = np.cross(vB2 - vB1, vB3 - vB1)
normalB = normalB / np.linalg.norm(normalB)
distanceB = np.dot(normalB, vB1)

# 4. Find the intersection of Plane A, Plane B, and Plane C
A_matrix = np.array([normalA, normalB, normalC])
B_vector = np.array([distanceA, distanceB, distanceC])

try:
    intersection_3d = np.linalg.solve(A_matrix, B_vector)
    
    r = np.linalg.norm(intersection_3d)
    print(f"Intersection distance from center: {r:.5f} (should be ~1.0 if on the surface)")
    
    if abs(r - 1.0) < 0.01:
        lat, lon = cartesian_to_latlon(intersection_3d)
        print("--- INTERSECTION OF A, B, C ---")
        print(f"Point: {lat:.5f}, {lon:.5f}")
    else:
        print(f"The 3 planes intersect at a point not on the surface! (r={r:.5f})")
        # Let's project it onto the sphere anyway
        lat, lon = cartesian_to_latlon(intersection_3d / r)
        print(f"Projected point on surface: {lat:.5f}, {lon:.5f}")

except np.linalg.LinAlgError:
    print("The three planes are co-axial (matrix is singular). They intersect at a line, meaning all 3 circles share 2 points!")

# ----------------- VISUALIZATION -----------------

print("Generating 3D visualization...")
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')

# Draw a sphere
u, v = np.mgrid[0:2*np.pi:50j, 0:np.pi:25j]
x = np.cos(u)*np.sin(v)
y = np.sin(u)*np.sin(v)
z = np.cos(v)
ax.plot_surface(x, y, z, color="lightblue", alpha=0.3, edgecolor='none')

def plot_circle(ax, normal, distance, color, name):
    center = distance * normal
    if distance**2 >= 1: return
    r_circle = np.sqrt(1 - distance**2)
    
    if abs(normal[0]) > 0.5:
        w = np.array([0, 1, 0])
    else:
        w = np.array([1, 0, 0])
        
    u1 = np.cross(normal, w)
    u1 = u1 / np.linalg.norm(u1)
    u2 = np.cross(normal, u1)
    
    t = np.linspace(0, 2*np.pi, 100)
    circle_pts = center[:, None] + r_circle * (np.outer(u1, np.cos(t)) + np.outer(u2, np.sin(t)))
    ax.plot(circle_pts[0,:], circle_pts[1,:], circle_pts[2,:], color=color, linewidth=2, label=name)

plot_circle(ax, normalA, distanceA, 'red', 'Circle A')
plot_circle(ax, normalB, distanceB, 'green', 'Circle B')
plot_circle(ax, normalC, distanceC, 'blue', 'Circle C')

# Plot the locations
for name, pt in points.items():
    ax.scatter(pt[0], pt[1], pt[2], color='black', s=30)
    ax.text(pt[0], pt[1], pt[2] + 0.05, name, size=9)

# Plot intersection
ax.scatter(intersection_3d[0], intersection_3d[1], intersection_3d[2], color='magenta', s=100, marker='*', label='Intersection')

# Set camera angle
ax.view_init(elev=50, azim=0)

plt.legend()
plt.title("Culinary Circles - 3D Visualization")

# Save to artifacts
output_path = '/home/ang3lo/.gemini/antigravity-ide/brain/7e64e277-5544-46c3-82f2-cd975c556cd5/visualization.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"Visualization saved to {output_path}")