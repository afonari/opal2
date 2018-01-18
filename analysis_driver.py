#!/bin/env python
#import evaluate_pp
import os
import subprocess

# globals that I need to eventuallyu read from input file
element_list = ['Si', 'Ge']
templates_dir = 'pseudopotential_templates'
template_path_list = [os.path.join(templates_dir, str(elem)+'.atompaw.template') 
                      for elem in element_list]
print(template_path_list)


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

def main():
    preprocess_pseudopotential_input_files(element_list, templates_dir)
    is_successful = create_all_pseudopotentials()
    if is_successful:
        objectives = mock_evaluate_pseudopotentials()    
        write_results(objectives)
    else:
        write_results(bad)
    

def mock_evaluate_pp():
    """ temporary until real evaluate_pp is up and running"""
    return 10, 20


def write_results():
    pass


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
    to the current directory. 

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
        raise PseudopotentialFail
     

class PseudopotentialFail(Exception):
    """raised if pseudopotential creation failed with given inputs"""


def run_atompaw(atompaw_input_filename):
    """
    runs atompaw in current directory for given input file
    currently assumes atompaw4
    """
    with open(atompaw_input_filename,'r') as input_fin, open('log', 'w') as log_fout: 
        subprocess.call(['atompaw'], stdin=input_fin, stdout=log_fout)


def preprocess_pseudopotential_input_files(element_list, template_path):
    """
    Preprocessing for atompaw, uses Dakota's dprepro utility 
    
    element_list: list of atomic symbols for all elements 
                  in current optimization    
    template_path: path to dir containing input file templates
    """
    for elem in element_list:
        template_file = os.path.join(template_path, elem+'.in.template')
        new_input_file = elem+'.in'
        subprocess.check_call(['dprepro', 'params', template_file, new_input_file])
            

if __name__=='__main__':
    main()


