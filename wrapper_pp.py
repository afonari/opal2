#/usr/bin/env python

import sys
import ConfigParser


# get global settings from config file
settings = ConfigParser.ConfigParser()
settings.read('opal.ini')


def main():
    random_sleep()  # sleep for random time to prevent overload of atompaw runs
    pp_success = create_paws()  # attempt to create PAW
    if pp_success == True:
        results = submit_job()  # if PP creation success, submit job to test PP
    else:
        results = (100, 100)
    write_results_file(results)

def random_sleep():
    '''sleeps a random amount of time to prevent overload of atompaw runs
    time is chosen to spread out n runs such that approximately p are 
    running at time
    '''
    #gen_size = get_gen_size()
    #nproc = get_num_procs()
    #t_atompaw = 


def create_paws():
    '''run atompaw for each element and attempt to create pp'''
    pass


def write_results_file(results):
    '''clean up job and write results file. 
    This wrapper can exit at many points, each resulting in different objectives.
    This function can be called at any point to write reults file and exit

    reads in 2-tuple for accuracy objective and work objective
    '''
    #with open('results.tmp') as f:
    clean_up()


def clean_up():
    '''compresses testing work directory to prevent breaking file number quotas
    may also delete some unnecessary files
    '''
    # compress_directory()
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
