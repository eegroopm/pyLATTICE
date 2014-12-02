pyLATTICE
=========

pyLATTICE is a program written in Python and PyQt for calculating and plotting electron diffraction patterns from any homogeneous material.

Dependencies
____________

pyLATTICE requires a number of dependencies. Below are the development versions for each dependency, though earlier versions may also work.

- Python 2.7 - 3.4
- PyQt 4.10.3 - 4.10.4
- Cython 0.19.1
- h5py 2.2.1
- lxml 3.3.0
- matplotlib 1.3.1
- numexpr 2.0
- numpy 1.8.0
- openpyxl 1.8.5
- pandas 0.13.1
- six 1.5.2
- tables 3.0.0
- xlwt 0.7.5

Usage
_____

Running from source:

python main.py

_____
To calculate D-spacings:

Select the desired crystal type from dropdown menus.The user may select crystal geometry, unit cell type, and (optionally) a specific space group. For the desired crystal type the user may then choose lattice parameters. The lattice parameters and angles are constrained by the crystal geometry. The calculate direct lattice and reciprocal lattice metric tensors are shown in the 'd-spacings' tab, along with the calculated d-spacings for a given range of Miller indices.

To plot:
To plot diffraction patterns, the user must select 'only N=0 Laue zones' (default on). From there the user may select the zone axis [uvw] from the spinboxes. The plotted diffraction pattern will appear in the 'Diffraction Pattern' tab. Diffraction spots are are pickable for measuring distances/angles. Labels may be toggled on and off (lower right on toolbar) and the pattern may be rotated. The main plot label is also draggable. The user may also toggle on/off plotting forbidden reflections (if any) for the diffraction patterns.

Minerals:
Specific minerals may be saved/loaded from a database for easy access and reproducability.

IPython Console:
An IPython console is implemented allowing for the user to interact with the d-spacing data and metric tensors (limited variables so far).

Optional:
______
To compile your own dspace and diffspot C-extensions, use the Csetup.py script in the resources folder. On Linux this will compile a .so file; on Windows this will compile a .pyd file. Compiled C-extensions are Python-version-dependent, so each new platform will require its own compiled copy. 

For instance, on Linux, compiling _dspace.pyx will create a file dspace.so for Python 2.7, dspace.cpython-33m.so for Python 3.3, and dspace.cpython-34m.so for Python 3.4.

To compile, simply change the extension name in Csetup.py to "dspace" or "diffspot" and the filename in brackets [] to "_dspace" or "_diffspot", respectively. Run:

python Csetup.py build_ext --inplace
