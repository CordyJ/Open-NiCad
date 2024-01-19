# -*- coding: utf-8 -*-

# Copyright (c) 2009 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a function to compile all user interface files of a
directory or directory tree.
"""

import os

def compileUiFiles(dir, recurse = False):
    """
    Module function to compile the .ui files of a directory tree to Python sources.
    
    @param dir name of a directory to scan for .ui files (string or QString)
    @param recurse flag indicating to recurse into subdirectories (boolean)
    """
    try:
        from PyQt4.uic import compileUiDir
    except ImportError:
        from PyQt4.uic import compileUi
        
        def compileUiDir(dir, recurse = False, map = None, **compileUi_args):
            """
            Creates Python modules from Qt Designer .ui files in a directory or
            directory tree.
            
            Note: This function is a modified version of the one found in PyQt4.

            @param dir Name of the directory to scan for files whose name ends with
                '.ui'. By default the generated Python module is created in the same
                directory ending with '.py'.
            @param recurse flag indicating that any sub-directories should be scanned.
            @param map an optional callable that is passed the name of the directory
                containing the '.ui' file and the name of the Python module that will be
                created. The callable should return a tuple of the name of the directory
                in which the Python module will be created and the (possibly modified)
                name of the module.
            @param compileUi_args any additional keyword arguments that are passed to
                the compileUi() function that is called to create each Python module.
            """
            def compile_ui(ui_dir, ui_file):
                """
                Local function to compile a single .ui file.
                
                @param ui_dir directory containing the .ui file (string)
                @param ui_file file name of the .ui file (string)
                """
                # Ignore if it doesn't seem to be a .ui file.
                if ui_file.endswith('.ui'):
                    py_dir = ui_dir
                    py_file = ui_file[:-3] + '.py'

                    # Allow the caller to change the name of the .py file or generate
                    # it in a different directory.
                    if map is not None:
                        py_dir, py_file = map(py_dir, py_file)

                    # Make sure the destination directory exists.
                    try:
                        os.makedirs(py_dir)
                    except:
                        pass

                    ui_path = os.path.join(ui_dir, ui_file)
                    py_path = os.path.join(py_dir, py_file)

                    ui_file = open(ui_path, 'r')
                    py_file = open(py_path, 'w')

                    try:
                        compileUi(ui_file, py_file, **compileUi_args)
                    finally:
                        ui_file.close()
                        py_file.close()

            if recurse:
                for root, _, files in os.walk(dir):
                    for ui in files:
                        compile_ui(root, ui)
            else:
                for ui in os.listdir(dir):
                    if os.path.isfile(os.path.join(dir, ui)):
                        compile_ui(dir, ui)

    def pyName(py_dir, py_file):
        """
        Local function to create the Python source file name for the compiled .ui file.
        
        @param py_dir suggested name of the directory (string)
        @param py_file suggested name for the compile source file (string)
        @return tuple of directory name (string) and source file name (string)
        """
        return py_dir, "Ui_%s" % py_file
    
    compileUiDir(dir, recurse, pyName)
