#!/usr/bin/env python
import os
import shutil
import tempfile

main_dir = os.getcwd()
test_dir = os.path.join(main_dir, 'tests')  # main test directory

class TemporaryDirectory(object):
    """
    Context manager for tempfile.mkdtemp() so it's usable with 'with' statement.
    This version automatically changes to and leaves temporary directory.
    
    This is needed in case of python 2. In python 3, there is already a 
    tempfile.TemporaryDirectory.
    """
    def __enter__(self):
        self.start_dir = os.getcwd()
        self.name = tempfile.mkdtemp(dir=main_dir)
        os.chdir(self.name)
        return self.name

    def __exit__(self, exc_type, exc_value, traceback):
        os.chdir(self.start_dir)
        shutil.rmtree(self.name)
