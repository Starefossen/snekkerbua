# Alcove-Style Bunk Bed Frame

This project contains a Python script using the `build123d` library to programmatically generate a 3D model of an alcove-style bunk bed frame and export it as a STEP file.

## Setup & Usage

This project uses `mise` for environment management and task running. 

1. Ensure you have `mise` installed.
2. In your terminal, navigate to this directory.
3. You can now use the built-in mise tasks to run the project.

To see available tasks:
```bash
mise run
```

### Available Tasks:

* **Install dependencies** (run automatically when building):
  ```bash
  mise run install
  ```
* **Generate the 3D models** (`.step`, `.stl`, `.glb`):
  ```bash
  mise run build
  ```
* **Preview the model natively on macOS**:
  ```bash
  mise run view
  ```

## Viewing the `.step` File

A STEP (`.step` or `.stp`) file is a standard 3D CAD file format. To view it on your Mac, you can use any of the following options:

1. **FreeCAD** (Recommended for Engineering): 
   A free, powerful, open-source 3D CAD modeler. You can download it at [freecad.org](https://www.freecad.org/) or install it via Homebrew (`brew install --cask freecad`). Once installed, open FreeCAD and simply go to `File > Open` and select the `bed_frame.step` file.

2. **Visual Studio Code**:
   If you use VS Code, you can install the **OCP CAD Viewer** extension. This allows you to view STEP files right inside your code editor.

3. **Online Viewers** (No installation required):
   You can drag and drop your `.step` file into a free online viewer, such as:
   - [3DViewerOnline](https://www.3dvieweronline.com/)
   - [CAD Exchanger](https://cadexchanger.com/view/)

4. **eDrawings Viewer for Mac**:
   A free dedicated desktop application from Dassault Systèmes for viewing 3D CAD files.
