import numpy as np
import os
import sys
import subprocess
import calc_accuracy


class SocorroFail(Exception):
    """raised if socorro run failed with given inputs"""

class NoCutoffConvergence(Exception):
    """raised if results don't converge with respect to cutoff"""


def main(element_list, gcuts, energy_tol):
    #def main(element_list):
    """
    INPUTS
        element_list: example are ['Si', 'Ge'] or ['N']
        gcuts: list of gcuts to run to tet for energy convergence
        energy_tol: energy at which

    ATTRIBUTES
        all_energy: energy at every configuration for each gcut.
            all_energy[i][j] is the energy for the ith gcut and jth config
        all_forces: forces at every configuration for each gcut.
            all_energy[i][j][k, m] is the force for the ith gcut, jth 
            config, kth atom, and m=0,1,2 for x,y,z direction
    
    RETURNS:
        objectives: 
    """
    run_dir = os.getcwd()

    # these are the same for different optimizations
    argvf_template_path = os.path.join(run_dir, 'argvf.template')
    crystal_template_path = os.path.join(run_dir, 'crystal.template')

    # these will change for different optimizations
    pp_path_list = [os.path.join(run_dir, 'PAW.'+elem) for elem in element_list]
    positions_to_run = get_random_configurations('../configurations.in') # read random configs from file
    print positions_to_run

    # increase gcut until converged
    # these all_ lists are needed for convergence checks
    all_energy = [] # will store all energies for each gcut
    all_forces = [] # will store all energies for each gcut
    for gcut in gcuts:
        # make and move to gcut directory
        gcut_dir_name = 'gcut_dir.' + str(int(gcut))
        os.mkdir(gcut_dir_name)
        os.chdir(gcut_dir_name)
        
        # return energies, forces

        # create DftRun object for each atomic structure
        position_dft_runs = []
        for pos in positions_to_run:
            pos_reshaped = pos.reshape([-1,3])  # reshape to one row per atom
            position_dft_runs.append(DftRun(pp_path_list, argvf_template_path,
                                            crystal_template_path, pos_reshaped, gcut))
        
        # run socorro at positions in parallel
        position_sweep(position_dft_runs)

        # extract relevant results from socorro outputs
        try:
            dft_results = get_dft_results_at_gcut(position_dft_runs) 
            print dft_results
        except SocorroFail:
            raise

        # append this gcuts results to list
        all_energy.append(dft_results['energies'])
        all_forces.append(dft_results['forces'])
        os.chdir(run_dir)

        # If results are converged with respect to gcut,
        # write results and exit.
        if is_converged(all_energy, energy_tol):
            print "Converged at gcut = ", gcut
            accu = calc_accuracy.calc_accuracy_objective(dft_results['forces'], 
                                                         os.path.join(run_dir, '..', 'allelectron_forces.dat'))
            work = calc_work_objective(position_dft_runs, os.path.join(run_dir, '..'))
            return {'accu': accu, 'work': work}
    else:
        raise NoCutoffConvergence  # if no gcut convergence



class DftRun:
    """
    class for setting up, running, and post processing soccoro dft
    calculation 

    inputs
    pp_path_list: paths to every pseudopotential needed for run.
     Assumes pseudopotential files already be named PAW.{elementsymbol}
    argvf_template_path: path to argvf template file
    crystal_template_path: path to crystal template file
    atom_positions: Nx3 array of atomic positions where N is number of atoms
    gcut: wf energy cutoff for dft calculation

    important attributes
    pp_path_list: see inputs (pp_path_list)
    argvf_template_path: see inputs
    crystal_template_path: see inputs
    atom_positions: see inputs
    gcut: see inputs
    run_dir: dir where files are setup (and where socorro should be run
        and where results will be)
    _are_files_setup: True if setup_files() run success, False otherwise

    public methods
    setup_files: sets up files for socorro dft run in current directory
     (argvf and crystal)
    run_socorro: system calls socorro in current directory, only works
     if _are_files_setup is True
    """
    def __init__(self, pp_path_list, argvf_template_path,
                 crystal_template_path, atom_positions, gcut):
        self.pp_path_list = pp_path_list
        self.atom_positions = atom_positions
        self.gcut = float(gcut)
        self.argvf_template_path = argvf_template_path
        self.crystal_template_path = crystal_template_path
        self._are_files_setup = False
        self.run_dir = None

    def run_socorro(self, logfile):
        """
        runs socorro in a subprocess, reurns process ID, and continues

        if files haven't been set up:
            return False after printing warning
        if socorro runs and finishes successfully:
            return process ID from Popen

        log_file: file handle for logging soccoro stdout/err output
        """
        if self._are_files_setup is False:
            # wnat exit so jobs don't keep running
            print 'Files not setup yet. Must run setup_files() first'
            return False
        else:
            p = subprocess.Popen('socorro', stdout=logfile, stderr=logfile)
            return p # return process id for wait later
   
    def setup_files(self):
        """
        write dft input files from templates 

        note this will probably fail if argvf, data/, or data/crystal
        already exist. This may be desirable behavior but if not I can
        change it.
        """
        self._make_argvf()
        os.mkdir('data')
        self._make_crystal()
        self._symlink_pseudopotentials()
        self._are_files_setup = True
        self.run_dir = os.getcwd()

    def _make_argvf(self):
        """ writes preprocessed argvf text to argvf file """
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
        """
        Some socorro builds want the crystal file in data/
        and some want it in the run directory.
        """
        # read in text from template file
        with open(self.crystal_template_path) as fin:
            crystal_template_text = fin.readlines()
        preprocessed_text = self._preproc_crystal(crystal_template_text,
                                                  self.atom_positions)
        # write preprocessed text to data/crystal
        with open('data/crystal', 'w') as fout:
            fout.writelines(preprocessed_text)
        os.symlink('data/crystal', 'crystal')
 
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
        
        Some socorro builds want the pseudopotential in data/
        and some want it in the run directory.
        """
        for pp in self.pp_path_list:
            pp_name = os.path.basename(pp)
            os.symlink(pp, pp_name)
            os.symlink(pp, 'data/'+pp_name)

    def read_energy(self, diaryf='diaryf'):
        """
        reads energy from socorro output file
        if total energy (cell energy) found, return as float
        otherwise, return None
    
        if socorro has run but didn't complete, cell energy won't be 
        printed at the end of diaryf and this will return None
        
        This could fail if the socorro run ouputs multiple cell
        energies, as it does for structure relaxations.
        """
        with open(diaryf) as fin:
            for line in fin:
                if 'cell energy   ' in line:
                    return float(line.split()[3])
            return None


    def read_forces(self, diaryf='diaryf'):
        """
        reads forces from socorro output file
    
        returns forces as 1 by 3N numpy array where N is the number of atoms
        """
        forces = np.array([]) # blank np array
        with open(diaryf) as fin:
            for line in fin:
                if 'Atomic forces:' in line:
                    # skip two lines then continue through file
                    fin.next()
                    fin.next()
                    for line in fin:
                        if line.strip() == '':
                            break # break when blank line after forces reached
                        f = map(float, line.split()[1:4])
                        forces = np.append(forces, f) # append to forces array
                    return forces
            return None



def position_sweep(dft_runs):
    """
    run several instances of socorro on different threads using
    different positions
    
    when all socorro runs are done, returns dft_run objects

    main_ variables are defined globally or in the calling function

    still untested
    """
    pos_sweep_dir = os.getcwd()
    print 'Calling Dakota position sweep in ' + pos_sweep_dir

    # for each dft run, set up files and start socorro subprocess
    processes = []
    for i,dft_run in enumerate(dft_runs):
        this_dir = 'workdir_r.'+str(i+1)
        os.mkdir(this_dir)
        os.chdir(this_dir)

        dft_run.setup_files()
        with open('socorro.log', 'w') as fout:
            p = dft_run.run_socorro(fout)
        processes.append(p) # add p to process list
        
        os.chdir(pos_sweep_dir)
    
    # wait for each process to finish
    for process in processes:
        process.wait()



def is_converged(energies_so_far, tol):
    """
    Check if energies for latest gcut have changed by less than tol.

    energies_so_far: list of lists of energies, for all gcuts so far
    tol: absolute energy tolerance
    
    returns True if abs(E[-1]-E[-2])<tol for all configurations, 
    and False otherwise.

    There are several possibilites for specifying convergence. If I
    change my mind about how I want to handle convergence (perhaps test
    forces instead of energy, or change to realtive tolerance), I can 
    replace this function. For previous work i use energy residuals
    as a convergence criterion so I'll write it that way for now.
    """
    if len(energies_so_far) == 1:
        # can't be converged if only one gcut has run
        return False
    
    # check all energy residuals less than tolerance
    energies_latest = energies_so_far[-1] 
    energies_previous = energies_so_far[-2]
    return np.isclose(energies_latest, energies_previous, atol=tol, rtol=0).all()


def get_random_configurations(filename):
    """ 
    Read random atomic configurations from file.

    Configurations should be formatted one random configuration per 
    line, where each group of three coordinates is one atom. 
    """
    return np.genfromtxt(filename, comments='#') 



def get_dft_results_at_gcut(position_dft_runs): 
    """
    returns eneriges and forces for every dft run at this gcut
    
    energy_list: energy at each position run
    forces_list: forces at each position run

    Raises SocorroFail exception if any of the socorro 
    output files did not contain energy or forces, indicating
    socorro did not complete at that position.
    """
    # get energy and force results from each socorro run
    energy_list = []
    forces_list = []
    for dft_run in position_dft_runs:
        # if a run did not finish, dft_run.read_*() will return None
        diaryf_path = os.path.join(dft_run.run_dir, 'diaryf')
        energy_list.append( dft_run.read_energy(diaryf=diaryf_path) )
        forces_list.append( dft_run.read_forces(diaryf=diaryf_path) )

    if None in energy_list or None in forces_list:
        raise SocorroFail

    return {'energies': energy_list, 'forces': forces_list}



def calc_work_objective(position_dft_runs, calc_nflops_dir=None):
    """ 
    I'm using an old bash script from Alan T. and Rachael H. so I'm just
    going to subprocess it.
        
    the work objective is equal to the sum of the estimated number of floating 
    point operations for all socorro runs (there is one socorro run per atomic 
    configuration).
    """
    start_dir = os.getcwd()
    if calc_nflops_dir is None:
        calc_nflops_dir = os.getcwd()
    calc_nflops = os.path.join(calc_nflops_dir, 'calc_nflops')

    work_objective = 0.
    for run in position_dft_runs:
        os.chdir(run.run_dir)
        nflops_data = subprocess.check_output([calc_nflops])
        work_objective += float(nflops_data.split()[-1])
    return work_objective 


