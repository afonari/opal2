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


def main():
    preprocess_pseudopotential_input_files(element_list, templates_dir)
    create_successful = create_pseudopotentials()
        
    if create_successful:
        objectives = mock_evaluate_pp()    
    else:
        write_results()
    
    write_results()




def mock_evaluate_pp():
    """ temporary until real evaluate_pp is up and running"""
    return 10, 20

def write_results():
    pass

# def create_pseudopotentials(element_list):
#     """
#     loops through element list
#     for each element, makes a directory in which to create psueodpotential
#     and keep log and atompaw output
#     symlinks to pseudopotentials from main directory
#     """
#     start_dir = os.getcwd()
#     for elem in element_list:
#         atompaw_input_filename = elem+'.in'
#         # create directory
#         dir_name = elem+'_pseudopotential'
#         os.mkdir(dir_name)
#         os.chdir(dir_name)
#         # go to directory
#         os.symlink(
#         # ln -s ../$elem.in
#         os.symlink
#         # some sort of error handling??
#         with open(atompaw_input_filename,'r') as input_fin, open('log', 'w') as log_fout: 
#             subprocess.call(['atompaw'], stdin=input_fin, stdout=log_fout)
#         os.chdir(start_dir)
#         os.symlink(os.path.join(dir_name, paw_name), paw_name)


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




# FROM OLD CREATE_PP.PY
### FOR ATOMPAW VERSION 4
# # write 100s to results.tmp and exit if pseudopotential not created correctly:
# if 'Error in EvaluateTP -- no convergence' in open(atompaw_log_file).read():
#   # write results.tmp
#   with open('atompaw_not_converged','w') as fout:
#     fout.write('no convergence for ' + element + ' \n')
#   exit()
#
### FOR ATOMPAW VERSION 3
# # write 100s to results.tmp and exit if pseudopotential not created correctly:
# if '-- no convergence' in open(atompaw_log_file).read():
#   # write results.tmp
#   with open('atompaw_not_converged','w') as fout:
#     fout.write('no convergence for ' + element + ' \n')
#   exit()
