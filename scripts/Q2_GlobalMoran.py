"""
GEOG41160 Assignment 2, Question 2: Global spatial autocorrelation 
Team: team 3

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
TREE_DENSITY = OUTPUTS / "DublinED_TreeDensity.gpkg"   # saved by Question 1

## Questions 2 to 4 start from Question 1's output. Question 1 instead reads
## the ED boundaries and the tree points from DATA.
if not TREE_DENSITY.exists():
    raise FileNotFoundError(f"{TREE_DENSITY} not found: run Q1_TreeDensity.py first.")
eds = gpd.read_file(TREE_DENSITY)
print(len(eds), "EDs,", eds.crs)                # 162 EDs, EPSG:2157


#########################################
##### 1. <first item of the question> #####
#########################################

## What this step does, in one or two lines.

# your code here
# print(...)                                    # print every value the answers quote


#########################################
##### 2. <second item of the question> #####
#########################################

# your code here


#########################################
##### 3. <and so on, one section per item> #####
#########################################

# your code here


## Save outputs with the file names the brief asks for, for example:
## fig.savefig(OUTPUTS / "LISA_TreeDensity_DublinED.png", dpi=200, bbox_inches="tight")
