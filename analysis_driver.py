#!/bin/env python
#import evaluate_pp
import os
import subprocess
import eval_pp
import sys
import dakota_interfacing_2.interfacing.parallel as di

# # EXAMPLE FROM DAKOTA DOCS (share/dakota/Python/dakota/interfacing/__init__.py)
# import dakota.interfacing as di
# # Read and parse the parameters file and construct Parameters and Results 
# # objects
# params, results = di.read_parameters_file("params.in", "results.out")
# # Accessing variables
# x1 = params["x1"]
# x2 = params["x2"]
# # Run a fictitious Python-based simulation and store the result in the
# # function value of the 'f1' response.
# results["f1"].function =  sim_results = my_simulation(x1, x2)
# results.write()



class PseudopotentialFail(Exception):
    """raised if pseudopotential creation failed with given inputs"""



def main():
    """
    required files in run directory: 
        ../opal.in  (contains some user settings for optimization)
        params  (created by dakota)
        results  (created by dakota)

    the Results and Parameters objects are created using dakota's python interface
    """
    with open('analysis_driver.log', 'w') as ad_log:
        sys.stdout = ad_log
        # read settings from input file
        settings = read_inputs('../opal.in')
        element_list = settings['element_list']
        templates_dir = settings['templates_dir']
        gcuts = map(float, settings['gcuts'])
        energy_tol = float(settings['energy_tol'])

        # Parse the Dakota parameters file and construct Parameters and Results objects
        params, results = di.read_parameters_file("params", "results")

        preprocess_pseudopotential_input_files(element_list, templates_dir)
        pseudopotential_success = create_all_pseudopotentials(element_list)
        if pseudopotential_success:
            try:
                objectives = eval_pp.main(element_list, gcuts, energy_tol)
                results['accu'].function = objectives['accu']
                results['work'].function = objectives['work']
            except eval_pp.SocorroFail:
                # if a socorro run fails
                results['accu'].function = 102
                results['work'].function = 102
            except eval_pp.NoCutoffConvergence:
                # if the results don't converge with respect to plane wave cutoff
                results['accu'].function = 95
                results['work'].function = 95
        else:
            # if pseudopotential creation unsuccessful
            results['accu'].function = 100
            results['work'].function = 100

        results.write()

    

def create_all_pseudopotentials(element_list):
    """
    For each element, attempt to create pseudopotential.

    Returns True if all pseudopotentials were created succesfully, 
    False otherwise.
    """
    for elem in element_list:
        try:
            create_a_pseudopotential(elem)
        except PseudopotentialFail:
            return False
    return True   
   


def create_a_pseudopotential(elem):
    """
    Creates a pseudopotential assuming input file is in current directory,
    and it is named {elem}.in

    The pseudopotential is generated in a named directory where all 
    output files can be nicely stored, and then symlinked
    to the current directory as PAW.{elem} 

    raises PseudopotentialFail exception if no pseudopotential can be created.
    """
    start_dir = os.getcwd()
    atompaw_input_filename = os.path.join(start_dir, elem+'.in')
    pseudopotential_name = elem+'.SOCORRO.atomicdata'

    dir_name = elem+'_pseudopotential'
    os.mkdir(dir_name)
    os.chdir(dir_name)

    run_atompaw(atompaw_input_filename)
    if os.path.isfile(pseudopotential_name):
        # if pseudopotential actually created, symlink to it
        os.chdir(start_dir)
        os.symlink(os.path.join(dir_name, pseudopotential_name), 'PAW.'+elem)
    else:
        os.chdir(start_dir)
        raise PseudopotentialFail
     


def run_atompaw(atompaw_input_filename):
    """
    runs atompaw in current directory for given input file
    currently assumes atompaw4

    For tile_run_dynamic, the first argument should be the tile size
    determined by the socorro runs, while np should always be 1.
    """
    with open(atompaw_input_filename,'r') as input_fin, open('log', 'w') as log_fout: 
        # subprocess.call(['atompaw'], stdin=input_fin, stdout=log_fout)
        # subprocess.call(['srun', '-n', '1', 'atompaw'], stdin=input_fin, stdout=log_fout)
        di.tile_run_dynamic(commands=[(1, ["-np", "1", "--bind-to", "none", "atompaw"])], 
                            dedicated_master=0, stdin=input_fin, stdout=log_fout)



def preprocess_pseudopotential_input_files(element_list, template_path):
    """
    Preprocessing for atompaw, uses Dakota's dprepro utility 
    Writes atompaw input file called {elem}.in each element in element list.
    
    element_list: list of atomic symbols for all elements 
                  in current optimization    
    template_path: path to dir containing input file templates
    """
    for elem in element_list:
        template_file = os.path.join(template_path, elem+'.in.template')
        new_input_file = elem+'.in'
        subprocess.check_call(['dprepro', 'params', template_file, new_input_file])
            


def read_inputs(filename):
    """ 
    flimsy input file parser
    
    returns a dictionary of settings, where the value of each setting is a string or
    list of strings
    """
    settings = {}
    with open(filename) as fin:
        data = fin.readlines()
    
    for line in data:
        if line.rstrip() and line.lstrip()[0] != '#':  # if line isn't blank and not a comment
            key, value = line.split()[0], line.split()[1:]
            if len(value) == 1:
                value = value[0]
            settings[key] = value

    return settings



if __name__=='__main__':
    main()
