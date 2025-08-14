# Rhino Single Hull Line v1 — Ra'anan Ynze de Jong — 2025

import rhinoscriptsyntax as rs
import scriptcontext as sc
import Rhino
import System.Drawing
import time

def ensure_layer(name, color_rgb):
    """Create layer with specified color if it doesn't exist."""
    if not rs.IsLayer(name):
        rs.AddLayer(name, color_rgb)
    rs.CurrentLayer(name)

def slice_single_contour(hull_id, axis, position_mm, layer_name, color_rgb):
    """Slice hull at a single absolute position and project the result."""
    hull = rs.coercebrep(hull_id)
    if not hull: return

    position_model = rs.UnitScale(Rhino.UnitSystem.Millimeters, rs.UnitSystem()) * position_mm

    idx = {'X':0, 'Y':1, 'Z':2}[axis]

    dir_vector = Rhino.Geometry.Vector3d(0,0,0)
    dir_vector[idx] = 1

    base_point = [0.0, 0.0, 0.0]
    base_point[idx] = position_model
    pt = Rhino.Geometry.Point3d(*base_point)
    plane = Rhino.Geometry.Plane(pt, dir_vector)

    start_time = time.time()
    section = Rhino.Geometry.Brep.CreateContourCurves(hull, plane)
    if not section:
        print("No intersection found at this position.")
        return

    ensure_layer(layer_name, System.Drawing.Color.FromArgb(*color_rgb))

    count = 0
    for crv in section:
        origin = Rhino.Geometry.Point3d(0,0,0)
        origin[idx] = crv.PointAtStart[idx]
        normal = Rhino.Geometry.Vector3d(0,0,0)
        normal[idx] = 1
        local_plane = Rhino.Geometry.Plane(origin, normal)

        projected = Rhino.Geometry.Curve.ProjectToPlane(crv, local_plane)
        if projected:
            attr = Rhino.DocObjects.ObjectAttributes()
            attr.LayerIndex = sc.doc.Layers.Find(layer_name, True)
            attr.ObjectColor = System.Drawing.Color.FromArgb(*color_rgb)
            attr.ColorSource = Rhino.DocObjects.ObjectColorSource.ColorFromObject
            sc.doc.Objects.AddCurve(projected, attr)
            count += 1
            print(f"✅ Added line at {round(position_mm, 2)} mm")

    sc.doc.Views.Redraw()
    Rhino.RhinoApp.Wait()
    print(f"Completed in {round(time.time() - start_time, 2)} seconds — {count} curves added.")

# Select hull polysurfaces
print("Select hulls to section, press ENTER when ready...")
object_ids = rs.GetObjects(
    "Select one or more hulls (polysurfaces) for slicing",
    filter=rs.filter.polysurface,
    group=True
)
if not object_ids:
    print("No objects selected. Exiting.")
    exit()

# Choose axis and absolute position
axis = rs.GetString("Choose :", "Stations [X] : Buttocks [Y] : Waterlines [Z]", ["X", "Y", "Z"])
if not axis: exit()

position_mm = rs.GetReal("Enter absolute slice position in millimeters", 1000.0, -100000.0, 100000.0)
if position_mm is None: exit()

# Axis-specific layer and color
color_map = {
    'X': ("Stations", (255, 0, 0)),     # Red
    'Y': ("Buttocks", (0, 255, 0)),     # Green
    'Z': ("Waterlines", (0, 0, 255))    # Blue
}

suffix, color_rgb = color_map[axis]

for obj_id in object_ids:
    obj_name = rs.ObjectName(obj_id) or "Hull"
    layer_name = f"{obj_name} {suffix}"
    print(f"Processing: {obj_name}")
    slice_single_contour(obj_id, axis, position_mm, layer_name, color_rgb)
    print("Single slice complete.\n")#! python 3
