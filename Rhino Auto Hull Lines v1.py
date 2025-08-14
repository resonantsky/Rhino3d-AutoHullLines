# Rhino AutoHullLines v1 — Ra'anan Ynze de Jong — 2025

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

def update_status(current, total):
    """Update progress meter and print status."""
    rs.StatusBarProgressMeterUpdate(current)
    percent = int((current / total) * 100)
    print(f"Sectioning: {percent}% ({current}/{total})")

def get_symmetric_slice_positions(bbox, idx, step_pos, step_neg, axis):
    """Generate symmetrical slice positions from centerline outward."""
    max_pos = bbox.Max[idx]
    max_neg = bbox.Min[idx]

    extent_pos = rs.GetReal(f"Maximum positive extent from {axis}=0", max_pos, 0.0, max_pos)
    extent_neg = rs.GetReal(f"Maximum negative extent from {axis}=0", abs(max_neg), 0.0, abs(max_neg))
    if extent_pos is None or extent_neg is None:
        print("Invalid extents.")
        return []

    slice_positions = []
    val = 0.0
    while val <= extent_pos:
        slice_positions.append(val)
        val += step_pos

    val = step_neg
    while val <= extent_neg:
        slice_positions.append(-val)
        val += step_neg

    slice_positions.sort()
    return slice_positions

def get_linear_slice_positions(bbox, idx, step_model, axis):
    """Generate linear slice positions from min to max."""
    min_val = bbox.Min[idx]
    max_val = bbox.Max[idx]
    min_val = rs.GetReal(f"Start slicing {axis}-axis from", min_val, min_val, max_val)
    max_val = rs.GetReal(f"End slicing {axis}-axis at", max_val, min_val, max_val)
    if min_val is None or max_val is None or max_val <= min_val:
        print("Invalid range.")
        return []

    slice_positions = []
    val = min_val
    while val <= max_val:
        slice_positions.append(val)
        val += step_model

    return slice_positions

def slice_with_contours(hull_id, axis, step_mm, layer_name, color_rgb):
    """Slice hull along axis, project curves, and update status per line."""
    hull = rs.coercebrep(hull_id)
    if not hull: return

    step_model = rs.UnitScale(Rhino.UnitSystem.Millimeters, rs.UnitSystem()) * step_mm
    if step_model <= 0:
        print("Invalid offset size.")
        return

    bbox = hull.GetBoundingBox(True)
    idx = {'X':0, 'Y':1, 'Z':2}[axis]

    # Axis-specific slicing logic
    if axis == 'Y':
        slice_positions = get_symmetric_slice_positions(bbox, idx, step_model, step_model, axis)
    elif axis == 'Z':
        step_pos = rs.GetReal("Enter positive Z spacing (mm)", step_mm, 1.0, 10000.0)
        step_neg = rs.GetReal("Enter negative Z spacing (mm)", step_pos, 1.0, 10000.0)
        step_pos_model = rs.UnitScale(Rhino.UnitSystem.Millimeters, rs.UnitSystem()) * step_pos
        step_neg_model = rs.UnitScale(Rhino.UnitSystem.Millimeters, rs.UnitSystem()) * step_neg
        slice_positions = get_symmetric_slice_positions(bbox, idx, step_pos_model, step_neg_model, axis)
    else:
        slice_positions = get_linear_slice_positions(bbox, idx, step_model, axis)

    total_slices = len(slice_positions)
    if total_slices == 0:
        print("No lines to generate.")
        return

    dir_vector = Rhino.Geometry.Vector3d(0,0,0)
    dir_vector[idx] = 1

    contours = []
    start_time = time.time()

    for i, val in enumerate(slice_positions):
        base_point = [0.0, 0.0, 0.0]
        base_point[idx] = val
        pt = Rhino.Geometry.Point3d(*base_point)
        plane = Rhino.Geometry.Plane(pt, dir_vector)

        section = Rhino.Geometry.Brep.CreateContourCurves(hull, plane)
        if section:
            contours.extend(section)

        update_status(i + 1, total_slices)
        Rhino.RhinoApp.Wait()

    rs.StatusBarProgressMeterHide()
    print(f"Projection completed in {round(time.time() - start_time, 2)} seconds")

    ensure_layer(layer_name, System.Drawing.Color.FromArgb(*color_rgb))

    for crv in contours:
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

    sc.doc.Views.Redraw()
    Rhino.RhinoApp.Wait()

# Select hull polysurface
print("Select hulls to section, press ENTER when ready...")
object_ids = rs.GetObjects(
    "Select one or more hulls (polysurfaces) for slicing",
    filter=rs.filter.polysurface,
    group=True
)
if not object_ids:
    print("No objects selected. Exiting.")
    exit()

# Choose axis and step interactively
axis = rs.GetString("Choose :", "Stations [X] : Buttocks [Y] : Waterlines [Z]", ["X", "Y", "Z"])
if not axis: exit()

step_mm = rs.GetReal("Enter default datum in millimeters", 1000.0, 1.0, 10000.0)
if step_mm is None: exit()

# Axis-specific layer and color
color_map = {
    'X': ("Stations", (255, 0, 0)),     # Red
    'Y': ("Buttocks", (0, 255, 0)),     # Green
    'Z': ("Waterlines", (0, 0, 255))    # Blue
}

layer_name, color_rgb = color_map[axis]
for obj_id in object_ids:
    print(f"Processing: {rs.ObjectName(obj_id) or 'Unnamed Polysurface'}")
    slice_with_contours(obj_id, axis, step_mm, layer_name, color_rgb)
    print("Hull lines generation complete!")
