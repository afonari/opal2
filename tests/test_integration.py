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

# configurations: [[ 0.       0.       0.       0.37167  0.5058   0.47536]
#                  [ 0.       0.       0.       0.74019  0.24042  0.44835]
#                  [ 0.       0.       0.       0.49723  0.50676  0.22171]
#                  [ 0.       0.       0.       0.59089  0.49233  0.32916]]
# 
# Calling Dakota position sweep in /home/cbrock/opal/opal2/tmpqBv_9u/workdir.example/gcut_dir.20
# 'energies': [-361.742524251, -361.645055783, -361.673323988, -361.741963805], 
# 'forces': [array([-0.028051, -0.005124, -0.009089,  0.028051,  0.005124,  0.009089]), 
#            array([-0.051472,  0.011634, -0.272628,  0.051472, -0.011634,  0.272628]), 
#            array([-0.098216, -0.001774, -0.06916 ,  0.098216,  0.001774,  0.06916 ]), 
#            array([ 0.00845 , -0.016124, -0.059293, -0.00845 ,  0.016124,  0.059293])]
# Calling Dakota position sweep in /home/cbrock/opal/opal2/tmpqBv_9u/workdir.example/gcut_dir.30
# 'energies': [-362.179592631, -362.084566451, -362.112875268, -362.178848522], 
# 'forces': [array([-0.026949, -0.003163, -0.009234,  0.026949,  0.003163,  0.009234]), 
#            array([-0.052534,  0.012131, -0.269554,  0.052534, -0.012131,  0.269554]), 
#            array([-0.095874, -0.001578, -0.067094,  0.095874,  0.001578,  0.067094]), 
#            array([ 0.009391, -0.01741 , -0.057644, -0.009391,  0.01741 ,  0.057644])]
# Calling Dakota position sweep in /home/cbrock/opal/opal2/tmptrcCMM/workdir.example/gcut_dir.40
# 'energies': [-362.181928104, -362.087090838, -362.115398065, -362.181194943]
# 'forces': [array([-0.026782, -0.003068, -0.009228,  0.026782,  0.003068,  0.009228]), 
#            array([-0.0525  ,  0.01213 , -0.269228,  0.0525  , -0.01213 ,  0.269228]), 
#            array([-0.095738, -0.001597, -0.066987,  0.095738,  0.001597,  0.066987]), 
#            array([ 0.009426, -0.017434, -0.057434, -0.009426,  0.017434,  0.057434])]}
# Calling Dakota position sweep in /home/cbrock/opal/opal2/tmptrcCMM/workdir.example/gcut_dir.50
# 'energies': [-362.183838239, -362.088984228, -362.117295369, -362.183104617]
# 'forces': [array([-0.026787, -0.003078, -0.009222,  0.026787,  0.003078,  0.009222]), 
#            array([-0.052491,  0.01214 , -0.26923 ,  0.052491, -0.01214 ,  0.26923 ]), 
#            array([-0.09575 , -0.0016  , -0.066991,  0.09575 ,  0.0016  ,  0.066991]), 
#            array([ 0.009425, -0.017436, -0.057438, -0.009425,  0.017436,  0.057438])]}
# Calling Dakota position sweep in /home/cbrock/opal/opal2/tmptrcCMM/workdir.example/gcut_dir.60
# 'energies': [-362.183869728, -362.08902307, -362.117334733, -362.183136411]
# 'forces': [array([-0.026785, -0.003072, -0.009222,  0.026785,  0.003072,  0.009222]), 
#            array([-0.052491,  0.012135, -0.269246,  0.052491, -0.012135,  0.269246]), 
#            array([-0.095744, -0.001602, -0.066987,  0.095744,  0.001602,  0.066987]), 
#            array([ 0.009425, -0.017436, -0.057439, -0.009425,  0.017436,  0.057439])]}
# Calling Dakota position sweep in /home/cbrock/opal/opal2/tmptrcCMM/workdir.example/gcut_dir.70
# 'energies': [-362.184065922, -362.089220811, -362.117531664, -362.183332873]
# 'forces': [array([-0.026785, -0.003073, -0.009221,  0.026785,  0.003073,  0.009221]), 
#            array([-0.052481,  0.012133, -0.269237,  0.052481, -0.012133,  0.269237]), 
#            array([-0.095746, -0.001603, -0.066991,  0.095746,  0.001603,  0.066991]), 
#            array([ 0.009426, -0.017436, -0.057437, -0.009426,  0.017436,  0.057437])]}
# Calling Dakota position sweep in /home/cbrock/opal/opal2/tmptrcCMM/workdir.example/gcut_dir.80
# 'energies': [-362.184110604, -362.089266806, -362.117577341, -362.183377512]
# 'forces': [array([-0.026783, -0.003071, -0.009221,  0.026783,  0.003071,  0.009221]), 
#            array([-0.052487,  0.012134, -0.269242,  0.052487, -0.012134,  0.269242]), 
#            array([-0.095743, -0.001603, -0.066987,  0.095743,  0.001603,  0.066987]), 
#            array([ 0.009426, -0.017436, -0.057437, -0.009426,  0.017436,  0.057437])]}
def test_eval_pp_main_no_converge():
    """
    objectives are None if there is no gcut convergence
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
    This should converge at gcut=40 and then return objectives of 
    accu=0.067545402548049124 and work=0.013059227885397404
    
    the "correct" objectives could depend on the socorro build.
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
        assert np.isclose(objectives['accu'], 0.067545402548049124)
        assert np.isclose(objectives['work'], 0.013059227885397404)


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
    """ returns proper obectives when no gcut convergence""" 
    raise NotImplementedError



def test_analysis_driver_main_nogcut_converge():
    """ returns proper obectives when a socorro run fails""" 
    raise NotImplementedError
