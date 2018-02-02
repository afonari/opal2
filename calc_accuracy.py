import os
import sys
import numpy as np


def calc_accuracy_objective(f_soc, allelectron_forces_file):
    """
    Calculates accuracy objective by comparing socorro and
    all electron forces at each atomic structure tested.
    """
    f_allelectron = read_allelectron_forces(filename=allelectron_forces_file)
    return force_objective(f_soc, f_allelectron)


def force_objective(f_soc, f_allelectron):
    """ 
    f_soc is list of numpy arrays, where each element of list represents 
    on atomic configuration. The numpy arrays are N by 3 where N is the number o
    of atoms in the crystal.
    """
    assert f_allelectron.shape[1]%3 == 0, "Each atom should have three force components."
    num_configs = f_allelectron.shape[0]
    num_atoms   = (f_allelectron.shape[1])/3

    # accuracy objective is rmsd of magnitude of difference between socorro and elk force vectors
    force_obj_unweighted = np.sqrt( np.sum((f_soc-f_allelectron)**2.)/num_configs/num_atoms )
    
    #force_obj = force_weight * force_obj_unweighted
    return force_obj_unweighted


def read_allelectron_forces(filename='allelectron_forces.dat'):
    """
    Read 'correct' forces as calculated from Elk from file.
    Returns an MxN numpy array where M is the number of atomic structures and N/3 is the number of atoms
    in the structures.
    """
    ae_forces = np.loadtxt(filename)
    return ae_forces



# #--- atan objective --------------------------------------------------------------------
# # read last (fifth) column from each scattering file, which is a single RMS of data from logderivative file
# 
# atan_sum = 0.
# scattering_file_count = 0
# for elem in element_list:
#     dir = elem+'_pseudopotential'
#     os.chdir(dir)
#     for file in os.listdir('.'):
#         if file.startswith("scattering."):
#             scattering_data = np.loadtxt(file)
#             atan_and_core_error = scattering_data[4]
#             atan_sum += atan_and_core_error
#             scattering_file_count += 1
#     os.chdir('..')
# 
# # division by pi/2 should normalize to 1 if E_fit = E_min
# atan_obj_unweighted = atan_sum / float(scattering_file_count) / (np.pi/2.)
# atan_obj = atan_weight * atan_obj_unweighted
# #---------------------------------------------------------------------------------------
# 
# #total_obj = force_obj + atan_obj
# 
# # # print accuracy objective
# # print "force_objective = ", force_obj 
# # print "atan_objective = ", atan_obj 
# # print "total_accuracy_objective =", total_obj 
