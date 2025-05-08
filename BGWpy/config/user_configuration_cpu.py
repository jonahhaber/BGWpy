"""
The user is advised to set the default behavior
of the module to their needs.

IMPORTANT:
Within this directory, copy this file as follow:
    cp  user_configuration.py.template  user_configuration.py

Then, edit the file user_configuration.py as desired.
This should be done before installing the module with the setup script.
"""

# MPI parameters
# Some mpi runners specify the number of processors and number of proc. per node,
# while other specify the number of nodes and the number of proc. per node.
# To disable a feature, set the value or the flag to None.
# Note that these parameters can always be used
# as keyword arguments for the various tasks and workflows.
default_mpi = dict(
    mpirun = 'mpirun',
    nproc = 1,
    nproc_flag = '-n',
    nproc_per_node = 1,
    nproc_per_node_flag = '--npernode',
    nodes = None,
    nodes_flag = None,
    )


# BGWpy generate several bash script, essentially to run BerkeleyGW.
default_runscript = dict(
    first_line = '#!/bin/bash', # The first line appearing in run scripts.
                                # Do not use any other shell than bash.

    #header = [],
    header = ['#SBATCH -N 1',
              '#SBATCH -C cpu',
              '#SBATCH -q debug',
              '#SBATCH -t 00:30:00',
              '#SBATCH -A m2651',
              '',
              '#OpenMP settings:',
              'export OMP_NUM_THREADS=1',
              'export OMP_PLACES=threads',
              'export OMP_PROC_BIND=spread',
              '',
              'module load espresso',
              'module load berkeleygw/3.0.1-cpu',
              ],

    footer = [],                # Lines that appear at the end of the scripts.
    )


# BerkeleyGW can be compiled with or without HDF5 io.
# Set this flag accordingly.
use_hdf5 = True
use_hdf5_qe = True

# BerkeleyGW can be compiled in complex or real flavor.
# Set this flag accordingly.
flavor_complex = True

# Choice of dft code ('espresso', 'abinit')
# for the premade workflows.
dft_flavor = 'espresso'

