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
    min_val = bbox.Min[idx]
    max_val = bbox.Max[idx]

    min_val = rs.GetReal(f"Start slicing {axis}-axis from", min_val, min_val, max_val)
    max_val = rs.GetReal(f"End slicing {axis}-axis at", max_val, min_val, max_val)
    if min_val is None or max_val is None or max_val <= min_val:
        print("Invalid range.")
        return

    slice_positions = []
    val = min_val
    while val <= max_val:
        slice_positions.append(val)
        val += step_model

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

        #rs.StatusBarProgressMeterShow(f"Slicing {axis}-axis...", total_slices, True)
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

# 🛠️ Select hull polysurface
hull_id = rs.GetObject("Select Hull polysurface", rs.filter.polysurface)
if not hull_id: exit()

# 🎛️ Choose axis and step interactively
axis = rs.GetString("Choose :", "Stations [X] : Buttocks [Y] : Waterlines [Z]", ["X", "Y", "Z"])
if not axis: exit()

step_mm = rs.GetReal("Enter datum in millimeters", 1000.0, 1.0, 10000.0)
if step_mm is None: exit()

# 🎨 Axis-specific layer and color
color_map = {
    'X': ("Stations", (255, 0, 0)),     # Red
    'Y': ("Buttocks", (0, 255, 0)),     # Green
    'Z': ("Waterlines", (0, 0, 255))    # Blue
}

layer_name, color_rgb = color_map[axis]
slice_with_contours(hull_id, axis, step_mm, layer_name, color_rgb)