from rdkit import Chem
import os
import shutil
import subprocess


def xtb_optimization(folder, sdf, xtb_path, logger):
    basename = os.path.basename(sdf)

    pwd = os.getcwd()

    os.chdir(folder)

    file_name = os.path.splitext(basename)[0]

    xtb_command = os.path.join(xtb_path, 'xtb')
    with open('{}_xtb_opt.log'.format(file_name), 'w') as out:
        print(xtb_command, '{}.sdf'.format(file_name))
        subprocess.call([xtb_command, '{}.sdf'.format(file_name), '-opt'],
                        stdout=out, stderr=out)
        shutil.move('xtbopt.sdf', '{}_opt.sdf'.format(file_name))
        os.remove('{}.sdf'.format(file_name))

    os.chdir(pwd)
    return '{}_opt.sdf'.format(file_name)

    os.chdir(pwd)
