#/usr/bin/env python

import os
import sys
import ConfigParser
#import logging

def main():
    settings = read_input_file()
    if _constraints_violated():
        results = {'accu': 110, 'work': 110}
        write_results_file(results)
        # clean up
    else:
        submit_batch_job()
    # log to som main file in this directory?


def read_input_file(config_file='opal.ini'):
    """
    reads user defined options from config file opal.ini
    (alternative config file names can be passed in for testing purposes)
    returns a SafeConfigParser opbject so user settings can be accessed
    using settings.get('section', 'option')
    """
    settings = ConfigParser.SafeConfigParser()
    settings.read(config_file)
    return settings


def _constraints_violated():
    # read constraints file (or is it part of input?)
    #if any statement false
    #    return False
    #else
    #    return True
    pass


def run_and_monitor_job():
    """
    submits job to cluster, which should run a bash script that runs a python script
    to create the pseudopotentials then run some tests. could return either real
    objectives, or false objectives based on a number of errors
    """
    # files that are created (not by this script) at different points during the run
    job_started_file = 'job_started'
    job_end_file = 'job_completed'
    job_canceled_file = 'job_canceled_walltime'

    # run bash script (system call sbatch)
    submit_job() # run this in new thread

    # somehow get results back
    return {'accu': 500, 'work': 500} # return 500s for testing


def submit_batch_job():
    # some sort of system call
    pass
        

# MAY MOVE ALL FUNCTIONALITY BELOW THIS POINT INTO SEPARATE MODULE 
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
