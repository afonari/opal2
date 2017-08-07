#/usr/bin/env python

import os
import sys
import ConfigParser


def main():
    settings = read_input_file()
    if _constraints_violated():
        results = {'accu': 110, 'work': 110}
    else:
        random_sleep()  # sleep for random time to prevent overload of atompaw runs
        pp_success = create_paws()  # attempt to create PAW
        if pp_success:
            results = submit_job()  # if PP creation success, submit job to test PP
        else:
            results = {'accu': 100, 'work': 100}
    write_results_file(results)


def _constraints_violated():
    # read constraints file (or is it part of input?)
    #if any statement false
    #    return False
    #else
    #    return True
    pass


def read_inputs_file():
    settings = ConfigParser.ConfigParser()
    settings.read('opal.ini')
    return settings


def random_sleep():
    '''sleeps a random amount of time to prevent overload of atompaw runs
    #time is chosen to spread out n runs such that approximately p are 
    #running at time
    '''
    # leave this manual for now...make it auto later
    #gen_size = get_gen_size()
    #nproc = get_num_procs()
    t_max = 


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


def get_gen_size():
    '''read generation size from dakota log'''
    return 100


def get_num_procs():
    if len(sys.argv) == 1:
        nproc = 8  # defualt value
    else:
        nproc = sys.argv[1]
    return nproc


if __name__=="__main__":
    main()
