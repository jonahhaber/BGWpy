"""Workflow to perform BSE calculation."""

import numpy as np
from os.path import join as pjoin

from ..core import Workflow
from ..BGW import  KernelTask, AbsorptionTask

__all__ = ['BSEQGridFlow']

class BSEQGridFlow(Workflow):
    def __init__(self, bse_flow, **kwargs):
        super(BSEQGridFlow, self).__init__(**kwargs)

        # link files
        kwargs.update(
            charge_density_fname = bse_flow.scftask.charge_density_fname,
            data_file_fname = bse_flow.scftask.data_file_fname,
            wfn_co_fname = bse_flow.wfntask_ush.wfn_fname,
            wfn_fi_fname = bse_flow.wfntask_fi_ush.wfn_fname,
            eps0mat_fname = bse_flow.epsilontask.eps0mat_fname,
            epsmat_fname = bse_flow.epsilontask.epsmat_fname,
            eqp_fname = bse_flow.sigmatask.eqp1_fname,
            eqp_q_fname = bse_flow.sigmatask.eqp1_fname
        )

        # Q-points
        self.Qpoints = list()
        self.ngQpt = kwargs.pop('ngQpt')
        delta_Qx = 1.0 / self.ngQpt[0]
        delta_Qy = 1.0 / self.ngQpt[1]
        delta_Qz = 1.0 / self.ngQpt[2]
        for ikx in range(self.ngQpt[0]):
            for iky in range(self.ngQpt[1]):
                for ikz in range(self.ngQpt[2]):
                    self.Qpoints.append([ikx * delta_Qx, iky * delta_Qy, ikz * delta_Qz])

        self.ngkpt = kwargs.pop('ngkpt')
        self.ngkpt_fi = kwargs.pop('ngkpt_fine')
        self.nc = kwargs['nbnd_cond']
        self.nv = kwargs['nbnd_val']
        self.nc_co = kwargs['nbnd_cond_co']
        self.nv_co = kwargs['nbnd_val_co']
        self.nc_fi = kwargs['nbnd_cond_fi']
        self.nv_fi = kwargs['nbnd_val_fi']
        self.absorption_extra_lines = kwargs.pop('absorption_extra_lines', [])

        self.wfn_co_fname = kwargs['wfn_co_fname']
        self.wfn_fi_fname = kwargs['wfn_fi_fname']

        # naming conventions for direcotries
        self.kernel_dirname = kwargs.pop('kernel_dirname', '03-xct-Qgrid/03-kernel')
        self.singlet_dirname = kwargs.pop('singlet_dirname', '03-xct-Qgrid/04-singlet')
        self.triplet_dirname = kwargs.pop('triplet_dirname', '03-xct-Qgrid/05-triplet')

        # kernel task
        self.kernel = Workflow(dirname=self.kernel_dirname)
        for iQ, Q in enumerate(self.Qpoints): 
            kernel_dir = 'Q{:04d}/k{:02d}_c{:02d}_v{:02d}'.format(iQ, self.ngkpt[0], self.nc, self.nv) 
            kernel_extra_lines = self.generate_kernel_extra_lines(Q) 
            kerneltask = KernelTask(
                dirname = pjoin(self.kernel.dirname, kernel_dir),
                wfnq_co_fname = self.wfn_co_fname,
                extra_lines = kernel_extra_lines,
                **kwargs)
            self.kernel.add_tasks([kerneltask], merge=False) 

        # kernel.write()
        # kernel.report() 
            
        # singlet task
        singlet = Workflow(dirname=self.singlet_dirname)
        for iQ, Q in enumerate(self.Qpoints):
            kernel_dir = 'Q{:04d}/k{:02d}_c{:02d}_v{:02d}'.format(iQ, self.ngkpt[0], self.nc, self.nv) 
            abs_dir = 'Q{:04d}/k{:02d}_c{:02d}_v{:02d}_k{:02d}_c{:02d}_v{:02d}'.format(iQ, self.ngkpt_fi[0], self.nc_fi, self.nv_fi, self.ngkpt[0], self.nc_co, self.nv_co)  
            absorption_extra_lines = self.generate_absorption_extra_lines(Q, spin='singlet')
            singlettask = AbsorptionTask(
                dirname = pjoin(singlet.dirname, abs_dir),
                wfnq_co_fname = self.wfn_co_fname,
                wfnq_fi_fname = self.wfn_fi_fname, 
                bsemat_fname = pjoin(self.kernel.dirname, kernel_dir, 'bsemat.h5'),
                extra_lines = absorption_extra_lines,
                **kwargs)
            
            singlet.add_tasks([singlettask], merge=False) 

        # singlet.write()
        # singlet.report() 


        # triplet task
        self.triplet = Workflow(dirname=self.triplet_dirname)
        for iQ, Q in enumerate(self.Qpoints):
            kernel_dir = 'Q{:04d}/k{:02d}_c{:02d}_v{:02d}'.format(iQ, self.ngkpt[0], self.nc, self.nv) 
            abs_dir = 'Q{:04d}/k{:02d}_c{:02d}_v{:02d}_k{:02d}_c{:02d}_v{:02d}'.format(iQ, self.ngkpt_fi[0], self.nc_fi, self.nv_fi, self.ngkpt[0], self.nc_co, self.nv_co)  
            absorption_extra_lines = self.generate_absorption_extra_lines(Q, spin='triplet')
            triplettask = AbsorptionTask(
                dirname = pjoin(self.triplet.dirname, abs_dir),
                wfnq_co_fname = self.wfn_co_fname,
                wfnq_fi_fname = self.wfn_fi_fname, 
                bsemat_fname = pjoin(self.kernel.dirname, kernel_dir, 'bsemat.h5'),
                extra_lines = absorption_extra_lines,
                **kwargs)
            
            self.triplet.add_tasks([triplettask], merge=False) 

        # triplet.write()
        # triplet.report() 



    @staticmethod
    def generate_kernel_extra_lines(Q):

        kernel_extra_lines = [
            'no_symmetries_coarse_grid',
            'screening_semiconductor',
            #'cell_slab_truncation',
            ]
        
        if np.linalg.norm(Q) > 1e-6:
            kernel_extra_lines.append('energy_loss') 
            kernel_extra_lines.append('exciton_Q_shift 0 {q[0]} {q[1]} {q[2]}'.format(q=Q)) 

        return kernel_extra_lines

    def generate_absorption_extra_lines(self,Q=None,spin=None):

        ecs = 2.85
        absorption_extra_lines = self.absorption_extra_lines +[
                'no_symmetries_coarse_grid',
                'no_symmetries_fine_grid',
                'no_symmetries_shifted_grid',
                'screening_semiconductor',
                'write_eigenvectors -1',
                'degeneracy_check_override',
                #'cell_slab_truncation',
                #'ecs {}'.format(ecs),
                ]
        
        if np.linalg.norm(Q) > 1e-6:
            absorption_extra_lines.append('use_velocity') 
            absorption_extra_lines.append('exciton_Q_shift 0 {q[0]} {q[1]} {q[2]}'.format(q=Q)) 
        else:
            absorption_extra_lines.append('use_momentum')

        if spin == 'triplet':
            absorption_extra_lines.append('spin_triplet')

        return absorption_extra_lines  
