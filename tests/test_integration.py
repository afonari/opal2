#!/usr/bin/env python
import sys
sys.path.append('.')
import os
import shutil
import tools_for_tests
import numpy as np
import pytest
import eval_pp
import analysis_driver

# directory of test input files
main_test_inputs_dir = os.path.join(os.getcwd(), 'tests', 'test_inputs_integration')



def test_eval_pp_main_no_converge():
    """
    raises NoCutoffConvergence if there is no gcut convergence
    """
    test_inputs_dir = os.path.join(main_test_inputs_dir, 'eval_pp_main_test')
    with pytest.raises(eval_pp.NoCutoffConvergence):
        with tools_for_tests.TemporaryDirectory() as tmp_dir:
            # set up a mock work directory:
            shutil.copy(os.path.join('..', 'calc_nflops'), os.getcwd())
            shutil.copy(os.path.join(test_inputs_dir, 'configurations.in.example'), 'configurations.in')
            shutil.copy(os.path.join(test_inputs_dir, 'allelectron_forces.dat.example'), 'allelectron_forces.dat')
            os.mkdir('workdir.example')
            os.chdir('workdir.example')
            shutil.copy(os.path.join(test_inputs_dir, 'argvf.template'), 'argvf.template')
            shutil.copy(os.path.join(test_inputs_dir, 'crystal.template'), 'crystal.template')
            shutil.copy(os.path.join(test_inputs_dir, 'PAW.Si'), 'PAW.Si')
            shutil.copy(os.path.join(test_inputs_dir, 'PAW.Ge'), 'PAW.Ge')
    
            # run eval_pp
            gcuts = [20., 30., 40.]
            energy_tol = 1.e-100  # set impossible tolerance so it doesn't converge
            objectives = eval_pp.main(['Si', 'Ge'], gcuts, energy_tol)


def test_eval_pp_main():
    """
    This should converge at gcut=40 and then return objectives:
    accu = 0.12408939054384546
    work = 0.009064640532217023
    
    the "correct" accuracy objectives could depend on the socorro build,
    and the work objective may depend on some other things such as parallelization.
    """
    test_inputs_dir = os.path.join(main_test_inputs_dir, 'eval_pp_main_test')
    with tools_for_tests.TemporaryDirectory() as tmp_dir:
        # set up a mock work directory:
        shutil.copy(os.path.join('..', 'calc_nflops'), os.getcwd())
        shutil.copy(os.path.join(test_inputs_dir, 'configurations.in.example'), 'configurations.in')
        shutil.copy(os.path.join(test_inputs_dir, 'allelectron_forces.dat.example'), 'allelectron_forces.dat')
        os.mkdir('workdir.example')
        os.chdir('workdir.example')
        shutil.copy(os.path.join(test_inputs_dir, 'argvf.template'), 'argvf.template')
        shutil.copy(os.path.join(test_inputs_dir, 'crystal.template'), 'crystal.template')
        shutil.copy(os.path.join(test_inputs_dir, 'PAW.Si'), 'PAW.Si')
        shutil.copy(os.path.join(test_inputs_dir, 'PAW.Ge'), 'PAW.Ge')

        # run eval_pp
        gcuts = [20., 30., 40., 50.]
        energy_tol = 3.e-3 
        objectives = eval_pp.main(['Si', 'Ge'], gcuts, energy_tol)
        assert np.isclose(objectives['accu'], 0.12408939054384546, rtol=0., atol=0.0002)
        assert np.isclose(objectives['work'], 0.009064640532217023, rtol=0., atol=0.000001)



def test_analysis_driver_main_Si_noconverge():
    """
    For this test, the silicon inputs are bad so atompaw does not converge,
    and the analysis driver returns 100s for both objectives
    """
    test_inputs_dir = os.path.join(main_test_inputs_dir, 'analysis_driver_main_Si_noconverge')
    with tools_for_tests.TemporaryDirectory() as tmp_dir:
        # set up a mock work directory:
        shutil.copy(os.path.join('..', 'calc_nflops'), os.getcwd())
        shutil.copy(os.path.join(test_inputs_dir, 'opal.in'), 'opal.in')
        shutil.copy(os.path.join(test_inputs_dir, 'configurations.in.example'), 'configurations.in')
        shutil.copy(os.path.join(test_inputs_dir, 'allelectron_forces.dat.example'), 'allelectron_forces.dat')
        os.mkdir('workdir.example')
        os.chdir('workdir.example')
        shutil.copy(os.path.join(test_inputs_dir, 'argvf.template'), 'argvf.template')
        shutil.copy(os.path.join(test_inputs_dir, 'crystal.template'), 'crystal.template')
        shutil.copy(os.path.join(test_inputs_dir, 'Si.in.template'), os.getcwd())
        shutil.copy(os.path.join(test_inputs_dir, 'Ge.in.template'), os.getcwd())
        shutil.copy(os.path.join(test_inputs_dir, 'params'), os.getcwd())

        # run analysis driver
        analysis_driver.main()
        with open('results') as fin:
            assert fin.readlines()==['  1.0000000000000000E+02 accu\n', '  1.0000000000000000E+02 work\n']



def test_analysis_driver_main_success():
    """
    """
    test_inputs_dir = os.path.join(main_test_inputs_dir, 'analysis_driver_main_success')
    with tools_for_tests.TemporaryDirectory() as tmp_dir:
        # set up a mock work directory:
        shutil.copy(os.path.join('..', 'calc_nflops'), os.getcwd())
        shutil.copy(os.path.join(test_inputs_dir, 'opal.in'), 'opal.in')
        shutil.copy(os.path.join(test_inputs_dir, 'configurations.in.example'), 'configurations.in')
        shutil.copy(os.path.join(test_inputs_dir, 'allelectron_forces.dat.example'), 'allelectron_forces.dat')
        os.mkdir('workdir.example')
        os.chdir('workdir.example')
        shutil.copy(os.path.join(test_inputs_dir, 'argvf.template'), 'argvf.template')
        shutil.copy(os.path.join(test_inputs_dir, 'crystal.template'), 'crystal.template')
        shutil.copy(os.path.join(test_inputs_dir, 'Si.in.template'), os.getcwd())
        shutil.copy(os.path.join(test_inputs_dir, 'Ge.in.template'), os.getcwd())
        shutil.copy(os.path.join(test_inputs_dir, 'params'), os.getcwd())

        # run analysis driver
        analysis_driver.main()
        with open('results') as fin:
            assert fin.readlines()==['  7.6992177462473416E-02 accu\n', '  8.7573645819723784E-03 work\n']



def test_analysis_driver_main_nogcut_converge():
    """ 
    returns proper obectives of 95 when no gcut convergence
    sets impossible energy tolerance in opal.in
    """ 
    test_inputs_dir = os.path.join(main_test_inputs_dir, 'analysis_driver_main_nogcut_converge')
    with tools_for_tests.TemporaryDirectory() as tmp_dir:
        # set up a mock work directory:
        shutil.copy(os.path.join('..', 'calc_nflops'), os.getcwd())
        shutil.copy(os.path.join(test_inputs_dir, 'opal.in'), 'opal.in')
        shutil.copy(os.path.join(test_inputs_dir, 'configurations.in.example'), 'configurations.in')
        shutil.copy(os.path.join(test_inputs_dir, 'allelectron_forces.dat.example'), 'allelectron_forces.dat')
        os.mkdir('workdir.example')
        os.chdir('workdir.example')
        shutil.copy(os.path.join(test_inputs_dir, 'argvf.template'), 'argvf.template')
        shutil.copy(os.path.join(test_inputs_dir, 'crystal.template'), 'crystal.template')
        shutil.copy(os.path.join(test_inputs_dir, 'Si.in.template'), os.getcwd())
        shutil.copy(os.path.join(test_inputs_dir, 'Ge.in.template'), os.getcwd())
        shutil.copy(os.path.join(test_inputs_dir, 'params'), os.getcwd())

        # run analysis driver
        analysis_driver.main()
        with open('results') as fin:
            assert fin.readlines()==['  9.5000000000000000E+01 accu\n', '  9.5000000000000000E+01 work\n']
