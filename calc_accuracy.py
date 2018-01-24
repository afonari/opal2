# calc_accuracy.py
# calculates accuracy objective for socorro run
#
# python calc_accuracy.py gcut_index
#
# force accuracy objective is rmsd of magnitude of difference between socorro and elk force vectors
# sqrt(   sum( (f_soc-f_elk)^2 ) /num_configs   )
# It is then weighted by force_weight
#
# atan accuracy objective is sum of atan+core error (fifth column) of each scattering file divided by number of scattering files. It is then weighted by atan_weight
#
#
# $Id: calc_accuracy.py,v 1.10 2015/07/30 20:46:09 brockc Exp $
#
# $Name:  $ 

import os
import sys
import numpy as np



# READ OPAL.IN INTO MEMORY
with open('../opal.in') as f:
    opal_in = f.readlines()

# READ OBJECTIVE WEIGHTS FROM OPAL.IN TEXT
for i in range(0, len(opal_in)):
    if opal_in[i].strip() == 'FORCE_WEIGHT':
        #read next line
        force_weight = float(opal_in[i+1])
    if opal_in[i].strip() == 'ATAN_WEIGHT':
        # read next line
        atan_weight = float(opal_in[i+1])

# READ ELEMENT LIST FROM OPAL.IN TEXT (NEED FOR ATAN OBJECTIVE LATER)
for i in range(0, len(opal_in)):
    if opal_in[i].strip() == 'ELEMENTS':
        element_list = opal_in[i+1].split()




#---FORCE OBJECTIVE----------------------------------------------------------------

## read gcut index from command line
#gcut_index  = float(sys.argv[1])

# read elk solution from file
elk_force_file = os.path.join(os.pardir, 'elk_force.dat')
f_elk_in = np.loadtxt(elk_force_file, skiprows=1,ndmin=2)

num_configs = f_elk_in.shape[0]
num_atoms   = (f_elk_in.shape[1]-1)/2/3

f_elk = 2.*f_elk_in[:,(num_atoms*3+1):] # convert Hartree to Ryd

# determine number of numerical columns in socorro force file
with open('converged_forces.dat') as f:
    f.readline() # skip headers
    f.readline()
    ncols = len(f.readline().split())

# read socorro forces from force.dat file
f_soc = np.loadtxt('converged_forces.dat', skiprows=2, usecols=range(1,ncols) )

#  accuracy objective is rmsd of magnitude of difference between socorro and elk force vectors
# force_obj = math.sqrt(  (fx_s-fx_e)**2. + (fy_s-fy_e)**2. + (fz_s-fz_e)**2.  )
force_obj_unweighted = np.sqrt(   np.sum( (f_soc-f_elk)**2. ) /num_configs /num_atoms  )

force_obj = force_weight * force_obj_unweighted
#-----------------------------------------------------------------------------------



#--- atan objective --------------------------------------------------------------------
# read last (fifth) column from each scattering file, which is a single RMS of data from logderivative file

atan_sum = 0.
scattering_file_count = 0
for elem in element_list:
    dir = elem+'_pseudopotential'
    os.chdir(dir)
    for file in os.listdir('.'):
        if file.startswith("scattering."):
            scattering_data = np.loadtxt(file)
            atan_and_core_error = scattering_data[4]
            atan_sum += atan_and_core_error
            scattering_file_count += 1
    os.chdir('..')

# division by pi/2 should normalize to 1 if E_fit = E_min
atan_obj_unweighted = atan_sum / float(scattering_file_count) / (np.pi/2.)
atan_obj = atan_weight * atan_obj_unweighted
#---------------------------------------------------------------------------------------


total_obj = force_obj + atan_obj

# print accuracy objective
print "force_objective = ", force_obj 
print "atan_objective = ", atan_obj 
print "total_accuracy_objective =", total_obj 
