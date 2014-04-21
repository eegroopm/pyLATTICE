# define authorship information
__authors__     = ['Evan Groopman', 'Thomas Bernatowicz']
__author__      = ','.join(__authors__)
__credits__     = []
__copyright__   = 'Copyright (c) 2012'
__license__     = 'GPL'

# maintanence information
__maintainer__  = 'Evan Groopman'
__email__       = 'eegroopm@gmail.com'

# define version information
__version_info__    = (0, 2,10)
__version__         = 'v%i.%01i.%03i' % __version_info__
__revision__        = __version__

"""
Changelog:
v0.2.10 - 3/6/2014
- Added popup IPython console for interacting with data

v0.2 - 2/18/2014:
- Added mineral database.
- Rewrote how special space group conditions are processed.
    Now, dspace calculates only general conditions.
    Afterwards, RemoveForbidden() parses if statements and drops invalid spots from dataframe
- Dropped spots are saved in self.Forbidden. Can be plotted with rest of pattern!
- Compiled linux binaries work for 32- and 64-bit Python 2.7 AND 3.3.
    Still an issue with Windows 64-bit and 3.3


v0.1
v.20140209
- Upgrade DSpace calculating function to Cython for speed enhancements - 35-75% speed increase! With rewriting function a bit.
- Change SpaceGroup conditions to modular arithmetic instead of having n in a loop
    e.g. (h + k +l)%2 == 0 instead of h+k+l == 2*n
- To implement: rotating diff pattern w/o recalculating

v.20140203
- Update to Python3.3.2
- Replace recordarray with pandas DataFrame
- Attempt to fix angle plotting bug w/ hexagonal crystals

v.20120927
-Changing from guiqwt to matplotlib for plotting.
Despite efficiency of guiqwt, matplotlib has more support and many more functions.
"""

import os.path

from PyQt4 import QtCore, uic
#from PySide import QtCore, QtUiTools

def loadUi( modpath, widget ):
    """
    Uses the PyQt4.uic.loadUI method to load the inputed ui file associated
    with the given module path and widget class information on the inputed
    widget.
    
    :param      modpath | str
    :param      widget  | QWidget
    """
    # generate the uifile path
    basepath = os.path.dirname(modpath)
    basename = widget.__class__.__name__
    #basename = 'pyLATTICE_GUI_devel'
    #need new path for windows compiled executable with shared library
    d,parent = os.path.split(basepath) #parent directory
    if parent == 'resources':
        basepath = os.path.join(d,'gui')
    dnew = os.path.split(d)
    if dnew[1] == 'library.zip':
        basepath = os.path.join(dnew[0],'gui')
    uifile   = os.path.join(basepath, 'ui' + os.sep + '%s.ui' % basename)
    uipath   = os.path.dirname(uifile)
    
    # swap the current path to use the ui file's path
    currdir = QtCore.QDir.currentPath()
    QtCore.QDir.setCurrent(uipath)
    
    # load the ui
    uic.loadUi(uifile, widget)
#    loader = QtUiTools.QUiLoader()
#    file = QtCore.QFile(uifile)
#    loader.load(file, widget)
    
    # reset the current QDir path
    QtCore.QDir.setCurrent(currdir)