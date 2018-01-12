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

def create_pseudopotentials():
    return True

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
