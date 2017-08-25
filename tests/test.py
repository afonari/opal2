#!/usr/bin/env python
import sys
import os
import shutil
import eval_pp
import wrapper_pp

main_dir = os.getcwd()
test_dir = main_dir + '/tests'
test_inputs_dir = main_dir + '/tests/test_inputs'

#################################
# UNIT TESTS (SORT OF)
################################
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



################################
# integration tests
################################
def test_symlink_pseudopotentials():
    """
    write later 
    """
    tmp_dir = test_dir + '/tmp_symlink_pseudopotential'
    os.mkdir(tmp_dir)
    try:
        os.chdir(tmp_dir)
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
    finally:
        os.chdir(main_dir)
        shutil.rmtree(tmp_dir)


def test_run_socorro():
    """
    test: run_socorro calls soccoro when files setup properly
    """
    raise Exception('test not implemented')
   

def test_run_socorro_no_files():
    """
    test: run_socorro failes gracefully if files not created
    """
    raise Exception('test not implemented')


def test_setup_files():
    """ 
    test: setup_dir method makes files for socorro run

    Expected behavior: calling setup_dir method will create correctly
    preprocessed argvf file in current directory, directory named data/
    and correctly preprocessed data/crystal file.
    """
    tmp_dir = test_dir + '/tmp_setup_files'
    os.mkdir(tmp_dir)
    try:
        os.chdir(tmp_dir)
        # create object to test
        argvf_template_path = test_inputs_dir+'/argvf.template.example1'
        crystal_template_path = test_inputs_dir+'/crystal.template.example1'
        correct_argvf = test_inputs_dir+'/argvf.example1'
        correct_crystal = test_inputs_dir+'/crystal.example1'
        pos = [[0.0, 0, '0.1'], [0.5, 0.6, 0.7]]
        testrun = eval_pp.DftRun([], argvf_template_path, crystal_template_path, pos, 30.)
        testrun.setup_files()
        # compare preprocessed files with correct file examples
        with open('argvf') as f1, open(correct_argvf) as f2:
            assert f1.read() == f2.read()
        with open('data/crystal') as f1, open(correct_crystal) as f2:
            assert map(str.split, f1.readlines()) == map(str.split, f2.readlines())
    finally:
        os.chdir(main_dir)
        shutil.rmtree(tmp_dir)
