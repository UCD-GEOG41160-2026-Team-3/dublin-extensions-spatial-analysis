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

## Save outputs with the file names the brief asks for, for example:
## fig.savefig(OUTPUTS / "LISA_TreeDensity_DublinED.png", dpi=200, bbox_inches="tight")
