#!/bin/env python
#
# tests requiring Socorro calls.
#
# will not run if socorro not installed
# integration test of single socorro dft run, including 
# preprocessing files, running socorro, post processing results
# and writing results

import os
import sys
sys.path.append('.')
import shutil
import eval_pp
import numpy as np
import tools_for_tests

# directory of test input files
test_inputs_dir = os.path.join(tools_for_tests.test_dir, 'test_inputs_socorro')

def test_run_socorro():
    """
    Set up socorro input files, run socorro, check force/energy results

    note: this might fail if socorro versions change because different
    versions could give different reults even with the same input,
    especially since total E is relative. Could I mock socorro instead?
    Alternatively, I could run socorro twice, the second time with pre-
    setup input files, and compare results
    """
    inputs = test_inputs_dir + '/SiGe_single_run'
    with tools_for_tests.TemporaryDirectory() as tmp_dir:
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
        assert np.isclose(testrun.read_energy(), correct_energy)
        assert np.isclose(testrun.read_forces(), correct_forces, atol=1.e-5).all()


def test_position_sweep():
    """
    Four instances of socorro run in parallel, results correct

    Sets up four DftRun instances with different atomic coordinates.
    The socorro runs should run simulataneously in different threads.

    note: this might fail if socorro versions change because different
    versions could give different reults even with the same input,
    especially since total E is relative. Could I mock socorro instead?
    Alternatively, I could run socorro twice, the second time with pre-
    setup input files, and compare results
    """
    inputs = test_inputs_dir + '/SiGe_single_run'
    with tools_for_tests.TemporaryDirectory() as tmp_dir:
        positions = [[[0.0, 0.0, 0.1], [0.24, 0.25, 0.26]],
                     [[0.0, 0.0, 0.0], [0.50, 0.50, 0.50]],
                     [[0.0, 0.0, 0.0], [0.25, 0.25, 0.25]],
                     [[0.1, 0.0, 0.0], [0.49, 0.50, 0.51]]]

        # create objects to test
        pp_path_list = [inputs+'/PAW.Si', inputs+'/PAW.Ge']
        argvf_template_path = inputs+'/argvf.template'
        crystal_template_path = inputs+'/crystal.template'
        testruns = []
        for pos in positions:
            testruns.append( eval_pp.DftRun(pp_path_list, argvf_template_path,
                                            crystal_template_path, pos, 10.) )

        # run position_sweep
        eval_pp.position_sweep(testruns)

        # get results from socorro runs
        energies = []
        forces = []
        for run in testruns:
            # get results and append to results array
            os.chdir(run.run_dir) 
            energies.append( run.read_energy() )
            forces.append( run.read_forces() )
            os.chdir(tmp_dir)

        # correct results
        correct_en = [-312.593586340, -311.879456794, -312.474999793, -312.000747628]
        correct_forces = [ np.array([[+0.246519, +0.247743, +0.243064],
                                     [-0.246519, -0.247743, -0.243064]]),
                           np.array([[-0.000000, -0.000000, -0.000000],
                                     [+0.000000, +0.000000, +0.000000]]),
                           np.array([[-0.000000, +0.000000, -0.000000],
                                     [+0.000000, -0.000000, +0.000000]]),
                           np.array([[+0.157293, +0.169207, -0.024752],
                                     [-0.157293, -0.169207, +0.024752]]) ]

        assert np.isclose(energies, correct_en).all()
        assert np.isclose(forces, correct_forces, atol=1.e-5).all()
