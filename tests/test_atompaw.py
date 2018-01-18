#!/bin/env python
#
# tests requiring Atompaw calls.
#
# will not run if Atopmaw not installed

import os
import sys
sys.path.append('.')
import shutil
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


def test_create_pseudopotentials():
    """
    Run in a directory with multiple atompaw input files, builds each PAW
    in its own directory.

    Compares created PAW to a correct pseudopotential.

    Assumes atompaw v4 right now. I can generalize this later if needed,
    or just check that atompaw is called and not that the output is correct.
    This test is fragile because output can easily change between atompaw 
    versions.
    """
    with tools_for_tests.TemporaryDirectory() as tmp_dir:
        shutil.copy(os.path.join(test_inputs_dir, 'Si.in'), os.getcwd())
        shutil.copy(os.path.join(test_inputs_dir, 'Ge.in'), os.getcwd())
        element_list = ['Si', 'Ge']
        analysis_driver.create_pseudopotentials(element_list)
        
        Si_file_correct = os.path.join(test_inputs_dir, 'PAW.Si.correct')
        with open(Si_file_correct) as f1, open('PAW.Si') as f2:
            assert f1.read() == f2.read()
        Ge_file_correct = os.path.join(test_inputs_dir, 'PAW.Ge.correct')
        with open(Ge_file_correct) as f1, open('PAW.Ge') as f2:
            assert f1.read() == f2.read()
        
    
def test_is_pseudopotential_converged_good():
    """
    case where atompaw creates PAW successfully
    """
    good_log = os.path.join(test_inputs_dir, 'log.good')
    assert analysis_driver.is_pseudopotential_converged(good_log) is True

def test_is_pseudopotential_converged_no_convergence():
    """
    case where atompaw does not converge
    """
    no_converge_log = os.path.join(test_inputs_dir, 'log.noconverge')
    assert analysis_driver.is_pseudopotential_converged(no_converge_log) is False


"""
test cases:

bad input (non_convergence)...need to dig through old runs for this
sweep of different elements
bad case of RCs? do this later (add github issue, or keep ISSUES list)
"""
