from rdkit import Chem
import os
import shutil
import subprocess

import numpy as np

from .g16_log import XtbLog


def xtb_optimization(folder, sdf, xtb_path, logger, timeout=600):
    basename = os.path.basename(sdf)
    file_name = os.path.splitext(basename)[0]

    if os.path.isfile(os.path.join(folder, '{}_freq.log')):
        return '{}_opt.sdf'.format(file_name)

    pwd = os.getcwd()
    os.chdir(folder)
    try:
        xtb_command = os.path.join(xtb_path, 'xtb')
        with open('{}_xtb_opt.log'.format(file_name), 'w') as out:
            print(xtb_command, '{}.sdf'.format(file_name))
            subprocess.call('{} {}_opt.sdf -opt'.format(xtb_command, file_name),
                            stdout=out, stderr=out, timeout=timeout)
            shutil.move('xtbopt.sdf', '{}_opt.sdf'.format(file_name))
            os.remove('{}.sdf'.format(file_name))

        with open(file_name + '_freq.log', 'w') as out:
            subprocess.run('{} {}_opt.sdf -ohess'.format(xtb_command, file_name), stdout=out,
                           stderr=out, timeout=timeout)

            os.remove('hessian')
            os.remove('vibspectrum')

        log = XtbLog('{}_freq.log'.format(file_name))
    except:
        pass
 
    os.chdir(pwd)
    if log.termination:
        peaks = log.wavenum
        if np.min(peaks) < 0:
            raise RuntimeError('imaginary frequency found for {}'.format(file_name))
        else:
            return '{}_opt.sdf'.format(file_name)
    else:
        raise RuntimeError('xtb optimization did not finish for {}'.format(file_name))
