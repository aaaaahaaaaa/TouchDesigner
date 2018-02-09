# SOP to SVG
Convert SOPs to SVG files.

## Dependencies
The component depends on the `svgwrite` package: https://pypi.python.org/pypi/svgwrite/

Check [Derivative's documentation](http://www.derivative.ca/wiki088/index.php?title=Introduction_to_Python_Tutorial#Importing_Modules) to install external Python packages.

## Features
* Supports SOPS composed of meshes or polygons.
* Projects 3D coordinates in 2D either using a CameraCOMP's internal projection matrix or by applying a 2D offset (offset `x` and `y` by a ratio of `z`).
* Configure canva size, margins and units.
* Auto scale to fit the canva and margins.
