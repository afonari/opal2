#!/bin/env python
#
# tests requiring dprepro calls.
#
# will not run if dprepro not installed or not in path
import os
import sys
sys.path.append('.')
import shutil
import tools_for_tests
import analysis_driver

# directory of test input files
test_inputs_dir = os.path.join(tools_for_tests.test_dir, 'test_inputs_dprepro')

def test_preprocess_pseudopotential_input_files():
    """
    
    """
    with tools_for_tests.TemporaryDirectory() as tmp_dir:
        # preprocess files
        element_list = ['Si', 'Ge']
        shutil.copyfile(os.path.join(test_inputs_dir, 'params.example'), 
                        os.path.join(os.getcwd(), 'params'))
        analysis_driver.preprocess_pseudopotential_input_files(element_list, test_inputs_dir)

        # compare with correct ouptut
        correct_Si_file = os.path.join(test_inputs_dir, 'Si.in.correct')
        with open(correct_Si_file) as f1, open('Si.in') as f2:
            assert f1.readlines() == f2.readlines()
        correct_Ge_file = os.path.join(test_inputs_dir, 'Ge.in.correct')
        with open(correct_Ge_file) as f1, open('Ge.in') as f2:
            assert f1.readlines() == f2.readlines()
