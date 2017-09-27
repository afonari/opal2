import numpy as np
import os
import sys
import subprocess


def main():
    '''
    code within gcut loop is structured the way it is so socorro runs
    can be run in parallel subprocesses
    '''
    # these are the same for different optimizations
    main_argvf_template_path = test_inputs_dir+'/argvf.template.example1'
    main_crystal_template_path = test_inputs_dir+'/crystal.template.example1'

    # these will change for different optimizations
    main_pp_path_list = get_pp_path_list() # read pp list from file?
    main_positions_to_run = get_random_configurations() # read random configs from file?

    # specify in opal.in?
    gcuts = np.arange(10.0, 110.0, 10.0)

    # increase gcut until converged
    for gcut in gcuts:
        gcut_dir_name = 'gcut_dir.' + str(int(gcut))
        os.mkdir(gcut_dir_name)
        os.cwd(gcut_dir_name)

        # creates dft run object for each position
        # NEED SOME SORT OF DIRECTORY MANAGEMENT HERE
        dft_runs = []
        for pos in main_positions_to_run:
            dft_runs.append(eval_pp.DftRun(main_pp_path_list, main_argvf_template_path,
                                 main_crystal_template_path, pos, gcut))
        
        # run socorro at position in parallel
        position_sweep(dft_runs)

        # get energy and force reults from each socorro run
        for dft_run in dft_runs:
            if dft_run.is_successful:
                dft_run.get_energy()
                dft_run.get_forces()
        # PRINT OUT INTERMEDIATE FORCES AND ENERGIES SOMEWHERE?

        # check if results are converged with respect to gcut
        if is_converged(dft_runs):
            calculate_final_results(dft_runs)
            write_forces('converged_forces.dat')
            write_objectives('accuracy_obj.log')
            break
    else:
        # do stuff related to no gcut converge
        pass


#def position_sweep(pp_path_list, argvf_template_path,
#                 crystal_template_path, atom_positions, gcut):
def position_sweep(dft_runs):
    '''
    run several instances of socorro on different threads using
    different positions
    
    when all socorro runs are done, returns dft_run objects

    main_ variables are defined globally or in the calling function
    '''
    # where does this get output to?? change to logger
    print 'Calling Dakota position sweep in', 'pwd'

    # # create dft run object for each position to run
    # dft_runs = []
    # for r in atom_positions:
    #     dft_runs.append(eval_pp.DftRun(main_pp_path_list, main_argvf_template_path,
    #                              main_crystal_template_path, pos, gcut))

    # for each dft run, set up files and start socorro subprocess
    processes = []
    for dft_run in dft_runs:
        dft_run.setup_files()
        # some sort of directory management
        p = dft_run.run_socorro() # call socorro 
        ps.append(p) # add p to process list
    
    # wait for each process to finish
    for process in ps:
        process.wait()


    # WHAT HAPPENS IN EVENT OF WALL TIME LIMIT
    check_socorro_fail()
    # cases: success, wall time limit hit, socorro no converge, socorro fail
    

class DftRun:
    '''
    class for setting up, running, and post processing soccoro dft
    calculation 

    inputs
    pp_path_list: paths to every pseudopotential needed for run.
     Assumes pseudopotential files already be named PAW.{elementsymbol}
    argvf_template_path: path to argvf template file
    crystal_template_path: path to crystal template file
    atom_positions: some sort of list of atomic positions
    gcut: wf energy cutoff for dft calculation

    important attributes
    pp_path_list: see inputs (pp_path_list)
    argvf_template_path: see inputs
    crystal_template_path: see inputs
    atom_positions: see inputs
    gcut: see inputs
    _are_files_setup: True if setup_files() run success, False otherwise

    public methods
    setup_files: sets up files for socorro dft run in current directory
     (argvf and crystal)
    run_socorro: system calls socorro in current directory, only works
     if _are_files_setup is True
    '''
    def __init__(self, pp_path_list, argvf_template_path,
                 crystal_template_path, atom_positions, gcut):
        self.pp_path_list = pp_path_list
        self.atom_positions = atom_positions
        self.gcut = float(gcut)
        self.argvf_template_path = argvf_template_path
        self.crystal_template_path = crystal_template_path
        self._are_files_setup = False

    def run_socorro(self):
        '''
        runs socorro in a subprocess, reurns process ID, and continues
        '''
        if self._are_files_setup is False:
            # wnat exit so jobs don't keep running
            print 'Files not setup yet. Must run setup_files() first'
            return False
        else:
            p = subprocess.Popen('socorro')
            return p # return process id for wait later
   
    def setup_files(self):
        '''
        write dft input files from templates 

        note this will probably fail if argvf, data/, or data/crystal
        already exist. This may be desirable behavior but if not I can
        change it.
        '''
        self._make_argvf()
        os.mkdir('data')
        self._make_crystal()
        self._symlink_pseudopotentials()
        self._are_files_setup = True

    def _make_argvf(self):
        ''' writes preprocessed argvf text to argvf file '''
        # read in text from template file
        with open(self.argvf_template_path) as fin:
            argvf_template_text = fin.readlines()
        # write preprocessed text to new argvf file
        with open('argvf', 'w') as fout:
            preprocessed_text = self._preproc_argvf(argvf_template_text)
            fout.writelines(preprocessed_text)
 

    def _preproc_argvf(self, template_text):
        """
        enters energy cutoff values into dft input file text

        gcut: number to input into template file (int, float, or str)
        template_text: template text for input to dft code,
            read using readlines or similar. The tags {gcut} and 
            {4gcut} should be in the file.
        returns new_text: final text for running dft code, in list of lines
        """
        gcut = float(self.gcut)
        text_tmp = [ line.replace('{gcut}', str(gcut)) for line in template_text ]
        new_text = [ line.replace('{4gcut}', str(4.0 * gcut)) for line in text_tmp ]
        return new_text

    def _make_crystal(self):
        # read in text from template file
        with open(self.crystal_template_path) as fin:
            crystal_template_text = fin.readlines()
        preprocessed_text = self._preproc_crystal(crystal_template_text,
                                                  self.atom_positions)
        # write preprocessed text to data/crystal
        with open('data/crystal', 'w') as fout:
            fout.writelines(preprocessed_text)
 
    @staticmethod
    def _preproc_crystal(mytext, atom_positions):
        atom_positions = [ map(float, r) for r in atom_positions ]
        # remove all blank lines (shouldn't cause problems?)
        mytext = [ line for line in mytext if line.strip() ]
        # append 3 float values for each of final lines
        for i, r in enumerate(reversed(atom_positions)):
            mytext[-i-1] = mytext[-i-1].strip()+' '+' '.join(map(str, r))+'\n'
        return mytext


    def _symlink_pseudopotentials(self):
        """ 
        symlinks pseudopotentials files from pp_path_list
        to data/ directory so socorro can find them
        """
        for pp in self.pp_path_list:
            pp_name = os.path.basename(pp)
            os.symlink(pp, 'data/'+pp_name)

    def read_energy(self, diaryf='diaryf'):
        """
        reads energy from socorro output file
        if total energy (cell energy) found, return as float
        otherwise, return None
    
        if socorro has run but didn't complete, cell energy won't be 
        printed at the end of diaryf and this will return None
        """
        with open(diaryf) as fin:
            for line in fin:
                if 'cell energy   ' in line:
                    return float(line.split()[3])
            return None


    def read_forces(self, diaryf='diaryf'):
        """
        reads forces from socorro output file
        """
        with open(diaryf) as fin:
            for line in fin:
                #if 'cell energy   ' in line:
                #    return float(line.split()[3])
                pass
            return None




def setup_file_structure():
    """
    create file structure for running dft code at given gcut, might
    just copy from template file structure??
    """
    pass



def write_energy_line():
    pass



def check_socorro_fail():
    '''
    check for non-convergence of socorro run by reading diaryf file

    previous opal would return 102s as objectives
    '''
    #     # If socorro didn't ouptut forces or energy, it didn't complete successfully
    # did_force=$(grep "Atomic force" diaryf)
    # if [[ $did_force == "" ]]; then
    #   echo fail >$2
    #   exit
    # fi
    pass


def write_data():
    pass


def is_converged(dft_runs):
    '''
    loop through dft runs and check that energy or forces or whatever
    else is converged
    '''
    pass


def calculate_final_reults():
    pass


def get_converged_forces():
    pass

def get_random_configurations():
    pass

def get_pp_path_list():
    pass
