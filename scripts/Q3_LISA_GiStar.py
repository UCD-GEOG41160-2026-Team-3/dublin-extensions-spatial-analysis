"""
GEOG41160 Assignment 2, Question 3: Local clusters and hotspots
Team: team 3- Elizabeth McCush and Kyra Hoffman

ANSWERS
Write every paragraph, report, or interpretation the question asks for here,
numbered to match the question's items. Quote the values this script prints,
and update the answers whenever the code changes. For example, for
Question 2:

1. Distribution: skewness of tree density is x.xx, so we used np.log1p because ...
2. Weights: queen contiguity, because ...
3. Moran's I: raw 0.xx (p = 0.xxx); log1p 0.xx (p = 0.xxx),
   9,999 permutations, seed 42.
4. Interpretation: ...
"""

## HOW TO USE THIS TEMPLATE
## Copy it once for each question into scripts/, and rename the copy:
##   Q1_TreeDensity.py, Q2_GlobalMoran.py, Q3_LISA_GiStar.py,
##   Q4_SpatialRegression.py
## Keep one numbered section below for each item of the question, and delete
## this block and any lines that do not apply.
##
## Run it from anywhere: the paths below are worked out from where this file
## is, so the script runs from a fresh copy of the repository.


from pathlib import Path

import numpy as np
import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd

from libpysal.weights import Queen
from esda.moran import Moran_Local
from esda.getisord import G_Local 
from esda import fdr
from matplotlib.patches import Patch
## Add the libraries this question needs, for example:
## from libpysal.weights import Queen
## from esda.moran import Moran


#########################################
##### SETUP #####
#########################################

ROOT = Path(__file__).resolve().parents[1]      # the repository folder
DATA = ROOT / "data"
OUTPUTS = ROOT / "outputs"
OUTPUTS.mkdir(exist_ok=True)

SEED = 42                                       # the same seed in every script
EXTENSION_DENSITY = OUTPUTS / "DublinED_ExtensionDensity.gpkg"   # saved by Question 1

## Questions 2 to 4 start from Question 1's output. Question 1 instead reads
## the ED boundaries and the tree points from DATA.
if not EXTENSION_DENSITY.exists():
    raise FileNotFoundError(f"{EXTENSION_DENSITY} not found: run Q1_ExtensionDensity.py first.")
eds = gpd.read_file(EXTENSION_DENSITY)
print(len(eds), "EDs,", eds.crs)                # 162 EDs, EPSG:2157


#########################################
##### 1. <Compute Local Moran's I (LISA). #####
#########################################

## What this step does, in one or two lines.
##### Calculate Local Moran's I using 9,999 permutations and a fixed seed (42)
##### then classify EDs as High-High, Low-High, Low-Low, High-Low, or Not Significant

# your code here
w = Queen.from_dataframe(eds)
w.transform = "r"

x = eds["extension_density"].fillna(0)

lisa = Moran_Local(
    x,
    w,
    permutations=9999,
    seed=42
)

quadrants = {
    1: "High-High",
    2: "Low-High",
    3: "Low-Low",
    4: "High-Low"
}

classes = pd.Series(lisa.q).map(quadrants)

eds["LISA_Class"] = np.where(
    lisa.p_sim<=0.05,
    classes,
    "Not Significant"
)
#store p-values and quadrants
eds["p_value"] = lisa.p_sim
eds["lisa_Is"] = lisa.Is

# print(...)                                    # print every value the answers quote
print("\nLISA cluster counts:")
print(eds["LISA_Class"].value_counts())

print("\nSignigicant EDs (p<= 0.05):")
print((eds["p_value"] <= 0.05).sum())

#########################################
##### 2. <False Discovery Rate> #####
#########################################
## What this step does, in one or two lines.
#### aplies a False Discovery Rate (FDR) correction to
#### the Local Moran's I p-values and report remaining significant EDS

# your code here
fdr_cutoff = fdr(eds["p_value"].values)

eds["LISA_FDR"] = eds["p_value"] <= fdr_cutoff

#print(..)
print("\nFDR cutoff:")
print(fdr_cutoff)

print("\nSignificant EDs after FDR correction:")
print(eds["LISA_FDR"].sum())

#########################################
##### 3. LISA Cluster Map #####
#########################################
# What this step does, in one or two lines.
####Create a map of the Local Moran's I classes and save is as 
#### LISA_ExtensionDensity_DublinED.png

# your code here
colours = {
    "High-High": "#88a9a8",
    "Low-Low": "#d47799",
    "Low-High": "#f2cd5f",
    "High-Low": "#96bb4b",
    "Not Significant": "#d6d8d9"
}
fig, ax = plt.subplots(figsize= (8, 6))

eds.plot(
    color=eds["LISA_Class"].map(colours),
    edgecolor="black",
    linewidth=0.3,
    ax=ax
)
ax.legend(
    handles=[
        Patch(color=c, label=k)
        for k, c in colours.items()
    ],
    loc="lower right"
)

ax.set_title("Local Moran's I Cluster Map")
ax.set_axis_off()

plt.savefig(
    OUTPUTS / "LISA_ExtensionDensity_DublinED.png",
    dpi=180,
    bbox_inches="tight"
)

plt.show()

#print(..)
print(
    "\nMap saved:",
    OUTPUTS / "LISA_ExtensionDensity_DublinED.png"
)

#########################################################################
##### 4. Computing Getis-Ord Gi* and Classifying Hotspots/Coldspots #####
#########################################################################

from scipy.stats import norm
import libpysal
import esda
import numpy as np

# In this step, we are defining the spatial weights as Queen contiguity weights but
# not row standardized, and running the Getis-Ord Gi* analysis through esda.G_Local

w_bin = libpysal.weights.Queen.from_dataframe(df, use_index=True)
gi = G_Local(x, w_bin, transform="B", star=1.0, permutations=999,seed=42)

# This step turns the results of the Gi* analysis into Z-scores and p-values,
# as well as counting the hotspots and coldspots

df["gi_z"] = gi.Zs
df["gi_p"] = 2 * norm.sf(np.abs(gi.Zs))
print("Hotspots:", (df["gi_z"] > 1.96).sum(),
      "| Coldspots:", (df["gi_z"] < -1.96).sum())

# This step applies the false discovery rate correction to two-sided p-values

threshold = esda.fdr(df["gi_p"].values, 0.05)
print(df.loc[df["gi_p"] <= threshold, ["ED_ENGLISH", "gi_z"]])

#############################################
##### 5. Mapping Hotspots and Coldspots #####
#############################################

# This step maps the hotspots and coldspots with a diverging color scheme

lim = np.abs(df["gi_z"]).max()
fig, ax = plt.subplots(figsize=(7, 6))
df.plot(column="gi_z", cmap="RdBu_r", vmin=-lim, vmax=lim, legend=True,
        edgecolor="grey", linewidth=0.3, ax=ax, legend_kwds={"label": "Gi* Z-score", "shrink": 0.6})
df[df["gi_p"] <= theshold].boundary.plot(ax=ax, color="black", linewidth=2)
ax.set_title("Getis-Ord Gi* Z-scores (outlined: significant after FDR)")
ax.set_axis_off()
plt.savefig(OUTPUTS / "GiStar_ExtensionDensity_DublinED.png", dpi=300, bbox_inches="tight")
plt.show()

######################################
##### 6. Comparing Gi* with LISA #####
######################################

# This step defines the hotspots and coldspots based on
# Z-score and compares the Gi* classes to the LISA classes

df["gi_class"] = np.where(
    df["gi_z"] > 1.96, "Hotspot",
    np.where(df["gi_z"] < -1.96, "Coldspot", "Not significant")
)
print(df["gi_class"].value_counts())

print(pd.crosstab(df["lisa_class"], df["gi_class"]))

