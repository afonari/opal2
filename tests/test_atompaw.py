#!/bin/env python
#
# tests requiring Atompaw calls.
#
# will not run if Atopmaw not installed

import os
import sys
sys.path.append('.')
#import shutil
#import numpy as np
import tools_for_tests
import analysis_driver

# directory of test input files
test_inputs_dir = os.path.join(tools_for_tests.test_dir, 'test_inputs_atompaw')

def test_run_atompaw():
    """
    create single pseudopotential in current directory

    Assumes atompaw v4 right now. I can generalize this later if needed,
    or just check that atompaw is called and not that the output is correct.
    This test is fragile because output can easily change between atompaw 
    versions.
    """
    with tools_for_tests.TemporaryDirectory() as tmp_dir:
        input_file_name = os.path.join(test_inputs_dir, 'Si.in.example')
        analysis_driver.run_atompaw(input_file_name)
        correct_file = os.path.join(test_inputs_dir, 'Si.SOCORRO.atomicdata.correct')
        with open(correct_file) as f1, open('Si.SOCORRO.atomicdata') as f2:
            assert f1.read() == f2.read()
