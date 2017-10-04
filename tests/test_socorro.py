#!/bin/env python
#
# tests requiring Socorro calls.
#
# will not run if socorro not installed
# integration test of single socorro dft run, including 
# preprocessing files, running socorro, post processing results
# and writing results

import os
import shutil
import eval_pp
import numpy as np

main_dir = os.getcwd()  # test called from this directory
tests_dir = main_dir + '/tests'  # directory containings test scripts
test_inputs_dir = tests_dir + '/test_inputs_socorro' # directory of test input files
 
def test_run_socorro():
    """
    test: setup_dir method makes files for socorro run

    Expected behavior: calling setup_dir method will create correctly
    preprocessed argvf file in current directory, directory named data/
    and correctly preprocessed data/crystal file.

    note: this might fail if socorro versions change because different
    versions could give different reults even with the same input,
    especially since total E is relative. Could I mock socorro instead?
    Alternatively, I could run socorro twice, the second time with pre-
    setup input files, and compare results
    """
    tmp_dir = tests_dir + '/tmp_socorro_run'
    inputs = test_inputs_dir + '/SiGe_single_run'
    try:
        os.mkdir(tmp_dir)
        os.chdir(tmp_dir)
        # create object to test
        pp_path_list = [inputs+'/PAW.Si',
                        inputs+'/PAW.Ge']
        argvf_template_path = inputs+'/argvf.template'
        crystal_template_path = inputs+'/crystal.template'
        pos = [[0.0, 0, '0.1'], [0.24, 0.25, 0.26]]
        testrun = eval_pp.DftRun(pp_path_list, argvf_template_path,
                                 crystal_template_path, pos, 10.)
        testrun.setup_files()
        with open('socorro.log', 'w') as fout:
            p = testrun.run_socorro(fout)
        p.wait()

        #assert force and energy reults
        correct_energy = -312.593586340
        correct_forces = np.array([[0.246519, 0.247743, 0.243064],
                                  [-0.246519, -0.247743, -0.243064]])
        assert testrun.read_energy() == correct_energy
        assert np.isclose(testrun.read_forces(), correct_forces).all()
    finally:
        os.chdir(main_dir)
        shutil.rmtree(tmp_dir)


def test_position_sweep():
    """ 
    runs four instances of socorro in parallel. compares results to
    correct results
    """
    raise Exception('implement me')


# SiGe_moga
#   5.293267755
#       1.0  1.0  0.0
#       0.0  1.0  1.0
#       1.0  0.0  1.0
# lattice
#   2
# Si    0.0  0.0  0.0
# Ge    0.25 0.25 0.25
