#!/usr/bin/env python
import sys
sys.path.append('.')
import os
import shutil
import eval_pp
import wrapper_pp
import numpy as np
import tools_for_tests
from tools_for_tests import test_inputs_dir

def isclose(a, b, rel_tol=1e-9, abs_tol=0.0):
    """
    for comparing floats to double precision
    """
    return abs(a-b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)

def test_write_results(tmpdir):
    """ writes objectives of 100, 100 to file, checks output """
    wrapper_pp.write_results_file({'accu': 100, 'work': 101})
    with open('results') as f:
        results_output = f.readlines()
    os.remove('results')
    assert map(str.strip, results_output) == ['100 accu_obj', '101 work_obj']


def test_preproc_argvf():
    """ make sure {gcut} and {4gcut} are replaced in text correctly """
    gcut = 40.
    example_template = 'tests/test_inputs/argvf.template.example1'
    testrun = eval_pp.DftRun([], example_template, '', [], gcut)
    with open(example_template) as fin:
        tmplt_txt = fin.readlines()
    assert testrun._preproc_argvf(tmplt_txt) == ['asdfsd\n', 
     'asdf 40.0\n', 'asdfas 160.0\n', '\n', '\n', 'lkjlj\n']


def test_preproc_crystal():
    """ check crystal coordinates placed in text correctly 
    would be better to add a couple more test cases
    """
    pos = [[0.0, 0, '0.1'], [0.5, 0.6, 0.7]]
    example_template = 'tests/test_inputs/crystal.template.example1'
    with open(example_template) as fin:
        tmplt_txt = fin.readlines()
    preprocessed_txt = eval_pp.DftRun._preproc_crystal(tmplt_txt, pos)
    assert map(str.split, preprocessed_txt) == [['Si_moga'], 
     ['5.169458407'], 
     ['1.0', '1.0', '0.0'], 
     ['0.0', '1.0', '1.0'], 
     ['1.0', '0.0', '1.0'], 
     ['lattice'], 
     ['2'], 
     ['Si', '0.0', '0.0', '0.1'], 
     ['Si', '0.5', '0.6', '0.7']]


def test_symlink_pseudopotentials():
    """
    symlinks pseudopotentials into data/ directory and compares to 
    original pseudopotential files. Obviously they'll be the same
    but this makes sure the file operations work
    """
    with tools_for_tests.TemporaryDirectory() as tmp_dir:
        # create object to test
        pp_path_list = [test_inputs_dir+'/PAW.Si', 
                        test_inputs_dir+'/PAW.Ge']
        argvf_template_path = ''
        crystal_template_path = ''
        correct_argvf = ''
        correct_crystal = ''
        pos = [] 
        gcut = -1
        testrun = eval_pp.DftRun(pp_path_list, argvf_template_path, 
                                 crystal_template_path, pos, gcut)
        # call _symlink_pseudopotentials method
        os.mkdir('data')
        testrun._symlink_pseudopotentials()
        # check pseudopotential files have been copied to data/
        with open('data/PAW.Si') as f1, open(pp_path_list[0]) as f2:
            assert f1.read() == f2.read()
        with open('data/PAW.Ge') as f1, open(pp_path_list[1]) as f2:
            assert f1.read() == f2.read()


def test_setup_files():
    """ 
    test: setup_dir method makes files for socorro run

    Expected behavior: calling setup_dir method will create correctly
    preprocessed argvf file in current directory, directory named data/
    and correctly preprocessed data/crystal file.
    """
    correct_argvf = test_inputs_dir+'/argvf.example1'
    correct_crystal = test_inputs_dir+'/crystal.example1'
    correct_Si = test_inputs_dir+'/PAW.Si'
    correct_Ge = test_inputs_dir+'/PAW.Ge'
    with tools_for_tests.TemporaryDirectory() as tmp_dir:
        # create object to test
        pp_path_list = [test_inputs_dir+'/PAW.Si',
                        test_inputs_dir+'/PAW.Ge']
        argvf_template_path = test_inputs_dir+'/argvf.template.example1'
        crystal_template_path = test_inputs_dir+'/crystal.template.example1'
        pos = [[0.0, 0, '0.1'], [0.5, 0.6, 0.7]]
        testrun = eval_pp.DftRun(pp_path_list, argvf_template_path, 
                                 crystal_template_path, pos, 30.)
        testrun.setup_files()
        # compare preprocessed files with correct file examples
        with open('argvf') as f1, open(correct_argvf) as f2:
            assert f1.read() == f2.read()
        with open('data/crystal') as f1, open(correct_crystal) as f2:
            assert map(str.split, f1.readlines()) == map(str.split, f2.readlines())
        with open('data/PAW.Si') as f1, open(correct_Si) as f2:
            assert f1.read() == f2.read()
        with open('data/PAW.Ge') as f1, open(correct_Ge) as f2:
            assert f1.read() == f2.read()



def test_get_forces():
    raise Exception('implement today')

def test_get_energy():
    """
    Read energy from example socorro ouput and check value is correct.
    Run inside temporary directory.
    """
    with tools_for_tests.TemporaryDirectory() as tmp_dir:
        # set up fake dft_run
        pp_path_list = []
        argvf_template_path = ''
        crystal_template_path = '' 
        pos = []
        gcut = -1
        testrun = eval_pp.DftRun(pp_path_list, argvf_template_path,
                                 crystal_template_path, pos, gcut)
        energy_in = testrun.read_energy(test_inputs_dir+'/diaryf.test_get_energy')
        assert isclose(energy_in, -738.821147137)


def test_get_energy_none():
    """
    should return None because no cell energy found in socorro output
    """
    with tools_for_tests.TemporaryDirectory() as tmp_dir:
        # set up fake dft_run
        pp_path_list = []
        argvf_template_path = ''
        crystal_template_path = '' 
        pos = []
        gcut = -1
        testrun = eval_pp.DftRun(pp_path_list, argvf_template_path,
                                 crystal_template_path, pos, gcut)
        energy_in = testrun.read_energy(test_inputs_dir+'/diaryf.test_get_energy_none')
        assert energy_in is None

def test_get_forces():
    """
    Read forces from example socorro ouput and check value is correct.
    Run inside temporary directory.
    """
    with tools_for_tests.TemporaryDirectory() as tmp_dir:
        # set up fake dft_run
        pp_path_list = []
        argvf_template_path = ''
        crystal_template_path = '' 
        pos = []
        gcut = -1
        testrun = eval_pp.DftRun(pp_path_list, argvf_template_path,
                                 crystal_template_path, pos, gcut)
        forces_in = testrun.read_forces(test_inputs_dir+'/diaryf.test_get_forces')
        correct_forces = [[0.007170, -0.015092, -0.069756], [-0.007170, 0.015092, 0.069756]]
        assert np.isclose(forces_in, correct_forces, rtol=1e-9, atol=0.0).all()


def test_get_forces_none():
    """
    Read forces from example socorro ouput and check value is correct.
    Run inside temporary directory.
    """
    with tools_for_tests.TemporaryDirectory() as tmp_dir:
        # set up fake dft_run
        pp_path_list = []
        argvf_template_path = ''
        crystal_template_path = '' 
        pos = []
        gcut = -1
        testrun = eval_pp.DftRun(pp_path_list, argvf_template_path,
                                 crystal_template_path, pos, gcut)
        forces_in = testrun.read_forces(test_inputs_dir+'/diaryf.test_get_forces_none')
        assert forces_in is None


def test_is_converged_converged():
    """returns True if all energies meet convergence criterion"""    
    tol =1e-8
    e0 = [1, 1, 1, 1] # dummy
    e1 = [1.10e-7, 0.80e-7, 5.0e-7, 1.0e-8]
    e2 = [1.15e-7, 0.75e-7, 5.0e-7, 1.5e-9]
    energies = [np.array(e0), np.array(e1), np.array(e2)]
    assert eval_pp.is_converged(energies, tol)


def test_is_converged_one_not_converged():
    """returns False if one energy does not meet convergence criterion"""    
    tol =1e-8
    e0 = [1, 1, 1, 1] # dummy
    e1 = [1.10e-7, 0.80e-7, 5.0e-7, 1.0e-8]
    e2 = [2.15e-7, 0.75e-7, 5.0e-7, 1.5e-9]
    energies = [np.array(e0), np.array(e1), np.array(e2)]
    assert not eval_pp.is_converged(energies, tol)


def test_is_converged_all_not_converged():
    """returns False if no energies meet convergence criterion"""    
    tol =1e-8
    e0 = [1, 1, 1, 1] # dummy
    ek = [1.10e-7, 0.80e-7, 5.0e-7, 1.0e-8]
    e2 = [2.15e-7, 1.75e-7, 6.0e-7, 3.0e-8]
    energies = [np.array(e0), np.array(e1), np.array(e2)]
    assert not eval_pp.is_converged(energies, tol)


def test_is_converged_all_not_converged():
    """returns false when only one gcut has run"""    
    tol =1e-8
    e0 = [1, 1, 1, 1]
    energies = [np.array(e0)]
    assert not eval_pp.is_converged(energies, tol)


def test_run_socorro_no_files():
    """
    test: run_socorro prints warning if files not created
    """
    testrun = eval_pp.DftRun([], [], [], [], 0) 
    assert testrun.run_socorro('') is False


def test_get_random_configurations():
    """Read random configs from file
    """
    positions_file = test_inputs_dir + '/configurations.in.example'
    positions = eval_pp.get_random_configurations(positions_file)
    assert (positions == [[0.00000, 0.00000, 0.00000,  0.37167, 0.50580, 0.47536],
                          [0.00000, 0.00000, 0.00000,  0.74019, 0.24042, 0.44835],
                          [0.00000, 0.00000, 0.00000,  0.49723, 0.50676, 0.22171],
                          [0.00000, 0.00000, 0.00000,  0.59089, 0.49233, 0.32916]]).all()


# def test_run_socorro():
#     """
#     run_socorro should return true when files set up correctly
#     
#     Ideally I could fake the file setup?
#     I should also mock a system call to socorro maybe, since currently
#     it actaully calls socorro (which aborts quickly because no input
#     files found)
#     """
#     testrun = eval_pp.DftRun([], [], [], [], 0) 
#     testrun._are_files_setup = True
#     assert testrun.run_socorro() is True
