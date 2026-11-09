"""
GEOG41160 Assignment 2, Question 2: Global spatial autocorrelation 
Team: Team 3

ANSWERS

### 1. Distribution
The skewness of extension density is 1.41, so it is strongly right-skewed: most EDs have between 50 and 146 applications per km2 (median 83.6), and a few small EDs have much higher values (max 403.2 per km2).
Moran's I is built on deviations from the mean, so these extreme EDs could dominate it. 
We used np.log1p (log(1 + x)), which squeezes the large values together and spreads the small ones apart, and still works for an ED with 0 applications.
After the transformation the skewness is -1.11: the log has removed the long right tail, but it has spread out a few EDs with very low densities (min 0.7 per km2), which now form a left tail.
Because neither scale is symmetric, we report Moran's I for both the raw and the log1p density and compare them in item 4.

### 2. Weights
Queen contiguity, so two EDs are neighbours if they share a boundary or a corner.
EDs are polygons that cover the whole city, so contiguity reflects which areas actually touch, and Queen keeps EDs that meet only at a corner as neighbours.
The weights were row-standardised, so each ED's weights add up to 1. 
Neighbours: min 2, mean 5.7, max 11, and there are no islands (w.islands = []), so every ED has at least two neighbours.

### 3. Moran's I
raw 0.328 (p = 0.0001); log1p 0.369 (p = 0.0001), 9,999 permutations, seed 42.
The expected value under spatial randomness is -1/(n-1) = -0.006.

### 4. Interpretation
Both values of I are well above the expected -0.006, and none of the 9,999 random maps was as clustered as the real map (p = 0.0001, z = 7.17 raw and 8.05 log1p, far beyond 1.96).
Extension density is therefore clustered: EDs with high densities sit next to other high EDs, and low next to low.
The log transformation does not change the conclusion, but I is higher (0.369 against 0.328), because it reduces the influence of the few EDs with very high densities, so the clustering of the other EDs shows more clearly.
The finding is robust to the transformation. 
"""

from pathlib import Path

import numpy as np
import geopandas as gpd
import matplotlib.pyplot as plt
from scipy.stats import skew
from libpysal.weights import Queen 
from esda.moran import Moran 


#########################################
##### SETUP #####
#########################################

ROOT = Path(__file__).resolve().parents[1]      # the repository folder
DATA = ROOT / "data"
OUTPUTS = ROOT / "outputs"
OUTPUTS.mkdir(exist_ok=True)

SEED = 42                                       # the same seed in every script       
PERMUTATIONS = 9999                              
EXTENSION_DENSITY = OUTPUTS / "DublinED_ExtensionDensity.gpkg"   # saved by Question 1

# Question 2 starts from Question 1's output.
if not EXTENSION_DENSITY.exists():
    raise FileNotFoundError(f"{EXTENSION_DENSITY} not found: run Q1_ExtensionDensity.py first.")
eds = gpd.read_file(EXTENSION_DENSITY)
print(len(eds), "EDs,", eds.crs)                # 162 EDs, EPSG:2157

#########################################
##### 1. DISTRIBUTION AND TRANSFORMATION #####
#########################################

# Check the distribution of extension density with histogram and skewness.
# If it is strongly skewed, use log(1 + x) to reduce the extreme values.

print("\nExtension density (applications per km2):")
print(eds["extension_density"].describe().round(1))

eds["log_density"] = np.log1p(eds["extension_density"])

raw_skew = skew(eds["extension_density"])
log_skew = skew(eds["log_density"])
print("Skewness, raw: %.2f, log: %.2f" % (raw_skew, log_skew))

# Histograms of the raw and log density side by side 
fig, axes = plt.subplots(1, 2, figsize=(10, 3.6))
axes[0].hist(eds["extension_density"], bins=30, color="#d95f0e")
axes[0].set_title("Extension applications per km2")
axes[1].hist(eds["log_density"], bins=30, color="#d95f0e")
axes[1].set_title("log(1 + applications per km2)")
plt.tight_layout()
fig.savefig(OUTPUTS / "Histogram_ExtensionDensity_DublinED.png", dpi=200, bbox_inches="tight")
plt.show()

#########################################
##### 2. SPATIAL WEIGHTS #####
#########################################

# Queen contiguity: EDs are neighbours if they share a boundary or a corner. 
# Check for islands, than row-standardised so each ED's weights add up to 1.

w = Queen.from_dataframe(eds, use_index=True)
print("\nIslands:", w.islands)
print("Neighbours: min", w.min_neighbors, "mean", round(w.mean_neighbors, 1),
      "max", w.max_neighbors)
w.transform = "r"

#########################################
##### 3. GLOBAL MORAN'S I #####
#########################################

# Global Moran's I for the raw and log density, with 9,999 permutations.
# np.random.seed before each run fixes the shuffles, so p is the same every time.

np.random.seed(SEED)
moran_raw = Moran(eds["extension_density"].values, w, permutations=PERMUTATIONS)

np.random.seed(SEED)
moran_log = Moran(eds["log_density"].values, w, permutations=PERMUTATIONS)

print("\nGlobal Moran's I (%d permutations, seed %d)" % (PERMUTATIONS, SEED))
print("Expected under spatial randomness: %.3f" % moran_log.EI)
print("Raw density: I = %.3f, p = %.4f" % (moran_raw.I, moran_raw.p_sim))
print("log1p density: I = %.3f, p = %.4f" % (moran_log.I, moran_log.p_sim))

#########################################
##### 4. INTERPRETATION #####
#########################################

# Count the random maps at least as clustered as the real one, and compare the z-values with 1.96, the threshold for significance at 0.05.

for name, m in [("Raw density", moran_raw), ("log1p density", moran_log)]:
    print("\n%s:" % name)
    print("Random maps at least as clustered:", (m.sim >= m.I).sum(), "of", len(m.sim))
    print("z from the shuffles: %.2f" % m.z_sim)
