"""
GEOG41160 Assignment 2, Question 1 : Extension density by ED
Team: Team 3

ANSWERS

### 1. Creating the database and filtering the data

We created a database called `extensions.duckdb` and imported the national ED and planning application datasets using SQL.
The national ED dataset had 3,420 EDs. After filtering for Dublin City 162 EDs remained.
The national planning dataset had 510,984 applications. After selecting Dublin City Council there were 24,879 applications. Filtering for the years 2019 to 2025 reduced this to 23,176. We then searched for the word "extension" in the development descriptions ignoring capital letters and got 9,657 applications.

### 2. Checking CRS and reprojecting

The Dublin City ED dataset has 162 MultiPolygon features. Uses EPSG:2157. The extension application dataset has 9,657 Point features and originally uses EPSG:3857.
We reprojected the application points to EPSG:2157 using `ST_Transform()` in SQL.
Irish Transverse Mercator (EPSG:2157) is better for this analysis because it uses metres and is suitable for calculating areas in Ireland. Web Mercator (EPSG:3857) can distort areas so it is not suitable for calculating application densities.

### 3. Spatial join and counting applications

We used `ST_Within()` to match each extension application point to the ED it falls inside. We used a `LEFT JOIN` so that all 162 EDs would remain in the result even if some had no applications.
The results showed that 14 applications did not match any Dublin City ED boundaries.
This could be because some application points have locations fall outside the boundary area or are exactly on an ED boundary and are not included by `ST_Within()`.

### 4. Calculating extension density

We calculated the area of each ED in kilometres and divided the number of extension applications by its area to get the application density per km².
For example Arran Quay A had a density of 189.30 applications per km² while Arran Quay B had 65.87 applications per km².
Using density makes it easier to compare EDs of sizes because larger EDs may have more applications simply because they cover more area.
The final result contained 162 EDs. Was saved as `DublinED_ExtensionDensity.gpkg`.

### 5. Creating the density map

We created a choropleth map showing extension application density across Dublin City EDs from 2019 to 2025.
We used five classes and the `YlOrRd` colour scheme. Yellow shows areas with application density while dark red shows areas with higher density.
From the map We can see that extension density is not the same across Dublin City. Some EDs have densities than others showing that extension applications are not evenly distributed across Dublin City.
The density values shown on the map range from 1 to 403 applications, per km².
We saved the map as `ExtensionDensity_DublinED.png`.
"""

from pathlib import Path

import numpy as np
import geopandas as gpd
import matplotlib.pyplot as plt
import duckdb


#########################################
##### SETUP #####
#########################################

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUTPUTS = ROOT / "outputs"
OUTPUTS.mkdir(exist_ok=True)

EDS = DATA / "boundaries" / "eds_national.gpkg"
PLANNING = DATA / "planning" / "planning_applications_national.gpkg"

DATABASE = OUTPUTS / "extensions.duckdb"
ED_DENSITY = OUTPUTS / "DublinED_ExtensionDensity.gpkg"
DENSITY_MAP = OUTPUTS / "ExtensionDensity_DublinED.png"

#########################################
##### 1.DATABASE AND FILTERING #####
#########################################

# This step creates a DuckDB spatial database and imports the national ED and planning data.
# We then filter for Dublin City EDs and extension applications from 2019 to 2025 and check the number of records left after each filter.

con = duckdb.connect(str(DATABASE))
con.load_extension("spatial")
con.sql(f"""
    CREATE OR REPLACE TABLE national_eds AS
    SELECT *
    FROM ST_Read('{EDS.as_posix()}')
""")

print("National EDs:")
print(con.sql("""
    SELECT COUNT(*) AS total_eds
    FROM national_eds
"""))

con.sql("""
    CREATE OR REPLACE TABLE eds AS
    SELECT *
    FROM national_eds
    WHERE COUNTY_ENGLISH = 'DUBLIN CITY'
""")

print("Dublin City EDs:")
print(con.sql("""
    SELECT COUNT(*) AS dublin_city_eds
    FROM eds
"""))

con.sql(f"""
    CREATE OR REPLACE TABLE national_planning AS
    SELECT *
    FROM ST_Read('{PLANNING.as_posix()}')
""")

print("National planning applications:")
print(con.sql("""
    SELECT COUNT(*) AS total_applications
    FROM national_planning
"""))

con.sql("""
    CREATE OR REPLACE TABLE dublin_planning AS
    SELECT *
    FROM national_planning
    WHERE PlanningAuthority = 'Dublin City Council'
""")

print("Dublin City Council planning applications:")
print(con.sql("""
    SELECT COUNT(*) AS dublin_applications
    FROM dublin_planning
"""))

con.sql("""
    CREATE OR REPLACE TABLE planning_2019_2025 AS
    SELECT *
    FROM dublin_planning
    WHERE year(ReceivedDate) BETWEEN 2019 AND 2025
""")

print("Planning applications received from 2019 to 2025:")
print(con.sql("""
    SELECT COUNT(*) AS applications_2019_2025
    FROM planning_2019_2025
"""))

con.sql(r"""
    CREATE OR REPLACE TABLE extensions AS
    SELECT *
    FROM planning_2019_2025
    WHERE regexp_matches(
        DevelopmentDescription,
        '(?i)\bextension\b'
    )
""")

print("Extension applications from 2019 to 2025:")
print(con.sql("""
    SELECT COUNT(*) AS total_extensions
    FROM extensions
"""))


#########################################
##### 2.CRS and Reprojection #####
#########################################

# This step checks the CRS, feature count and geometry type of both layers.
# It then reprojects the extension points to Irish Transverse Mercator (EPSG:2157).

print("\nDublin City EDs:")
print(con.sql("DESCRIBE eds"))

print(con.sql("""
    SELECT COUNT(*) AS feature_count,
           ST_GeometryType(FIRST(SHAPE)) AS geometry_type
    FROM eds
"""))

print("\nExtension applications:")
print(con.sql("DESCRIBE extensions"))

planning_columns = con.sql("DESCRIBE extensions").df()["column_name"].tolist()

if "SHAPE" in planning_columns:
    planning_geom = "SHAPE"
elif "geom" in planning_columns:
    planning_geom = "geom"
else:
    raise ValueError("Planning geometry column not found.")

print(con.sql(f"""
    SELECT COUNT(*) AS feature_count,
           ST_GeometryType(FIRST({planning_geom})) AS geometry_type
    FROM extensions
"""))

con.sql(f"""
    CREATE OR REPLACE TABLE extensions_itm AS
    SELECT * EXCLUDE ({planning_geom}),
           ST_Transform(
               {planning_geom},
               'EPSG:3857',
               'EPSG:2157',
               always_xy := true
           ) AS geom
    FROM extensions
""")

print("\nReprojected extension applications:")
print(con.sql("""
    SELECT COUNT(*) AS feature_count,
           ST_GeometryType(FIRST(geom)) AS geometry_type
    FROM extensions_itm
"""))

#########################################
##### 3.SPATIAL JOIN #####
#########################################

# Count extension applications in each ED using a spatial join.
# Identify applications that do not fall within any Dublin City ED.

con.sql("""
    CREATE OR REPLACE TABLE extension_counts AS
    SELECT
        e.ED_GUID,
        COUNT(p.ApplicationNumber) AS extension_count
    FROM eds e
    LEFT JOIN extensions_itm p
        ON ST_Within(p.geom, e.SHAPE)
    GROUP BY e.ED_GUID
""")

print("\nApplications per ED:")
print(con.sql("""
    SELECT *
    FROM extension_counts
    ORDER BY extension_count DESC
"""))

print("\nTotal EDs:")
print(con.sql("""
    SELECT COUNT(*) AS total_eds
    FROM extension_counts
"""))

print("\nApplications outside every ED:")
print(con.sql("""
    SELECT COUNT(*) AS unmatched_applications
    FROM extensions_itm p
    WHERE NOT EXISTS (
        SELECT 1
        FROM eds e
        WHERE ST_Within(p.geom, e.SHAPE)
    )
"""))

#########################################
##### 4. EXTENSION DENSITY #####
#########################################

# Calculate extension applications per km2 for each ED.
# Save the result as a GeoPackage.

df = con.sql("""
    SELECT
        e.ED_GUID,
        e.ED_ENGLISH,
        c.extension_count,
        ST_AsWKB(e.SHAPE) AS wkb
    FROM eds e
    LEFT JOIN extension_counts c
        ON e.ED_GUID = c.ED_GUID
""").df()

eds_map = gpd.GeoDataFrame(
    df.drop(columns="wkb"),
    geometry=gpd.GeoSeries.from_wkb(df["wkb"].apply(bytes)),
    crs="EPSG:2157"
)

eds_map["area_km2"] = eds_map.geometry.area / 1e6

eds_map["extension_density"] = (
    eds_map["extension_count"] / eds_map["area_km2"]
)

eds_map.to_file(ED_DENSITY, driver="GPKG")

print("\nExtension density by ED:")
print(eds_map[[
    "ED_ENGLISH",
    "extension_count",
    "area_km2",
    "extension_density"
]].head(10))

print("\nTotal EDs:", len(eds_map))
print("GeoPackage saved:", ED_DENSITY)

#########################################
##### 5. EXTENSION DENSITY MAP #####
#########################################

# Create a choropleth map of extension density across Dublin City EDs.
# Save the map as a PNG file.

ax = eds_map.plot(
    column="extension_density",
    scheme="Quantiles",
    k=5,
    cmap="YlOrRd",
    edgecolor="grey",
    linewidth=0.3,
    figsize=(7, 6),
    legend=True,
    legend_kwds={
        "title": "Extensions per km2",
        "fmt": "{:.0f}",
        "loc": "lower right"
    }
)

ax.set_title("Extension Application Density by Dublin City ED, 2019-2025")
ax.set_axis_off()

plt.savefig(DENSITY_MAP, dpi=180, bbox_inches="tight")
plt.show()

print("\nDensity map saved:", DENSITY_MAP)

con.close()

## Save outputs with the file names the brief asks for, for example:
## fig.savefig(OUTPUTS / "LISA_TreeDensity_DublinED.png", dpi=200, bbox_inches="tight")
