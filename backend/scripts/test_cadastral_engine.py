import os
import sys

sys.path.insert(
    0,
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    ),
)

from app.api.cadastral_real import (
    AREA_TOLERANCE_PERCENT,
    BOUNDARY_TOLERANCE_METERS,
    MATCH_OVERLAP_PERCENT,
    OVERLAP_TOLERANCE_PERCENT,
)

print("HELIOS-LAND cadastral engine")
print("--------------------------------")
print("Area tolerance:", AREA_TOLERANCE_PERCENT, "%")
print("Boundary tolerance:", BOUNDARY_TOLERANCE_METERS, "m")
print("Overlap tolerance:", OVERLAP_TOLERANCE_PERCENT, "%")
print("Match threshold:", MATCH_OVERLAP_PERCENT, "%")

from shapely.geometry import Polygon

old = Polygon([(0, 0), (40, 0), (40, 30), (0, 30)])
new = Polygon([(1, 0), (41, 0), (41, 30), (1, 30)])

print("\nGeometry sanity test:")
print("Old area:", old.area)
print("New area:", new.area)

intersection = old.intersection(new)
union = old.union(new)

print("Intersection:", intersection.area)
print("Union:", union.area)
print("Overlap:", intersection.area / union.area * 100, "%")
print("Centroid shift:", old.centroid.distance(new.centroid), "m")
print("\nPASS: GIS engine imports and runs.")
