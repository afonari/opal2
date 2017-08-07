#/usr/bin/env python

import os
import sys
import ConfigParser


def main():
    settings = read_input_file()
    if _constraints_violated():
        results = {'accu': 110, 'work': 110}
    else:
        results = submit job():
        # MOVE TO SUBMIT JOB
        # pp_success = create_paws()  # attempt to create PAW
        # if pp_success:
        #     results = submit_job()  # if PP creation success, submit job to test PP
        # else:
        #     results = {'accu': 100, 'work': 100}
    write_results_file(results)


def read_inputs_file():
    settings = ConfigParser.ConfigParser()
    settings.read('opal.ini')
    return settings


def _constraints_violated():
    # read constraints file (or is it part of input?)
    #if any statement false
    #    return False
    #else
    #    return True
    pass

def submit_job():
    """
    submits job to cluster, which should run a bash script that runs a python script
    to create the pseudopotentials then run some tests. could return either real
    objectives, or false objectives based on a number of errors
    """
    pass


# MOVE TO DIFFERENT SCRIPT
def create_paws():
    '''run atompaw for each element and attempt to create pp'''
    pass


def write_results_file(results):
    '''write results file. 
    This wrapper_pp.py script can exit at many points, each resulting in 
    different objectives. This function can be called at any point to write 
    results file and exit

    accepts Objectives object for accuracy objective and work objective
    '''
    with open('results.tmp', 'w') as f:
        f.write(str(results['accu'])+' accu_obj\n')
        f.write(str(results['work'])+' work_obj\n')
    os.rename('results.tmp', 'results')  # necessary to prevent Dakota race condition
    clean_up()


def clean_up():
    '''compresses testing work directory to prevent breaking file number quotas
    may also delete some unnecessary files
    '''
    # compress_directory()
    # also, delete directory if constraints violated????
    pass


if __name__=="__main__":
    main()
