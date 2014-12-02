#!/usr/bin/env python3
#-*- coding: utf-8 -*-
""" 
pyLATTICE is...
"""

# define authorship information
__authors__     = ['Evan Groopman', 'Thomas Bernatowicz']
__author__      = ','.join(__authors__)
__credits__     = []
__copyright__   = 'Copyright (c) 2011-2014'
__license__     = 'GPL'

# maintanence information
__maintainer__  = 'Evan Groopman'
__email__       = 'eegroopm@gmail.com'

import sys
if sys.version_info[0] == 3:
    import sip
    sip.setapi("QString", 2)
    sip.setapi("QVariant", 2)
from PyQt4 import QtGui

def main(argv = None):
    """
    Creates the main window for the nexsys application and begins the \
    QApplication if necessary.
    
    :param      argv | [, ..] || None
    
    :return      error code
    """
    app = None
    
    # create the application if necessary
    if ( not QtGui.QApplication.instance() ):
        app = QtGui.QApplication(sys.argv)
        app.setStyle('cleanlooks')
        font = QtGui.QFont('Arial Unicode MS')
        #font = QtGui.QFont('Times')
        app.setFont(font)
    
    # create the main window
    from gui.pyLATTICE import pyLATTICE_GUI
    window = pyLATTICE_GUI()
    window.show()
    
    
    # run the application if necessary
    if ( app ):
        return app.exec_()


if __name__ == "__main__":
    import sys
    sys.exit(main(sys.argv))
