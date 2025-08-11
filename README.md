# 🧭 Rhino3d AutoHullLines - Hull Sectioning Tool - v1

A Rhino Python script for slicing hull geometries into clean sectional contours—commonly referred to as Hull Lines, Waterlines, Stations, and Buttocks.

This script allows you to project any form using metric fractions of the world origin and model boundaries, generating arrays of 3D parametric curves that define the contours.

## ✨ Features

🔹 Multi-object selection: Project multiple bodies in one go.

🔹 Modular axis control: Choose slicing direction (X, Y, or Z)

🔹 Dynamic layer naming: Auto-generates layers per hull and axis

🔹 Incremental feedback: Console-driven progress for each hull.

## 🚀 Usage

1. Open Rhino and run the script via Python (`EditPythonScript`)
2. Select one or more polysurfaces
3. Choose slicing axis and step size in millimeters
4. Watch contours populate in named layers

## 🧩 Requirements

- Rhino 6 or later
- Python scripting enabled (`rhinoscriptsyntax`)
