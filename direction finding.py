import numpy as np
import matplotlib.pyplot as plt

# convert latitude and longitude to Cartesian coordinates (meters)
def latlon_to_meters(lat1, lon1, lat2, lon2):
    R = 6378137  # Radius of Earth)
    lat1_rad, lon1_rad = np.radians(lat1), np.radians(lon1)
    lat2_rad, lon2_rad = np.radians(lat2), np.radians(lon2)
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    dy = dlat * R
    dx = dlon * R * np.cos(lat1_rad)
    return dx, dy

# Receiver locations and C/N drops during jamming
#upate the cno values for each run
receivers = [
    {"lat": 69.2724, "lon": 15.9598, "cno_drop": 18.9817},
    {"lat": 69.2762, "lon": 15.9690, "cno_drop": 20.9303},
    {"lat": 69.2707, "lon": 15.9581, "cno_drop": 5.8306},
    {"lat": 69.2731, "lon": 15.9440, "cno_drop": 19.48021},
    {"lat": 69.2744, "lon": 15.9499, "cno_drop": 20.1485},
]

# Ground truth jammer location
jammer_location = {"lat": 69.280072, "lon": 16.006435}

ref_lat = np.mean([rx["lat"] for rx in receivers])
ref_lon = np.mean([rx["lon"] for rx in receivers])

# Convert coordinates to cartesian system
for rx in receivers:
    rx["dx"], rx["dy"] = latlon_to_meters(ref_lat, ref_lon, rx["lat"], rx["lon"])

jammer_dx, jammer_dy = latlon_to_meters(ref_lat, ref_lon, jammer_location["lat"], jammer_location["lon"])

# Compute gradient vectors
vectors = []
for i, rx1 in enumerate(receivers):
    for j, rx2 in enumerate(receivers):
        if i >= j:
            continue
        # Vector computation
        diff_cno = rx2["cno_drop"] - rx1["cno_drop"]
        dx = rx2["dx"] - rx1["dx"]
        dy = rx2["dy"] - rx1["dy"]
        magnitude = np.sqrt(dx**2 + dy**2)
        if magnitude > 0:
            vectors.append({"vector": (dx / magnitude * diff_cno, dy / magnitude * diff_cno)})

# Average the vectors to determine the resultant direction
resultant_vector = np.mean([v["vector"] for v in vectors], axis=0)

vector_scale = 5  # Scale factor for extending the red arrow
resultant_vector = resultant_vector * vector_scale

# Visualization
plt.figure(figsize=(10, 8))

# Plot receivers
for rx in receivers:
    plt.scatter(rx["dx"], rx["dy"], color="blue", s=100)
    plt.text(rx["dx"] + 50, rx["dy"] + 50, f"Drop: {rx['cno_drop']} dB", fontsize=10)

# Plot vectors
for v in vectors:
    dx, dy = v["vector"]
    plt.arrow(0, 0, dx, dy, color="gray", alpha=0.5)

plt.arrow(0, 0, resultant_vector[0], resultant_vector[1], color="red", width=50, label="Resultant Direction")

# Plot actual jammer location
plt.scatter(jammer_dx, jammer_dy, color="green", marker="x", label="Actual Jammer", s=150)
plt.text(jammer_dx + 50, jammer_dy + 50, "Jammer", fontsize=12, color="green")

plt.title("Jammer Direction Based on C/N₀ Gradient", fontsize=16)
plt.xlabel("East-West Distance (meters)", fontsize=14)
plt.ylabel("North-South Distance (meters)", fontsize=14)
plt.grid(True)
plt.legend(fontsize=10, loc="upper left")
plt.tight_layout()
plt.show()

print("Resultant Direction Vector (meters):", resultant_vector)
