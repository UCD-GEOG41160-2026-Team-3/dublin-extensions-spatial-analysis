# GEOG41160 Assignment 2 - Team 3
Kyra Hoffman, Shakthi Anand, Cara Wilson, Lizzie 

## Description
This python workflow analyses where people in Dublin City extend their
buildings based on the density of planning applications for extensions by Electoral Division (ED),
performing global spatial autocorrelation, and analyzing local clusters and hot-spots.

### Sprint 0 - Setup
Date: 28/10/2026
Members: All present
What Was Done: We all read the brief to gain a better understanding of the task. Our github organization "UCD-GEOG41160-2026-Team-3" was created along with our repository "dublin-extensions-spatial-analysis". All members were added as owners. We worked to get everyone to clone the repo onto their local computer. Permissions affected Lizzie cloning the repo so we still need to fix that issue. Kyra, Shakthi, and Cara were able to make commits. We have also chosen our roles. Lizzie has fixed the cloning issue and is now in on VS code.
What is Next: Discuss the workflow for each step, download the data packages, and begin writing scripts.

### Sprint 1 – Extension Density Analysis
Date: 02/11/2026 

Members: Kyra Hoffman, Shakthi Anand, Cara Wilson, Lizzie

What Was Done:
During Sprint 1, the team worked on Question 1, which involved analysing the density of planning applications for building extensions across Dublin City Electoral Divisions.

The completed work included:
- Creating the DuckDB spatial database and importing the national datasets.
- Filtering the data to 162 Dublin City EDs and 9,657 extension applications received between 2019 and 2025.
- Reprojecting the applications to EPSG:2157 and spatially joining them to the ED boundaries.
- Identifying 14 applications that did not match any ED.
- Calculating extension application density for each ED.
- Generating DublinED_ExtensionDensity.gpkg and ExtensionDensity_DublinED.png.
The Question 1 script, Q1_ExtensionDensity.py, was completed and tested.

What Is Next:The next steps are to review the Question 1 script and outputs with the team, commit the completed work to GitHub and begin Question 2, which involves global spatial autocorrelation using extension density.

### Sprint 1 - Global Spatial Autocorrelation 
Date: 06/11/2026

Members: Members: Kyra Hoffman, Shakthi Anand, Cara Wilson, Lizzie

What Was Done:
During Sprint 2, the team worked on Question 2, which involved testing whether extension application density is spatially clustered across Dublin City EDs using Global Moran's I.

The completed work included:
- Checking the distribution of extension density: skewness of 1.41 (right-skewed), and -1.11 after a log1p transformation. 
- Plotting histograms of the raw and log1p density. 
- Building Queen contiguity spatial weights and row-standardising them (min 2, mean 5.7, max 11 neighbours, no islands).
- Calculating Global Moran's I with 9,999 permutations and seed 42: raw density I = 0.328 (p = 0.0001) and log1p density I = 0.369 (p = 0.0001).
- Interpreting the results: extension density is significantly clustered, and the conclusion does not change with the log transformation. 
- Generating Histogram_ExtensionDensity_DublinED.png.
The Question 2 script, Q2_GlobalMoran.py, was complted and tested.

What Is Next: Review the Question 2 script and outputs with the team, commit the completed work to GitHub and begin Question 3, which involves Local Moran's I (LISA) and Getis-Ord Gi* hot-spot analysis. 